"""Chunkformer ASR package.

This package contains the Chunkformer model implementation and its
utilities. It intentionally avoids side‑effect imports to prevent
import‑time circular dependencies when higher‑level modules import
from `service_asr.model.chunkformer`.
"""

# Explicitly export nothing by default; callers should import the
# specific submodules they need (e.g., `asr_model`, `utils`, etc.).
__all__: list[str] = []
