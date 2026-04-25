"""Utility functions for the documentation generator."""

import logging
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Any


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger("doc_generator")
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def sanitize_output(text: str) -> str:
    """Clean and sanitize generated text output."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()


def create_output_dir(base_path: str = "output") -> Path:
    """Create output directory with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(base_path) / timestamp
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def chunk_code(code: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Split code into overlapping chunks for embedding."""
    if len(code) <= chunk_size:
        return [code]
    
    chunks = []
    start = 0
    while start < len(code):
        end = start + chunk_size
        chunk = code[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def format_parameter(name: str, annotation: str | None, default: Any | None) -> dict:
    """Format a parameter into a structured dictionary."""
    return {
        "name": name,
        "type": annotation if annotation else "Not specified",
        "default": repr(default) if default is not None else "Required",
        "required": default is None
    }
