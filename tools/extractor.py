"""Code extractor tool for organizing parsed code by type."""

from typing import Any
from pydantic import BaseModel

from tools.parser import ParsedCode, ClassInfo, FunctionInfo, EndpointInfo
from tools.type_detector import CodeType
from utils.helpers import setup_logging

logger = setup_logging()


class ExtractedSDK(BaseModel):
    """Extracted SDK information."""
    classes: list[dict[str, Any]]
    standalone_functions: list[dict[str, Any]] = []


class ExtractedFastAPI(BaseModel):
    """Extracted FastAPI information."""
    endpoints: list[dict[str, Any]]
    pydantic_models: list[dict[str, Any]] = []
    dependencies: list[str] = []


class ExtractedGeneral(BaseModel):
    """Extracted general Python information."""
    functions: list[dict[str, Any]]
    classes: list[dict[str, Any]] = []


class CodeExtractor:
    """Extract and organize code information based on type."""
    
    def extract(self, parsed: ParsedCode, code_type: CodeType) -> dict[str, Any]:
        """Extract code information based on detected type."""
        if code_type == CodeType.SDK:
            return self._extract_sdk(parsed)
        elif code_type == CodeType.FASTAPI:
            return self._extract_fastapi(parsed)
        else:
            return self._extract_general(parsed)
    
    def _extract_sdk(self, parsed: ParsedCode) -> dict[str, Any]:
        """Extract SDK-style class information."""
        classes = []
        
        for cls in parsed.classes:
            class_data = {
                "name": cls.name,
                "docstring": cls.docstring or "Not specified",
                "bases": cls.bases if cls.bases else ["Not specified"],
                "decorators": cls.decorators if cls.decorators else [],
                "methods": []
            }
            
            for method in cls.methods:
                method_data = {
                    "name": method.name,
                    "docstring": method.docstring or "Not specified",
                    "is_async": method.is_async,
                    "decorators": method.decorators,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.annotation or "Not specified",
                            "default": p.default or "Required" if p.is_required else p.default,
                            "required": p.is_required
                        }
                        for p in method.parameters
                    ],
                    "return_type": method.return_annotation or "Not specified"
                }
                class_data["methods"].append(method_data)
            
            classes.append(class_data)
        
        # Include standalone functions
        standalone_functions = [
            self._function_to_dict(f) for f in parsed.functions
        ]
        
        result = ExtractedSDK(
            classes=classes,
            standalone_functions=standalone_functions
        )
        
        logger.info(f"Extracted SDK: {len(classes)} classes, {len(standalone_functions)} functions")
        return result.model_dump()
    
    def _extract_fastapi(self, parsed: ParsedCode) -> dict[str, Any]:
        """Extract FastAPI endpoint information."""
        endpoints = []
        
        for endpoint in parsed.endpoints:
            endpoint_data = {
                "path": endpoint.path,
                "method": endpoint.http_method,
                "function_name": endpoint.function_name,
                "docstring": endpoint.docstring or "Not specified",
                "is_async": endpoint.is_async,
                "response_model": endpoint.response_model or "Not specified",
                "parameters": self._categorize_parameters(endpoint.parameters),
                "return_type": endpoint.return_annotation or "Not specified"
            }
            endpoints.append(endpoint_data)
        
        # Extract Pydantic models (classes that might be used as request/response)
        pydantic_models = []
        for cls in parsed.classes:
            if any("BaseModel" in base or "pydantic" in base.lower() for base in cls.bases):
                pydantic_models.append({
                    "name": cls.name,
                    "fields": cls.class_variables,
                    "docstring": cls.docstring or "Not specified"
                })
        
        result = ExtractedFastAPI(
            endpoints=endpoints,
            pydantic_models=pydantic_models
        )
        
        logger.info(f"Extracted FastAPI: {len(endpoints)} endpoints, {len(pydantic_models)} models")
        return result.model_dump()
    
    def _extract_general(self, parsed: ParsedCode) -> dict[str, Any]:
        """Extract general Python function information."""
        functions = [self._function_to_dict(f) for f in parsed.functions]
        classes = []
        
        for cls in parsed.classes:
            class_data = {
                "name": cls.name,
                "docstring": cls.docstring or "Not specified",
                "methods": [self._function_to_dict_simple(m) for m in cls.methods]
            }
            classes.append(class_data)
        
        result = ExtractedGeneral(
            functions=functions,
            classes=classes
        )
        
        logger.info(f"Extracted General: {len(functions)} functions, {len(classes)} classes")
        return result.model_dump()
    
    def _function_to_dict(self, func: FunctionInfo) -> dict[str, Any]:
        """Convert FunctionInfo to dictionary."""
        return {
            "name": func.name,
            "docstring": func.docstring or "Not specified",
            "is_async": func.is_async,
            "decorators": func.decorators,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.annotation or "Not specified",
                    "default": p.default if p.default else ("Required" if p.is_required else "None"),
                    "required": p.is_required
                }
                for p in func.parameters
            ],
            "return_type": func.return_annotation or "Not specified"
        }
    
    def _function_to_dict_simple(self, func: FunctionInfo) -> dict[str, Any]:
        """Simplified function dict for nested display."""
        return {
            "name": func.name,
            "parameters": [p.name for p in func.parameters],
            "return_type": func.return_annotation or "Not specified"
        }
    
    def _categorize_parameters(self, parameters: list) -> dict[str, list]:
        """Categorize FastAPI parameters by type."""
        categorized = {
            "path": [],
            "query": [],
            "body": [],
            "header": [],
            "cookie": []
        }
        
        for param in parameters:
            param_dict = {
                "name": param.name,
                "type": param.annotation or "Not specified",
                "default": param.default if param.default else ("Required" if param.is_required else "None"),
                "required": param.is_required
            }
            
            # Determine category based on annotation/default
            annotation = param.annotation or ""
            default = param.default or ""
            
            if "Path" in annotation or "Path" in default:
                categorized["path"].append(param_dict)
            elif "Body" in annotation or "Body" in default:
                categorized["body"].append(param_dict)
            elif "Header" in annotation or "Header" in default:
                categorized["header"].append(param_dict)
            elif "Cookie" in annotation or "Cookie" in default:
                categorized["cookie"].append(param_dict)
            else:
                # Default to query for simple parameters
                categorized["query"].append(param_dict)
        
        return categorized
