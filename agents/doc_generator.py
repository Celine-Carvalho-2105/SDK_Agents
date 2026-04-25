"""Documentation generation agent using LangChain and Groq."""

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llm.groq_client import get_groq_llm
from tools.type_detector import CodeType
from prompts.templates import SDK_DOC_PROMPT, FASTAPI_DOC_PROMPT, GENERAL_DOC_PROMPT
from utils.helpers import setup_logging, sanitize_output

logger = setup_logging()


class DocumentationGenerator:
    """Agent for generating documentation from extracted code information."""
    
    def __init__(self, temperature: float = 0.2):
        self.llm = get_groq_llm(temperature=temperature)
        self.output_parser = StrOutputParser()
        
        # Create prompt templates for each code type
        self.prompts = {
            CodeType.SDK: ChatPromptTemplate.from_template(SDK_DOC_PROMPT),
            CodeType.FASTAPI: ChatPromptTemplate.from_template(FASTAPI_DOC_PROMPT),
            CodeType.GENERAL_PYTHON: ChatPromptTemplate.from_template(GENERAL_DOC_PROMPT),
        }
    
    def generate(
        self,
        extracted_data: dict[str, Any],
        parsed_structure: dict[str, Any],
        code_type: CodeType
    ) -> str:
        """Generate documentation based on code type."""
        prompt = self.prompts.get(code_type)
        if not prompt:
            raise ValueError(f"Unknown code type: {code_type}")
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            documentation = chain.invoke({
                "extracted_data": json.dumps(extracted_data, indent=2),
                "parsed_structure": json.dumps(parsed_structure, indent=2)
            })
            
            documentation = sanitize_output(documentation)
            logger.info(f"Generated {len(documentation)} characters of documentation")
            
            return documentation
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            raise
    
    def generate_sdk_docs(self, extracted_data: dict, parsed_structure: dict) -> str:
        """Generate SDK documentation."""
        return self.generate(extracted_data, parsed_structure, CodeType.SDK)
    
    def generate_fastapi_docs(self, extracted_data: dict, parsed_structure: dict) -> str:
        """Generate FastAPI documentation."""
        return self.generate(extracted_data, parsed_structure, CodeType.FASTAPI)
    
    def generate_general_docs(self, extracted_data: dict, parsed_structure: dict) -> str:
        """Generate general Python documentation."""
        return self.generate(extracted_data, parsed_structure, CodeType.GENERAL_PYTHON)
