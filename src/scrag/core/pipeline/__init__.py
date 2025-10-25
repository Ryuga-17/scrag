"""Pipeline stage interface and base implementations."""

from .stages import PipelineStage, StageContext, StageResult

__all__ = [
    "PipelineStage",
    "StageContext", 
    "StageResult",
]