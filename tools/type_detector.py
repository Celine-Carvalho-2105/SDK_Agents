"""Tool for detecting the type of Python code."""

import ast
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from utils.helpers import setup_logging

logger = setup_logging()


class CodeType(str, Enum):
    SDK = "sdk"
    FASTAPI = "fastapi"
    GENERAL_PYTHON = "general_python"


class DetectionResult(BaseModel):
    """Result of code type detection."""
    code_type: CodeType
    confidence: float
    indicators: list[str]


class CodeTypeDetector:
    """Detects whether Python code is SDK, FastAPI, or general Python."""
    
    FASTAPI_PATTERNS = [
        r'from\s+fastapi\s+import',
        r'import\s+fastapi',
        r'FastAPI\s*\(',
        r'@app\.(get|post|put|delete|patch|options|head)',
        r'@router\.(get|post|put|delete|patch|options|head)',
        r'APIRouter\s*\(',
    ]
    
    SDK_INDICATORS = [
        'class',
        '__init__',
        'self',
        'property',
        'classmethod',
        'staticmethod',
    ]
    
    def detect(self, code: str) -> DetectionResult:
        """Detect the type of Python code."""
        indicators = []
        
        # Check for FastAPI first (most specific)
        fastapi_score = self._check_fastapi(code)
        if fastapi_score > 0:
            indicators.append("FastAPI imports/decorators detected")
            return DetectionResult(
                code_type=CodeType.FASTAPI,
                confidence=min(1.0, fastapi_score * 0.3),
                indicators=indicators
            )
        
        # Check for SDK/class-based code
        sdk_score = self._check_sdk(code)
        if sdk_score >= 2:
            indicators.append("Class definitions with methods detected")
            return DetectionResult(
                code_type=CodeType.SDK,
                confidence=min(1.0, sdk_score * 0.2),
                indicators=indicators
            )
        
        # Default to general Python
        indicators.append("General Python functions/scripts")
        return DetectionResult(
            code_type=CodeType.GENERAL_PYTHON,
            confidence=0.8,
            indicators=indicators
        )
    
    def _check_fastapi(self, code: str) -> int:
        """Count FastAPI indicators in code."""
        score = 0
        for pattern in self.FASTAPI_PATTERNS:
            if re.search(pattern, code):
                score += 1
        return score
    
    def _check_sdk(self, code: str) -> int:
        """Count SDK/class indicators in code."""
        score = 0
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    score += 2
                    # Check for methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            score += 1
        except SyntaxError:
            # Fall back to simple pattern matching
            if 'class ' in code:
                score += 1
            if 'def __init__' in code:
                score += 1
        
        return score
