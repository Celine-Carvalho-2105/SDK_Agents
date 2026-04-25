"""Tests for the documentation pipeline."""

import pytest
from tools.type_detector import CodeTypeDetector, CodeType
from tools.parser import CodeParser
from tools.extractor import CodeExtractor


# Sample test codes
SDK_CODE = '''
class MyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def fetch_data(self, endpoint: str) -> dict:
        """Fetch data from endpoint."""
        pass
'''

FASTAPI_CODE = '''
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, include_details: bool = False):
    """Get user by ID."""
    pass

@app.post("/users")
async def create_user(name: str, email: str):
    """Create a new user."""
    pass
'''

GENERAL_CODE = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b

def process_data(data: list, filter_empty: bool = True) -> list:
    """Process and filter data."""
    if filter_empty:
        return [x for x in data if x]
    return data
'''


class TestCodeTypeDetector:
    """Tests for CodeTypeDetector."""
    
    def test_detect_sdk(self):
        detector = CodeTypeDetector()
        result = detector.detect(SDK_CODE)
        assert result.code_type == CodeType.SDK
    
    def test_detect_fastapi(self):
        detector = CodeTypeDetector()
        result = detector.detect(FASTAPI_CODE)
        assert result.code_type == CodeType.FASTAPI
    
    def test_detect_general(self):
        detector = CodeTypeDetector()
        result = detector.detect(GENERAL_CODE)
        assert result.code_type == CodeType.GENERAL_PYTHON


class TestCodeParser:
    """Tests for CodeParser."""
    
    def test_parse_sdk(self):
        parser = CodeParser()
        result = parser.parse(SDK_CODE)
        
        assert len(result.classes) == 1
        assert result.classes[0].name == "MyClient"
        assert len(result.classes[0].methods) == 2
    
    def test_parse_fastapi(self):
        parser = CodeParser()
        result = parser.parse(FASTAPI_CODE)
        
        assert len(result.endpoints) == 2
        assert result.endpoints[0].path == "/users/{user_id}"
        assert result.endpoints[0].http_method == "GET"
        assert result.endpoints[1].http_method == "POST"
    
    def test_parse_general(self):
        parser = CodeParser()
        result = parser.parse(GENERAL_CODE)
        
        assert len(result.functions) == 2
        assert result.functions[0].name == "calculate_sum"
        assert len(result.functions[0].parameters) == 2


class TestCodeExtractor:
    """Tests for CodeExtractor."""
    
    def test_extract_sdk(self):
        parser = CodeParser()
        extractor = CodeExtractor()
        
        parsed = parser.parse(SDK_CODE)
        extracted = extractor.extract(parsed, CodeType.SDK)
        
        assert "classes" in extracted
        assert len(extracted["classes"]) == 1
        assert extracted["classes"][0]["name"] == "MyClient"
    
    def test_extract_fastapi(self):
        parser = CodeParser()
        extractor = CodeExtractor()
        
        parsed = parser.parse(FASTAPI_CODE)
        extracted = extractor.extract(parsed, CodeType.FASTAPI)
        
        assert "endpoints" in extracted
        assert len(extracted["endpoints"]) == 2
    
    def test_no_hallucination_in_extraction(self):
        """Ensure extractor doesn't add non-existent methods."""
        parser = CodeParser()
        extractor = CodeExtractor()
        
        parsed = parser.parse(SDK_CODE)
        extracted = extractor.extract(parsed, CodeType.SDK)
        
        method_names = [m["name"] for m in extracted["classes"][0]["methods"]]
        
        # Only __init__ and fetch_data should exist
        assert "__init__" in method_names
        assert "fetch_data" in method_names
        assert len(method_names) == 2  # No extra methods


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
