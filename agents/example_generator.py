"""Example generation agent for creating usage examples."""

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llm.groq_client import get_groq_llm
from prompts.templates import EXAMPLE_PROMPT
from utils.helpers import setup_logging, sanitize_output

logger = setup_logging()


class ExampleGenerator:
    """Agent for generating usage examples from documentation."""
    
    def __init__(self, temperature: float = 0.2):
        self.llm = get_groq_llm(temperature=temperature)
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_template(EXAMPLE_PROMPT)
    
    def generate(
        self,
        documented_code: str,
        parsed_structure: dict[str, Any]
    ) -> str:
        """Generate usage examples based on documentation."""
        chain = self.prompt | self.llm | self.output_parser
        
        try:
            examples = chain.invoke({
                "documented_code": documented_code,
                "parsed_structure": json.dumps(parsed_structure, indent=2)
            })
            
            examples = sanitize_output(examples)
            logger.info(f"Generated {len(examples)} characters of examples")
            
            return examples
            
        except Exception as e:
            logger.error(f"Error generating examples: {e}")
            raise
    
    def append_examples_to_docs(
        self,
        documentation: str,
        parsed_structure: dict[str, Any]
    ) -> str:
        """Generate and append examples to existing documentation."""
        examples = self.generate(documentation, parsed_structure)
        
        # Check if examples section already exists
        if "## Examples" in documentation or "## Usage Examples" in documentation:
            return documentation
        
        # Append examples section
        combined = f"{documentation}\n\n---\n\n## Additional Usage Examples\n\n{examples}"
        return combined
