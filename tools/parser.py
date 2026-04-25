"""AST-based code parser for extracting code structure."""

import ast
from typing import Any, Optional
from pydantic import BaseModel

from utils.helpers import setup_logging

logger = setup_logging()


class ParameterInfo(BaseModel):
    """Information about a function/method parameter."""
    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None
    is_required: bool = True


class FunctionInfo(BaseModel):
    """Information about a function or method."""
    name: str
    parameters: list[ParameterInfo]
    return_annotation: Optional[str] = None
    decorators: list[str] = []
    docstring: Optional[str] = None
    is_async: bool = False


class ClassInfo(BaseModel):
    """Information about a class."""
    name: str
    bases: list[str] = []
    methods: list[FunctionInfo] = []
    class_variables: list[str] = []
    docstring: Optional[str] = None
    decorators: list[str] = []


class EndpointInfo(BaseModel):
    """Information about a FastAPI endpoint."""
    path: str
    http_method: str
    function_name: str
    parameters: list[ParameterInfo]
    return_annotation: Optional[str] = None
    docstring: Optional[str] = None
    response_model: Optional[str] = None
    is_async: bool = False


class ParsedCode(BaseModel):
    """Complete parsed code structure."""
    classes: list[ClassInfo] = []
    functions: list[FunctionInfo] = []
    endpoints: list[EndpointInfo] = []
    imports: list[str] = []
    module_docstring: Optional[str] = None


class CodeParser:
    """Parse Python code using AST to extract structure."""
    
    FASTAPI_DECORATORS = {'get', 'post', 'put', 'delete', 'patch', 'options', 'head'}
    
    def parse(self, code: str) -> ParsedCode:
        """Parse code and extract all structural information."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error parsing code: {e}")
            raise ValueError(f"Invalid Python syntax: {e}")
        
        parsed = ParsedCode()
        
        # Get module docstring
        parsed.module_docstring = ast.get_docstring(tree)
        
        # Extract imports
        parsed.imports = self._extract_imports(tree)
        
        # Process top-level nodes
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                parsed.classes.append(self._parse_class(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._parse_function(node)
                endpoint = self._check_endpoint(node, func_info)
                if endpoint:
                    parsed.endpoints.append(endpoint)
                else:
                    parsed.functions.append(func_info)
        
        logger.info(
            f"Parsed: {len(parsed.classes)} classes, "
            f"{len(parsed.functions)} functions, "
            f"{len(parsed.endpoints)} endpoints"
        )
        
        return parsed
    
    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
    
    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """Parse a class definition."""
        methods = []
        class_vars = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_function(item))
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_vars.append(target.id)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_vars.append(item.target.id)
        
        return ClassInfo(
            name=node.name,
            bases=[self._get_name(base) for base in node.bases],
            methods=methods,
            class_variables=class_vars,
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
    
    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        """Parse a function or method definition."""
        parameters = []
        
        # Process arguments
        args = node.args
        defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
        
        for arg, default in zip(args.args, defaults):
            # Skip 'self' and 'cls' for methods
            if arg.arg in ('self', 'cls'):
                continue
            
            param = ParameterInfo(
                name=arg.arg,
                annotation=self._get_annotation(arg.annotation),
                default=self._get_default_value(default) if default else None,
                is_required=default is None
            )
            parameters.append(param)
        
        # Handle *args and **kwargs
        if args.vararg:
            parameters.append(ParameterInfo(
                name=f"*{args.vararg.arg}",
                annotation=self._get_annotation(args.vararg.annotation),
                is_required=False
            ))
        
        if args.kwarg:
            parameters.append(ParameterInfo(
                name=f"**{args.kwarg.arg}",
                annotation=self._get_annotation(args.kwarg.annotation),
                is_required=False
            ))
        
        return FunctionInfo(
            name=node.name,
            parameters=parameters,
            return_annotation=self._get_annotation(node.returns),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
    
    def _check_endpoint(self, node: ast.FunctionDef | ast.AsyncFunctionDef, func_info: FunctionInfo) -> Optional[EndpointInfo]:
        """Check if function is a FastAPI endpoint."""
        for decorator in node.decorator_list:
            decorator_info = self._parse_decorator_for_endpoint(decorator)
            if decorator_info:
                http_method, path, response_model = decorator_info
                return EndpointInfo(
                    path=path,
                    http_method=http_method.upper(),
                    function_name=func_info.name,
                    parameters=func_info.parameters,
                    return_annotation=func_info.return_annotation,
                    docstring=func_info.docstring,
                    response_model=response_model,
                    is_async=func_info.is_async
                )
        return None
    
    def _parse_decorator_for_endpoint(self, decorator: ast.expr) -> Optional[tuple[str, str, Optional[str]]]:
        """Parse decorator to extract FastAPI endpoint info."""
        if isinstance(decorator, ast.Call):
            func = decorator.func
            if isinstance(func, ast.Attribute) and func.attr in self.FASTAPI_DECORATORS:
                http_method = func.attr
                path = "/"
                response_model = None
                
                # Get path from first positional argument
                if decorator.args:
                    first_arg = decorator.args[0]
                    if isinstance(first_arg, ast.Constant):
                        path = first_arg.value
                
                # Check for response_model in keywords
                for keyword in decorator.keywords:
                    if keyword.arg == "response_model":
                        response_model = self._get_name(keyword.value)
                
                return (http_method, path, response_model)
        
        return None
    
    def _get_annotation(self, node: Optional[ast.expr]) -> Optional[str]:
        """Convert AST annotation to string."""
        if node is None:
            return None
        return ast.unparse(node)
    
    def _get_default_value(self, node: ast.expr) -> str:
        """Get string representation of default value."""
        return ast.unparse(node)
    
    def _get_decorator_name(self, node: ast.expr) -> str:
        """Get decorator name as string."""
        return ast.unparse(node)
    
    def _get_name(self, node: ast.expr) -> str:
        """Get name from various AST node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return ast.unparse(node)
        return ast.unparse(node)
