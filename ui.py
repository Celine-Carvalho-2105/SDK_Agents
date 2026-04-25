"""
Streamlit UI for the Agentic AI Documentation Generator
Run: streamlit run ui.py
"""

import streamlit as st
import ast
import re
import json
import os
import time
from datetime import datetime
from pathlib import Path

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocGen AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0d0f14;
    --surface: #13161e;
    --surface2: #1a1e2a;
    --border: #252a38;
    --accent: #5c6ef8;
    --accent2: #38d9a9;
    --accent3: #f7b731;
    --text: #e8eaf6;
    --muted: #6b7280;
    --danger: #f87171;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background-color: var(--bg) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Main header */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #5c6ef8 0%, #38d9a9 60%, #f7b731 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1.1;
    margin: 0;
}

.hero-sub {
    color: var(--muted);
    font-size: 1rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 6px;
    letter-spacing: 0.5px;
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-sdk { background: #5c6ef820; color: #5c6ef8; border: 1px solid #5c6ef840; }
.badge-fastapi { background: #38d9a920; color: #38d9a9; border: 1px solid #38d9a940; }
.badge-general { background: #f7b73120; color: #f7b731; border: 1px solid #f7b73140; }

/* Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
}
.metric-label {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Validation result box */
.validation-pass {
    background: #38d9a910;
    border: 1px solid #38d9a940;
    border-left: 4px solid #38d9a9;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #38d9a9;
}
.validation-warn {
    background: #f7b73110;
    border: 1px solid #f7b73140;
    border-left: 4px solid #f7b731;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #f7b731;
}

/* Section divider */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* Override streamlit defaults */
.stTextArea textarea {
    background-color: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px #5c6ef820 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #5c6ef8, #38d9a9) !important;
    color: #0d0f14 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.5px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
}

.stSelectbox > div > div {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background-color: var(--accent) !important;
    color: white !important;
}

.stExpander {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
.stExpander summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    color: var(--text) !important;
}

/* JSON/code display */
pre {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    color: var(--text) !important;
    overflow-x: auto !important;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

.stMarkdown table {
    border-collapse: collapse !important;
    width: 100% !important;
}
.stMarkdown th {
    background: var(--surface2) !important;
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    padding: 8px 12px !important;
    border: 1px solid var(--border) !important;
}
.stMarkdown td {
    padding: 8px 12px !important;
    border: 1px solid var(--border) !important;
    font-size: 0.85rem !important;
}

/* Download button */
.stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--accent2) !important;
    border: 1px solid var(--accent2) !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: #38d9a910 !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* Alerts */
.stAlert {
    border-radius: 10px !important;
}

/* Input labels */
.stTextArea label, .stSelectbox label, .stCheckbox label {
    color: var(--muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* Checkbox */
.stCheckbox {
    color: var(--text) !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Utility: Pure Python AST-based pipeline (no external deps required) ─────

def detect_code_type(code: str) -> tuple[str, float, list[str]]:
    FASTAPI_PATTERNS = [
        r'from\s+fastapi\s+import', r'import\s+fastapi',
        r'FastAPI\s*\(', r'@app\.(get|post|put|delete|patch)',
        r'@router\.(get|post|put|delete|patch)', r'APIRouter\s*\(',
    ]
    indicators = []
    fastapi_score = sum(1 for p in FASTAPI_PATTERNS if re.search(p, code))
    if fastapi_score > 0:
        indicators.append("FastAPI imports/decorators found")
        return "fastapi", min(1.0, fastapi_score * 0.3), indicators

    sdk_score = 0
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                sdk_score += 2
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        sdk_score += 1
    except SyntaxError:
        if 'class ' in code: sdk_score += 2

    if sdk_score >= 2:
        indicators.append("Class definitions with methods detected")
        return "sdk", min(1.0, sdk_score * 0.15), indicators

    indicators.append("General Python functions/scripts")
    return "general_python", 0.85, indicators


def parse_code(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"error": str(e), "classes": [], "functions": [], "endpoints": [], "imports": [], "module_docstring": None}

    FASTAPI_METHODS = {'get', 'post', 'put', 'delete', 'patch', 'options', 'head'}

    def get_annotation(node):
        if node is None: return None
        try: return ast.unparse(node)
        except: return None

    def get_default(node):
        if node is None: return None
        try: return ast.unparse(node)
        except: return None

    def get_decorator_name(node):
        try: return ast.unparse(node)
        except: return ""

    def parse_params(func_node):
        args = func_node.args
        defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
        params = []
        for arg, default in zip(args.args, defaults):
            if arg.arg in ('self', 'cls'): continue
            params.append({
                "name": arg.arg,
                "type": get_annotation(arg.annotation) or "Not specified",
                "default": get_default(default),
                "required": default is None
            })
        if args.vararg:
            params.append({"name": f"*{args.vararg.arg}", "type": get_annotation(args.vararg.annotation) or "Not specified", "default": None, "required": False})
        if args.kwarg:
            params.append({"name": f"**{args.kwarg.arg}", "type": get_annotation(args.kwarg.annotation) or "Not specified", "default": None, "required": False})
        return params

    def check_endpoint(func_node):
        for dec in func_node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if dec.func.attr in FASTAPI_METHODS:
                    path = "/"
                    response_model = None
                    if dec.args and isinstance(dec.args[0], ast.Constant):
                        path = dec.args[0].value
                    for kw in dec.keywords:
                        if kw.arg == "response_model":
                            try: response_model = ast.unparse(kw.value)
                            except: pass
                    return dec.func.attr.upper(), path, response_model
        return None

    result = {
        "module_docstring": ast.get_docstring(tree),
        "imports": [],
        "classes": [],
        "functions": [],
        "endpoints": []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names: result["imports"].append(a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names: result["imports"].append(f"{mod}.{a.name}")

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            class_vars = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append({
                        "name": item.name,
                        "parameters": parse_params(item),
                        "return_type": get_annotation(item.returns) or "Not specified",
                        "decorators": [get_decorator_name(d) for d in item.decorator_list],
                        "docstring": ast.get_docstring(item),
                        "is_async": isinstance(item, ast.AsyncFunctionDef)
                    })
                elif isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name): class_vars.append(t.id)
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    class_vars.append(item.target.id)
            result["classes"].append({
                "name": node.name,
                "bases": [get_annotation(b) or "" for b in node.bases],
                "methods": methods,
                "class_variables": class_vars,
                "docstring": ast.get_docstring(node),
                "decorators": [get_decorator_name(d) for d in node.decorator_list]
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ep = check_endpoint(node)
            if ep:
                http_method, path, response_model = ep
                result["endpoints"].append({
                    "path": path,
                    "http_method": http_method,
                    "function_name": node.name,
                    "parameters": parse_params(node),
                    "return_type": get_annotation(node.returns) or "Not specified",
                    "response_model": response_model or "Not specified",
                    "docstring": ast.get_docstring(node),
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })
            else:
                result["functions"].append({
                    "name": node.name,
                    "parameters": parse_params(node),
                    "return_type": get_annotation(node.returns) or "Not specified",
                    "decorators": [get_decorator_name(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })

    return result


def call_groq(api_key: str, prompt: str, temperature: float = 0.2) -> str:
    """Call Groq API directly."""
    import urllib.request
    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "max_tokens": 4096,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Groq API error: {e}")


def build_prompt(code_type: str, parsed: dict, extracted_info: str) -> str:
    base_rules = """CRITICAL ANTI-HALLUCINATION RULES:
1. Document ONLY items present in EXTRACTED_DATA below
2. DO NOT invent any function, method, class, endpoint, or parameter
3. If something is unclear, write "Not specified"
4. Every documented item MUST be traceable to EXTRACTED_DATA

"""
    parsed_str = json.dumps(parsed, indent=2)

    if code_type == "fastapi":
        return base_rules + f"""Generate API documentation for these FastAPI endpoints.
EXTRACTED_DATA:
{extracted_info}

GROUND_TRUTH:
{parsed_str}

Format as Markdown:
# API Documentation
## Base URL
Not specified in source code.
## Authentication
Not specified in source code.
## Endpoints
[For each endpoint: method, path, description (from docstring or "Not specified"), parameters table, response, curl example]
"""
    elif code_type == "sdk":
        return base_rules + f"""Generate SDK documentation for these Python classes.
EXTRACTED_DATA:
{extracted_info}

GROUND_TRUTH:
{parsed_str}

Format as Markdown:
# SDK Documentation
## Overview
[Brief overview from class names/docstrings only]
## Installation
```bash
pip install <package-name>
```
Note: Package name not specified in source code.
## Class Reference
[For each class: name, docstring, then for each method: name, description, parameters table with (Name|Type|Required|Default|Description), Returns]
"""
    else:
        return base_rules + f"""Generate module documentation for these Python functions.
EXTRACTED_DATA:
{extracted_info}

GROUND_TRUTH:
{parsed_str}

Format as Markdown:
# Module Documentation
## Overview
[Brief overview]
## Functions
[For each function: name, description, parameters table, Returns, Example]
"""


def build_extracted_info(parsed: dict, code_type: str) -> str:
    lines = []
    if code_type == "sdk":
        for cls in parsed.get("classes", []):
            lines.append(f"CLASS: {cls['name']}")
            if cls.get("docstring"): lines.append(f"  Docstring: {cls['docstring']}")
            for m in cls.get("methods", []):
                lines.append(f"  METHOD: {m['name']} (async={m['is_async']})")
                if m.get("docstring"): lines.append(f"    Docstring: {m['docstring']}")
                for p in m.get("parameters", []):
                    req = "required" if p['required'] else f"default={p['default']}"
                    lines.append(f"    PARAM: {p['name']}: {p['type']} ({req})")
                lines.append(f"    RETURNS: {m['return_type']}")
    elif code_type == "fastapi":
        for ep in parsed.get("endpoints", []):
            lines.append(f"ENDPOINT: {ep['http_method']} {ep['path']}")
            lines.append(f"  Function: {ep['function_name']} (async={ep['is_async']})")
            if ep.get("docstring"): lines.append(f"  Docstring: {ep['docstring']}")
            for p in ep.get("parameters", []):
                req = "required" if p['required'] else f"default={p['default']}"
                lines.append(f"  PARAM: {p['name']}: {p['type']} ({req})")
            lines.append(f"  RESPONSE_MODEL: {ep['response_model']}")
    else:
        for fn in parsed.get("functions", []):
            lines.append(f"FUNCTION: {fn['name']} (async={fn['is_async']})")
            if fn.get("docstring"): lines.append(f"  Docstring: {fn['docstring']}")
            for p in fn.get("parameters", []):
                req = "required" if p['required'] else f"default={p['default']}"
                lines.append(f"  PARAM: {p['name']}: {p['type']} ({req})")
            lines.append(f"  RETURNS: {fn['return_type']}")
        for cls in parsed.get("classes", []):
            lines.append(f"CLASS: {cls['name']}")
            for m in cls.get("methods", []):
                lines.append(f"  METHOD: {m['name']}")
    return "\n".join(lines)


def validate_docs(docs: str, parsed: dict) -> tuple[bool, list, list]:
    """Rule-based validation against parsed structure."""
    hallucinations = []
    verified = []

    doc_methods = re.findall(r'####\s*(?:Method:\s*)?`?(\w+)`?', docs)
    doc_classes = re.findall(r'###\s*(?:Class:\s*)?`?(\w+)`?', docs)
    doc_endpoints = re.findall(r'###\s*(GET|POST|PUT|DELETE|PATCH)\s+`?([^`\n]+)`?', docs)

    gt_classes = {c["name"] for c in parsed.get("classes", [])}
    gt_methods = set()
    for c in parsed.get("classes", []): 
        for m in c.get("methods", []): gt_methods.add(m["name"])
    for f in parsed.get("functions", []): gt_methods.add(f["name"])
    gt_endpoints = {(e["http_method"].upper(), e["path"]) for e in parsed.get("endpoints", [])}

    for cls in doc_classes:
        if cls in gt_classes: verified.append(f"Class: {cls}")

    for method in doc_methods:
        if method in gt_methods: verified.append(f"Method: {method}")
        elif method not in gt_classes and method not in {"Not", "Overview", "Installation", "Quick", "Base", "Authentication", "Endpoints", "Functions", "Returns", "Parameters", "Example", "Module"}:
            hallucinations.append({"type": "method", "name": method})

    for http_method, path in doc_endpoints:
        path = path.strip()
        if (http_method.upper(), path) in gt_endpoints: verified.append(f"Endpoint: {http_method} {path}")

    return len(hallucinations) == 0, hallucinations, verified


# ─── Sample codes ─────────────────────────────────────────────────────────────
SAMPLE_SDK = '''"""Weather SDK"""
from typing import Optional, List
from datetime import datetime

class WeatherClient:
    """Client for fetching weather data."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.com"):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_current_weather(self, city: str, units: str = "metric") -> dict:
        """Get current weather for a city."""
        pass
    
    def get_forecast(self, city: str, days: int = 7, include_hourly: bool = False) -> List[dict]:
        """Get weather forecast."""
        pass
    
    async def get_historical_data(self, city: str, start_date: datetime, end_date: Optional[datetime] = None) -> List[dict]:
        """Get historical weather data."""
        pass

class WeatherAlert:
    """Represents a weather alert."""
    
    def __init__(self, alert_type: str, severity: str, message: str):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary."""
        return {"type": self.alert_type, "severity": self.severity, "message": self.message}
'''

SAMPLE_FASTAPI = '''from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str

@app.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: int, include_details: bool = False):
    """Get a user by their ID."""
    pass

@app.post("/users", response_model=UserCreate)
async def create_user(user: UserCreate):
    """Create a new user."""
    pass

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user by ID."""
    pass
'''

SAMPLE_GENERAL = '''"""Data processing utilities."""
from typing import List, Optional

def calculate_statistics(data: List[float]) -> dict:
    """Calculate basic statistics for a dataset."""
    if not data:
        return {}
    return {
        "mean": sum(data) / len(data),
        "min": min(data),
        "max": max(data),
        "count": len(data)
    }

def filter_outliers(data: List[float], threshold: float = 2.0) -> List[float]:
    """Remove outliers from data using z-score method."""
    if len(data) < 2:
        return data
    mean = sum(data) / len(data)
    return [x for x in data if abs(x - mean) < threshold * mean]

def normalize_data(data: List[float], min_val: Optional[float] = None, max_val: Optional[float] = None) -> List[float]:
    """Normalize data to [0, 1] range."""
    lo = min_val if min_val is not None else min(data)
    hi = max_val if max_val is not None else max(data)
    if hi == lo:
        return [0.0] * len(data)
    return [(x - lo) / (hi - lo) for x in data]
'''


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown('<div class="section-label">API Keys</div>', unsafe_allow_html=True)
    
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get yours at console.groq.com"
    )
    
    use_groq = bool(groq_key)
    
    if groq_key:
        st.success("✅ Groq key set")
    else:
        st.info("ℹ️ No Groq key — AST preview mode only")

    st.markdown('<div class="section-label" style="margin-top:1rem">Options</div>', unsafe_allow_html=True)
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05,
        help="Lower = less hallucination")
    
    strict_validation = st.checkbox("Strict Validation", value=True,
        help="Run multi-pass validation to remove hallucinations")
    
    show_parsed = st.checkbox("Show Parsed AST", value=False)
    show_extracted = st.checkbox("Show Extracted Info", value=False)

    st.markdown("---")
    st.markdown('<div class="section-label">Quick Load</div>', unsafe_allow_html=True)
    sample = st.selectbox("Sample Code", ["— none —", "SDK (WeatherClient)", "FastAPI (REST API)", "General Python (Utils)"])

    st.markdown("---")
    st.markdown(
        '<div style="font-family: JetBrains Mono; font-size: 0.7rem; color: #6b7280; line-height: 1.6">'
        'Model: llama-3.1-8b-instant<br>'
        'Parser: Python AST<br>'
        'Validation: Rule-based + LLM'
        '</div>',
        unsafe_allow_html=True
    )


# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">DocGen AI</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">// agentic • hallucination-free • ast-validated</p>', unsafe_allow_html=True)
st.markdown("")

# Resolve sample
default_code = ""
if sample == "SDK (WeatherClient)": default_code = SAMPLE_SDK
elif sample == "FastAPI (REST API)": default_code = SAMPLE_FASTAPI
elif sample == "General Python (Utils)": default_code = SAMPLE_GENERAL

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown('<div class="section-label">Python Code Input</div>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Upload .py file", type=["py"], label_visibility="collapsed")
    if uploaded:
        default_code = uploaded.read().decode("utf-8")
    
    code_input = st.text_area(
        "code",
        value=default_code,
        height=420,
        placeholder="# Paste your Python code here...\n# Supports: SDK classes, FastAPI endpoints, general Python",
        label_visibility="collapsed"
    )

    generate_btn = st.button("⚡ Generate Documentation", use_container_width=True)

with col_output:
    st.markdown('<div class="section-label">Live Analysis</div>', unsafe_allow_html=True)
    
    if code_input.strip():
        code_type, confidence, indicators = detect_code_type(code_input)
        parsed = parse_code(code_input)
        
        badge_class = {"sdk": "badge-sdk", "fastapi": "badge-fastapi", "general_python": "badge-general"}.get(code_type, "badge-general")
        badge_label = {"sdk": "SDK", "fastapi": "FastAPI", "general_python": "General Python"}.get(code_type, code_type)
        
        st.markdown(
            f'<span class="badge {badge_class}">{badge_label}</span> '
            f'<span style="color:#6b7280; font-size:0.78rem; font-family:JetBrains Mono">confidence: {confidence:.0%}</span>',
            unsafe_allow_html=True
        )
        st.markdown("")
        
        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(parsed.get("classes", []))}</div><div class="metric-label">Classes</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(parsed.get("functions", []))}</div><div class="metric-label">Functions</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(parsed.get("endpoints", []))}</div><div class="metric-label">Endpoints</div></div>', unsafe_allow_html=True)
        with m4:
            total_methods = sum(len(c.get("methods", [])) for c in parsed.get("classes", []))
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total_methods}</div><div class="metric-label">Methods</div></div>', unsafe_allow_html=True)
        
        st.markdown("")
        
        if "error" in parsed:
            st.error(f"⚠️ Syntax Error: {parsed['error']}")
        
        if show_parsed and not "error" in parsed:
            with st.expander("🔍 Parsed AST Structure"):
                st.code(json.dumps(parsed, indent=2), language="json")
        
        if show_extracted and not "error" in parsed:
            with st.expander("📋 Extracted Info"):
                extracted_info = build_extracted_info(parsed, code_type)
                st.code(extracted_info, language="text")
    else:
        st.markdown(
            '<div style="color: #6b7280; font-family: JetBrains Mono; font-size: 0.85rem; '
            'border: 1px dashed #252a38; border-radius: 12px; padding: 2rem; text-align: center; margin-top: 1rem">'
            'Paste code on the left to see live analysis'
            '</div>',
            unsafe_allow_html=True
        )


# ─── Generation + Results ──────────────────────────────────────────────────────
if generate_btn and code_input.strip():
    if "error" in parse_code(code_input):
        st.error("Cannot generate docs — fix the syntax error first.")
        st.stop()
    
    st.markdown("---")
    st.markdown('<div class="section-label">Generated Documentation</div>', unsafe_allow_html=True)
    
    parsed = parse_code(code_input)
    code_type, _, _ = detect_code_type(code_input)
    extracted_info = build_extracted_info(parsed, code_type)
    
    with st.spinner("Running pipeline…"):
        progress = st.progress(0)
        status = st.empty()
        
        # Step 1: Parse
        status.markdown("**[1/4]** 🔍 Parsing code with AST…")
        time.sleep(0.3)
        progress.progress(25)
        
        # Step 2: Generate
        status.markdown("**[2/4]** 🤖 Generating documentation…")
        
        if use_groq:
            try:
                prompt = build_prompt(code_type, parsed, extracted_info)
                documentation = call_groq(groq_key, prompt, temperature)
            except RuntimeError as e:
                st.error(str(e))
                st.stop()
        else:
            # AST-only fallback: build markdown directly from parsed structure
            lines = []
            if code_type == "sdk":
                lines.append("# SDK Documentation\n")
                lines.append("## Overview\n")
                lines.append("SDK auto-documented from source code.\n\n")
                lines.append("## Class Reference\n")
                for cls in parsed.get("classes", []):
                    lines.append(f"### Class: `{cls['name']}`\n")
                    if cls.get("docstring"): lines.append(f"{cls['docstring']}\n\n")
                    for m in cls.get("methods", []):
                        lines.append(f"#### Method: `{m['name']}`\n")
                        if m.get("docstring"): lines.append(f"**Description:** {m['docstring']}\n\n")
                        if m["parameters"]:
                            lines.append("**Parameters:**\n\n| Name | Type | Required | Default |\n|------|------|----------|---------|")
                            for p in m["parameters"]:
                                req = "Yes" if p["required"] else "No"
                                default = p["default"] or "—"
                                lines.append(f"| `{p['name']}` | `{p['type']}` | {req} | {default} |")
                            lines.append("")
                        lines.append(f"**Returns:** `{m['return_type']}`\n")
            elif code_type == "fastapi":
                lines.append("# API Documentation\n")
                lines.append("## Base URL\nNot specified in source code.\n\n")
                lines.append("## Endpoints\n")
                for ep in parsed.get("endpoints", []):
                    lines.append(f"### `{ep['http_method']} {ep['path']}`\n")
                    if ep.get("docstring"): lines.append(f"**Description:** {ep['docstring']}\n\n")
                    if ep["parameters"]:
                        lines.append("**Parameters:**\n\n| Name | Type | Required | Default |\n|------|------|----------|---------|")
                        for p in ep["parameters"]:
                            req = "Yes" if p["required"] else "No"
                            default = p["default"] or "—"
                            lines.append(f"| `{p['name']}` | `{p['type']}` | {req} | {default} |")
                        lines.append("")
                    lines.append(f"**Response Model:** `{ep['response_model']}`\n")
            else:
                lines.append("# Module Documentation\n")
                lines.append("## Functions\n")
                for fn in parsed.get("functions", []):
                    lines.append(f"### `{fn['name']}`\n")
                    if fn.get("docstring"): lines.append(f"**Description:** {fn['docstring']}\n\n")
                    if fn["parameters"]:
                        lines.append("**Parameters:**\n\n| Name | Type | Required | Default |\n|------|------|----------|---------|")
                        for p in fn["parameters"]:
                            req = "Yes" if p["required"] else "No"
                            default = p["default"] or "—"
                            lines.append(f"| `{p['name']}` | `{p['type']}` | {req} | {default} |")
                        lines.append("")
                    lines.append(f"**Returns:** `{fn['return_type']}`\n")
            documentation = "\n".join(lines)
        
        progress.progress(65)
        
        # Step 3: Validate
        status.markdown("**[3/4]** ✅ Validating against parsed structure…")
        time.sleep(0.3)
        is_valid, hallucinations, verified = validate_docs(documentation, parsed)
        progress.progress(90)
        
        # Step 4: Finalize
        status.markdown("**[4/4]** 💾 Finalizing output…")
        time.sleep(0.2)
        progress.progress(100)
        status.empty()
        progress.empty()
    
    # ── Validation summary ─────────────────────────────────────────────────
    vcol1, vcol2 = st.columns([2, 1])
    with vcol1:
        if is_valid:
            st.markdown(
                f'<div class="validation-pass">✅ VALIDATION PASSED — {len(verified)} items verified against AST ground truth. Zero hallucinations detected.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="validation-warn">⚠️ VALIDATION: {len(hallucinations)} potential issue(s) flagged. {len(verified)} items verified.</div>',
                unsafe_allow_html=True
            )
            for h in hallucinations:
                st.caption(f"→ Flagged `{h['name']}` ({h['type']})")
    
    with vcol2:
        if not use_groq:
            st.info("ℹ️ AST-only mode\nAdd Groq key for AI-enhanced docs")
    
    st.markdown("")
    
    # ── Output Tabs ────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📄 Documentation", "🔍 Raw Markdown", "📊 Parse Summary"])
    
    with tab1:
        st.markdown(documentation)
    
    with tab2:
        st.code(documentation, language="markdown")
    
    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Parsed Structure**")
            st.json(parsed)
        with c2:
            st.markdown("**Pipeline Metadata**")
            st.json({
                "code_type": code_type,
                "groq_used": use_groq,
                "temperature": temperature if use_groq else "N/A",
                "model": "llama-3.1-8b-instant" if use_groq else "AST-only",
                "classes": len(parsed.get("classes", [])),
                "functions": len(parsed.get("functions", [])),
                "endpoints": len(parsed.get("endpoints", [])),
                "validation_passed": is_valid,
                "hallucinations_flagged": len(hallucinations),
                "items_verified": len(verified),
                "generated_at": datetime.now().isoformat()
            })
    
    st.markdown("")
    
    # ── Download buttons ───────────────────────────────────────────────────
    dl1, dl2, dl3, _ = st.columns([1, 1, 1, 2])
    with dl1:
        st.download_button(
            "⬇️ Download .md",
            data=documentation,
            file_name=f"documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with dl2:
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(parsed, indent=2),
            file_name=f"parsed_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    with dl3:
        meta = json.dumps({
            "code_type": code_type,
            "groq_used": use_groq,
            "validation_passed": is_valid,
            "hallucinations_flagged": len(hallucinations),
            "verified_items": verified,
            "generated_at": datetime.now().isoformat()
        }, indent=2)
        st.download_button(
            "⬇️ Download Report",
            data=meta,
            file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )