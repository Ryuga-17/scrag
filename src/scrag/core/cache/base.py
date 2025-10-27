"""HTTP caching support for improved performance on repeated runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests


@dataclass
class CacheEntry:
    """Represents a cached HTTP response."""

    url: str
    content: str
    status_code: int
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    cached_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None


class CacheStore:
    """On-disk cache store for HTTP responses."""

    def __init__(
        self,
        cache_dir: Path,
        *,
        default_ttl: int = 3600,
        max_size: int = 100 * 1024 * 1024,  # 100MB
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.index_file = self.cache_dir / "cache_index.json"
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load the cache index from disk."""
        if self.index_file.exists():
            try:
                self._index = json.loads(self.index_file.read_text(encoding="utf8"))
            except (json.JSONDecodeError, IOError):
                self._index = {}

    def _save_index(self) -> None:
        """Save the cache index to disk."""
        try:
            self.index_file.write_text(json.dumps(self._index, indent=2), encoding="utf8")
        except IOError:
            pass  # Best effort

    def _get_cache_key(self, url: str, headers: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key for the URL and headers."""
        key_data = f"{url}:{json.dumps(headers or {}, sort_keys=True)}"
        return hashlib.sha256(key_data.encode("utf8")).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the cache file path for a given key."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, url: str, headers: Optional[Dict[str, Any]] = None) -> Optional[CacheEntry]:
        """Retrieve a cached entry if valid."""
        cache_key = self._get_cache_key(url, headers)
        
        if cache_key not in self._index:
            return None
        
        cache_info = self._index[cache_key]
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            # Cache file missing, remove from index
            del self._index[cache_key]
            self._save_index()
            return None
        
        try:
            entry = json.loads(cache_path.read_text(encoding="utf8"))
            
            # Check if expired
            if entry.get("expires_at"):
                expires = datetime.fromisoformat(entry["expires_at"])
                if datetime.utcnow() > expires:
                    self.invalidate(url, headers)
                    return None
            
            return CacheEntry(**entry)
        except (json.JSONDecodeError, IOError, KeyError):
            # Corrupted cache entry
            self.invalidate(url, headers)
            return None

    def set(self, entry: CacheEntry) -> None:
        """Store a cache entry."""
        cache_key = self._get_cache_key(entry.url)
        cache_path = self._get_cache_path(cache_key)
        
        # Calculate expiration
        expires_at = None
        if entry.expires_at:
            expires_at = entry.expires_at
        else:
            expires_at = (datetime.utcnow() + timedelta(seconds=self.default_ttl)).isoformat()
        
        entry_dict = {
            "url": entry.url,
            "content": entry.content,
            "status_code": entry.status_code,
            "etag": entry.etag,
            "last_modified": entry.last_modified,
            "headers": entry.headers,
            "cached_at": entry.cached_at,
            "expires_at": expires_at,
        }
        
        try:
            cache_path.write_text(json.dumps(entry_dict, indent=2), encoding="utf8")
            self._index[cache_key] = {
                "url": entry.url,
                "cached_at": entry.cached_at,
                "expires_at": expires_at,
                "size": len(entry.content.encode("utf8")),
            }
            self._save_index()
        except IOError:
            pass  # Best effort

    def invalidate(self, url: str, headers: Optional[Dict[str, Any]] = None) -> None:
        """Remove a cache entry."""
        cache_key = self._get_cache_key(url, headers)
        
        if cache_key in self._index:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                try:
                    cache_path.unlink()
                except IOError:
                    pass
            del self._index[cache_key]
            self._save_index()

    def clear(self) -> None:
        """Clear all cached entries."""
        for cache_key in list(self._index.keys()):
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                try:
                    cache_path.unlink()
                except IOError:
                    pass
        self._index.clear()
        self._save_index()

    def size(self) -> int:
        """Get total cache size in bytes."""
        return sum(entry.get("size", 0) for entry in self._index.values())


class CacheableHTTPClient:
    """HTTP client with caching support."""

    def __init__(
        self,
        cache_store: Optional[CacheStore] = None,
        user_agent: Optional[str] = None,
        timeout: int = 10,
    ):
        self.cache_store = cache_store
        self.user_agent = user_agent or "ScragBot/0.1"
        self.timeout = timeout

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        *,
        use_cache: bool = True,
    ) -> tuple[Optional[str], Optional[int], Dict[str, Any]]:
        """
        Fetch a URL with caching support.
        
        Returns:
            Tuple of (content, status_code, headers)
        """
        if not use_cache or not self.cache_store:
            return self._fetch_fresh(url, headers)
        
        # Try to get from cache
        cached_entry = self.cache_store.get(url, headers)
        
        if cached_entry:
            # Prepare conditional request headers
            request_headers = headers or {}
            request_headers["User-Agent"] = self.user_agent
            request_headers["If-None-Match"] = cached_entry.etag or ""
            request_headers["If-Modified-Since"] = cached_entry.last_modified or ""
            
            try:
                response = requests.get(url, headers=request_headers, timeout=self.timeout)
                
                if response.status_code == 304:  # Not Modified
                    # Use cached content
                    return cached_entry.content, cached_entry.status_code, cached_entry.headers
                elif response.status_code == 200:
                    # Content changed, update cache
                    content = response.text
                    new_entry = CacheEntry(
                        url=url,
                        content=content,
                        status_code=response.status_code,
                        etag=response.headers.get("ETag"),
                        last_modified=response.headers.get("Last-Modified"),
                        headers=dict(response.headers),
                    )
                    self.cache_store.set(new_entry)
                    return content, response.status_code, dict(response.headers)
                else:
                    # Error response, return as-is
                    return response.text, response.status_code, dict(response.headers)
            except requests.RequestException:
                # Network error, use cached content
                return cached_entry.content, cached_entry.status_code, cached_entry.headers
        
        # No cache, fetch fresh
        return self._fetch_fresh(url, headers)

    def _fetch_fresh(self, url: str, headers: Optional[Dict[str, Any]] = None) -> tuple[Optional[str], Optional[int], Dict[str, Any]]:
        """Fetch a fresh copy without checking cache."""
        request_headers = headers or {}
        request_headers["User-Agent"] = self.user_agent
        
        try:
            response = requests.get(url, headers=request_headers, timeout=self.timeout)
            response.raise_for_status()
            
            content = response.text
            status_code = response.status_code
            
            # Store in cache if available
            if self.cache_store:
                entry = CacheEntry(
                    url=url,
                    content=content,
                    status_code=status_code,
                    etag=response.headers.get("ETag"),
                    last_modified=response.headers.get("Last-Modified"),
                    headers=dict(response.headers),
                )
                self.cache_store.set(entry)
            
            return content, status_code, dict(response.headers)
        except requests.RequestException as error:
            return None, None, {"error": str(error)}
