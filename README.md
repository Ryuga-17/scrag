<div align="center">

![Forktober GIF](https://raw.githubusercontent.com/ACM-VIT/.github/master/profile/acm_gif_banner.gif)

<!-- Project Title -->
<h2>Scrag</h2>

<p>Adaptive, multi‑strategy web scraper that extracts clean text and metadata for RAG pipelines and local LLM workflows.</p>

<p>
  <a href="https://acmvit.in/" target="_blank">
    <img alt="made-by-acm" src="https://img.shields.io/badge/MADE%20BY-ACM%20VIT-orange?style=flat-square&logo=acm&link=acmvit.in" />
  </a>
  <img alt="license" src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" />
</p>

</div>

---

## Table of Contents
- [About](#about)
- [Features](#features)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Contributing](#contributing)
- [Hacktoberfest](#hacktoberfest)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Guidelines for Pull Request](#guidelines-for-pull-request)
- [Authors](#authors)

---

## About
This project proposes a robust web scraper designed for maximum adaptability. It automatically adjusts to various website structures by employing a multi‑strategy extraction approach. The scraper attempts to extract clean, structured text and metadata (including title, author, and date) using methods such as newspaper3k, readability‑lxml, and BeautifulSoup heuristics. In cases where these methods are insufficient, it can optionally fall back to headless browser rendering to capture content from more complex, dynamically loaded websites. The output is specifically formatted for integration into Retrieval‑Augmented Generation (RAG) pipelines or for use with local Large Language Models (LLMs).

An ambitious, optional extension to this project is the Universal RAG Builder. This layer would automatically identify and scrape top‑ranked websites relevant to a user's query, subsequently building a RAG index from the collected data. This feature addresses a key limitation of local LLMs, their inability to browse the internet by providing automated knowledge aggregation and up‑to‑date information retrieval without requiring manual data collection. The project's user interface will initially be a Command Line Interface (CLI), with plans for a web‑based version to cater to users who prefer a more visually appealing display.

---

## Features
- Multi‑strategy extraction: newspaper3k, readability‑lxml, and BeautifulSoup‑based heuristics.  
- Metadata capture: title, author, and date when available.  
- Optional headless rendering fallback for dynamic, JS‑heavy pages.  
- RAG‑ready output: clean, structured content suitable for chunking and indexing.  
- CLI first: simple commands to fetch and export content; web UI planned.  

---

## Project Structure

```
scrag/
├── src/scrag/                 # Main source code
│   ├── extractors/           # Content extraction strategies
│   ├── processors/           # Text processing and cleaning
│   ├── storage/              # Storage backends and adapters
│   ├── rag/                  # RAG pipeline components
│   ├── cli/                  # Command-line interface
│   ├── web/                  # Web interface (planned)
│   └── utils/                # Utility functions
├── tests/                    # Comprehensive test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── performance/          # Performance benchmarks
│   └── fixtures/             # Test data and mocks
├── docs/                     # Documentation
│   ├── api/                  # API reference
│   ├── guides/               # User guides
│   └── tutorials/            # Step-by-step tutorials
├── config/                   # Configuration files
│   ├── extractors/           # Extractor configurations
│   └── rag/                  # RAG pipeline configurations
├── deployment/               # Deployment configurations
│   ├── docker/               # Docker configurations
│   ├── kubernetes/           # Kubernetes manifests
│   └── aws/                  # AWS deployment files
├── scripts/                  # Development and build scripts
└── ARCHITECTURE.md           # Detailed architecture documentation
```

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Roadmap
- Universal RAG Builder: auto‑discover top results for a query, scrape them, and build a ready‑to‑use RAG index.  
- Web UI: a lightweight interface for users who prefer a visual workflow.  
- Export adapters: convenient formats for popular vector DBs and RAG frameworks.  

---

## Quick Start

```bash
# 1) Fork and clone
# Click Fork on GitHub, then:
 git clone https://github.com/ACM-VIT/scrag.git
 cd scrag

# 2) Create a branch
 git checkout -b feat/your-feature

# 3) Install dependencies
 uv sync
 uv pip install -e src/scrag

# 4) Run the project
 uv run python -m core.cli info
```

---

## Usage
Provide examples and code snippets showing how to use the project. Add screenshots or GIFs if applicable.

```console
# examples
<your-cli> init
<your-cli> run
```

---

## Contributing
We welcome contributions of all kinds! Please read our [Contributing Guidelines](contributing.md) to get started quickly and make your PRs count.

---

## Hacktoberfest

<p>
   <a href="https://hacktoberfest.com/" target="_blank">
      <img alt="Hacktoberfest" src="https://img.shields.io/badge/Hacktoberfest-2025-indigo?style=flat-square" />
   </a>
</p>

Join us for Hacktoberfest! Quality > quantity.
- Aim for meaningful, well‑scoped PR/MRs that solve real issues.
- Non‑code contributions (docs, design, tutorials) are welcome via PR.
- Full participation details: https://hacktoberfest.com/participation

---

## Submitting a Pull Request

1. Fork the repository (top‑right on GitHub)
2. Clone your fork locally:
   ```bash
   git clone <HTTPS-ADDRESS>
   cd <NAME-OF-REPO>
   ```
3. Create a new branch:
   ```bash
   git checkout -b <your-branch-name>
   ```
4. Make your changes and stage them:
   ```bash
   git add .
   ```
5. Commit your changes:
   ```bash
   git commit -m "feat: your message"
   ```
6. Push to your fork:
   ```bash
   git push origin <your-branch-name>
   ```
7. Open a Pull Request and clearly describe what you changed and why. Link related issues (e.g., “Fixes #123”).

<!-- <img src="https://img.shields.io/github/:variant/:user/:repo?style=flat-square&labelColor=orange" alt="Open a Pull Request" /> -->

---

## Guidelines for Pull Request
- Avoid PRs that are automated/scripted or plagiarized from someone else’s work.
- Don’t spam; keep each PR focused and meaningful.
- The project maintainer’s decision on PR validity is final.
- For more, see our [Contributing Guidelines](contributing.md) and the Hacktoberfest [participation rules](https://hacktoberfest.com/participation).

---

## Authors

**Authors:** <!-- [author1's name](link), [author2's name](link) -->  
**Contributors:** <!-- Generate contributors list using https://contributors-img.web.app/preview -->

---

## Community & Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

<div align="center">
  
Made with ❤️ by <a href="https://acmvit.in/" target="_blank">ACM‑VIT</a>

![Footer GIF](https://raw.githubusercontent.com/ACM-VIT/.github/master/profile/domains.gif)

</div>
