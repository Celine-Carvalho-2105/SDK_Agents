"""Prompt templates for all agents - designed to prevent hallucination."""

EXTRACTION_PROMPT = """You are a precise code analyzer. Your task is to extract information ONLY from the provided parsed code structure.

CRITICAL RULES:
1. ONLY report what exists in the parsed data below
2. DO NOT invent, assume, or hallucinate any methods, parameters, or behaviors
3. If information is missing, write "Not specified"
4. Every item you report MUST be directly traceable to the parsed data

PARSED CODE STRUCTURE:
{parsed_structure}

CODE TYPE: {code_type}

Extract and organize the following based on code type:

For SDK (class-based):
- List each class name EXACTLY as parsed
- List each method name EXACTLY as parsed  
- List parameters with their exact names and types from parsing
- Note return types if present in parsing, otherwise "Not specified"

For FastAPI:
- List each endpoint decorator EXACTLY as parsed (e.g., @app.get, @app.post)
- List route paths EXACTLY as parsed
- List HTTP methods EXACTLY as parsed
- List parameters (path, query, body) EXACTLY as parsed
- Note response models if present in parsing, otherwise "Not specified"

For General Python:
- List each function name EXACTLY as parsed
- List parameters with their exact names and types from parsing
- Note return types if present in parsing, otherwise "Not specified"

OUTPUT FORMAT:
Provide a structured JSON-like format with ONLY the extracted information.
Mark any unclear or missing information as "Not specified".
"""

SDK_DOC_PROMPT = """You are a technical documentation writer. Generate documentation STRICTLY based on the extracted code information below.

CRITICAL ANTI-HALLUCINATION RULES:
1. Document ONLY the classes, methods, and parameters provided in EXTRACTED_DATA
2. DO NOT invent any functionality not present in EXTRACTED_DATA
3. DO NOT assume behaviors - if not specified, write "Behavior not specified in source code"
4. DO NOT add methods, parameters, or features that don't exist in EXTRACTED_DATA
5. Every documented item MUST exist in EXTRACTED_DATA

EXTRACTED_DATA:
{extracted_data}

GROUND_TRUTH_PARSED_STRUCTURE:
{parsed_structure}

Generate documentation in this EXACT format:

# SDK Documentation

## Overview
[Brief description based ONLY on class/method names - do not invent functionality]

## Installation
```bash
pip install [package-name]
Note: Package name not specified in source code.

Quick Start
[Basic usage example using ONLY documented classes/methods]

Class Reference
For each class in EXTRACTED_DATA:

Class: [ClassName]
[Description based only on what's evident from method names]

For each method:

Method: method_name
Description: [Only what's evident from name/signature, or "Not specified"] Parameters:

Name	Type	Required	Description
[ONLY parameters from EXTRACTED_DATA]			
Returns: [ONLY if specified in EXTRACTED_DATA, otherwise "Not specified"]

Example:

python


[Example using ONLY the exact method signature from EXTRACTED_DATA]
REMEMBER: If it's not in EXTRACTED_DATA, it doesn't exist. Do not hallucinate. """

FASTAPI_DOC_PROMPT = """You are a technical API documentation writer. Generate documentation STRICTLY based on the extracted endpoint information below.

CRITICAL ANTI-HALLUCINATION RULES:

Document ONLY the endpoints present in EXTRACTED_DATA
DO NOT invent any endpoints, parameters, or response fields
DO NOT assume request/response structures not in EXTRACTED_DATA
If something is not specified, explicitly write "Not specified"
Every documented endpoint MUST exist in EXTRACTED_DATA
EXTRACTED_DATA: {extracted_data}

GROUND_TRUTH_PARSED_STRUCTURE: {parsed_structure}

Generate documentation in this EXACT format:

API Documentation
Base URL


Not specified in source code - configure based on deployment
Authentication
Not specified in source code.

Endpoints
For each endpoint in EXTRACTED_DATA:

{HTTP_METHOD} {path}
Description: [Only what's evident from function name/path, or "Not specified"]

Parameters:

Path Parameters:

Name	Type	Required	Description
[ONLY parameters from EXTRACTED_DATA with Path() dependency]			
Query Parameters:

Name	Type	Required	Default	Description
[ONLY parameters from EXTRACTED_DATA with Query() or no dependency]				
Request Body: [ONLY if Pydantic model or Body() is in EXTRACTED_DATA, otherwise "None"]

Response: [ONLY if response_model is in EXTRACTED_DATA, otherwise "Not specified"]

Example Request:

bash


curl -X {METHOD} "http://localhost:8000{path}" [with ONLY documented parameters]
Example Response:

json


[Based ONLY on response_model if specified, otherwise "Response structure not specified"]
REMEMBER: If it's not in EXTRACTED_DATA, it doesn't exist. Do not hallucinate. """

GENERAL_DOC_PROMPT = """You are a technical documentation writer. Generate documentation STRICTLY based on the extracted function information below.

CRITICAL ANTI-HALLUCINATION RULES:

Document ONLY the functions present in EXTRACTED_DATA
DO NOT invent any functions, parameters, or behaviors
DO NOT assume return values or side effects not evident from the code
If something is not specified, explicitly write "Not specified"
Every documented function MUST exist in EXTRACTED_DATA
EXTRACTED_DATA: {extracted_data}

GROUND_TRUTH_PARSED_STRUCTURE: {parsed_structure}

Generate documentation in this EXACT format:

Module Documentation
Overview
[Brief description based ONLY on function names - do not invent functionality]

Functions
For each function in EXTRACTED_DATA:

function_name
Description: [Only what's evident from name/signature, or "Not specified"]

Parameters:

Name	Type	Required	Default	Description
[ONLY parameters from EXTRACTED_DATA]				
Returns: [ONLY if specified in EXTRACTED_DATA, otherwise "Not specified"]

Raises: [ONLY if evident from code, otherwise "Not specified"]

Example:

python


[Example using ONLY the exact function signature from EXTRACTED_DATA]
REMEMBER: If it's not in EXTRACTED_DATA, it doesn't exist. Do not hallucinate. """

EXAMPLE_PROMPT = """Generate usage examples STRICTLY based on the documented code below.

CRITICAL RULES:

Use ONLY the exact method/function/endpoint signatures provided
DO NOT invent methods or parameters that don't exist
DO NOT assume additional functionality
Examples must be directly executable with the documented signatures
DOCUMENTED_CODE: {documented_code}

GROUND_TRUTH_STRUCTURE: {parsed_structure}

Generate practical examples that:

Use ONLY documented classes/methods/endpoints
Show realistic but simple use cases
Include proper error handling where appropriate
Are syntactically correct and runnable
For each major component, provide ONE clear example. """

VALIDATION_PROMPT = """You are a strict documentation validator. Your job is to detect and remove ALL hallucinated content.

GROUND_TRUTH (Parsed Code Structure): {parsed_structure}

GENERATED_DOCUMENTATION: {generated_docs}

VALIDATION RULES:

Every class in documentation MUST exist in GROUND_TRUTH
Every method in documentation MUST exist in GROUND_TRUTH under the correct class
Every endpoint in documentation MUST exist in GROUND_TRUTH
Every parameter in documentation MUST exist in GROUND_TRUTH for that method/endpoint
Parameter types must match GROUND_TRUTH (or be marked "Not specified" if not in GROUND_TRUTH)
Return types must match GROUND_TRUTH (or be marked "Not specified" if not in GROUND_TRUTH)
VALIDATION PROCESS:

List every class/method/endpoint in the documentation
For each, verify it exists in GROUND_TRUTH
For each parameter, verify it exists in GROUND_TRUTH
Flag any item NOT in GROUND_TRUTH as HALLUCINATED
OUTPUT FORMAT:

json


{{
    "validation_passed": true/false,
    "hallucinations_found": [
        {{
            "type": "method/endpoint/parameter/class",
            "name": "hallucinated_item_name",
            "location": "where it appeared",
            "action": "REMOVE"
        }}
    ],
    "corrections_needed": [
        {{
            "location": "where correction needed",
            "current": "current incorrect value",
            "correct": "value from GROUND_TRUTH"
        }}
    ],
    "verified_items": ["list of items that correctly match GROUND_TRUTH"]
}}
Be extremely strict. When in doubt, flag it. """


