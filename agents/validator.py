"""Validation agent for detecting and removing hallucinated content."""

import json
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llm.groq_client import get_groq_llm
from prompts.templates import VALIDATION_PROMPT
from utils.helpers import setup_logging

logger = setup_logging()


class ValidationResult:
    """Result of documentation validation."""
    
    def __init__(
        self,
        is_valid: bool,
        hallucinations: list[dict],
        corrections: list[dict],
        verified_items: list[str],
        corrected_documentation: str
    ):
        self.is_valid = is_valid
        self.hallucinations = hallucinations
        self.corrections = corrections
        self.verified_items = verified_items
        self.corrected_documentation = corrected_documentation


class ValidationAgent:
    """Agent for validating documentation against parsed code structure."""
    
    def __init__(self, temperature: float = 0.1):  # Very low temperature for strict validation
        self.llm = get_groq_llm(temperature=temperature)
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_template(VALIDATION_PROMPT)
    
    def validate(
        self,
        generated_docs: str,
        parsed_structure: dict[str, Any]
    ) -> ValidationResult:
        """Validate documentation against parsed code structure."""
        chain = self.prompt | self.llm | self.output_parser
        
        try:
            validation_response = chain.invoke({
                "parsed_structure": json.dumps(parsed_structure, indent=2),
                "generated_docs": generated_docs
            })
            
            # Parse the validation response
            result = self._parse_validation_response(validation_response)
            
            # Apply corrections if needed
            if not result["validation_passed"]:
                corrected_docs = self._apply_corrections(
                    generated_docs,
                    result["hallucinations_found"],
                    result["corrections_needed"],
                    parsed_structure
                )
            else:
                corrected_docs = generated_docs
            
            return ValidationResult(
                is_valid=result["validation_passed"],
                hallucinations=result["hallucinations_found"],
                corrections=result["corrections_needed"],
                verified_items=result["verified_items"],
                corrected_documentation=corrected_docs
            )
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            # Fall back to rule-based validation
            return self._fallback_validation(generated_docs, parsed_structure)
    
    def _parse_validation_response(self, response: str) -> dict[str, Any]:
        """Parse the LLM validation response."""
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Default response if parsing fails
        return {
            "validation_passed": True,
            "hallucinations_found": [],
            "corrections_needed": [],
            "verified_items": []
        }
    
    def _apply_corrections(
        self,
        documentation: str,
        hallucinations: list[dict],
        corrections: list[dict],
        parsed_structure: dict[str, Any]
    ) -> str:
        """Apply corrections to remove hallucinated content."""
        corrected = documentation
        
        # Remove hallucinated items
        for hallucination in hallucinations:
            item_name = hallucination.get("name", "")
            item_type = hallucination.get("type", "")
            
            if item_name:
                # Remove sections mentioning hallucinated items
                patterns = [
                    rf'###\s*{re.escape(item_name)}.*?(?=###|\Z)',  # Remove subsections
                    rf'####\s*Method:\s*`?{re.escape(item_name)}`?.*?(?=####|###|\Z)',  # Remove methods
                    rf'####\s*`?{re.escape(item_name)}`?.*?(?=####|###|\Z)',
                ]
                
                for pattern in patterns:
                    corrected = re.sub(pattern, '', corrected, flags=re.DOTALL | re.IGNORECASE)
        
        # Apply specific corrections
        for correction in corrections:
            current = correction.get("current", "")
            correct = correction.get("correct", "")
            if current and correct:
                corrected = corrected.replace(current, correct)
        
        # Clean up multiple newlines
        corrected = re.sub(r'\n{3,}', '\n\n', corrected)
        
        logger.info(f"Applied {len(hallucinations)} hallucination removals and {len(corrections)} corrections")
        return corrected.strip()
    
    def _fallback_validation(
        self,
        documentation: str,
        parsed_structure: dict[str, Any]
    ) -> ValidationResult:
        """Rule-based fallback validation when LLM validation fails."""
        hallucinations = []
        verified = []
        
        # Extract all documented items
        documented_methods = re.findall(r'####\s*Method:\s*`?(\w+)`?', documentation)
        documented_classes = re.findall(r'###\s*Class:\s*`?(\w+)`?', documentation)
        documented_endpoints = re.findall(r'###\s*(GET|POST|PUT|DELETE|PATCH)\s*`([^`]+)`', documentation)
        
        # Get ground truth from parsed structure
        ground_truth_classes = set()
        ground_truth_methods = {}
        ground_truth_endpoints = set()
        
        if "classes" in parsed_structure:
            for cls in parsed_structure["classes"]:
                class_name = cls.get("name", "")
                ground_truth_classes.add(class_name)
                ground_truth_methods[class_name] = set()
                for method in cls.get("methods", []):
                    method_name = method.get("name", "")
                    ground_truth_methods[class_name].add(method_name)
        
        if "endpoints" in parsed_structure:
            for endpoint in parsed_structure["endpoints"]:
                path = endpoint.get("path", "")
                method = endpoint.get("method", endpoint.get("http_method", ""))
                ground_truth_endpoints.add((method.upper(), path))
        
        if "functions" in parsed_structure:
            for func in parsed_structure["functions"]:
                # Treat top-level functions as methods of an implicit module
                func_name = func.get("name", "")
                if "" not in ground_truth_methods:
                    ground_truth_methods[""] = set()
                ground_truth_methods[""].add(func_name)
        
        # Check for hallucinated classes
        for cls in documented_classes:
            if cls in ground_truth_classes:
                verified.append(f"Class: {cls}")
            else:
                hallucinations.append({
                    "type": "class",
                    "name": cls,
                    "location": "Class Reference",
                    "action": "REMOVE"
                })
        
        # Check for hallucinated methods
        all_ground_truth_methods = set()
        for methods in ground_truth_methods.values():
            all_ground_truth_methods.update(methods)
        
        for method in documented_methods:
            if method in all_ground_truth_methods:
                verified.append(f"Method: {method}")
            else:
                hallucinations.append({
                    "type": "method",
                    "name": method,
                    "location": "Method documentation",
                    "action": "REMOVE"
                })
        
        # Check for hallucinated endpoints
        for http_method, path in documented_endpoints:
            if (http_method.upper(), path) in ground_truth_endpoints:
                verified.append(f"Endpoint: {http_method} {path}")
            else:
                hallucinations.append({
                    "type": "endpoint",
                    "name": f"{http_method} {path}",
                    "location": "Endpoints section",
                    "action": "REMOVE"
                })
        
        is_valid = len(hallucinations) == 0
        
        corrected_docs = documentation
        if not is_valid:
            corrected_docs = self._apply_corrections(
                documentation, hallucinations, [], parsed_structure
            )
        
        logger.info(f"Fallback validation: {len(verified)} verified, {len(hallucinations)} hallucinations")
        
        return ValidationResult(
            is_valid=is_valid,
            hallucinations=hallucinations,
            corrections=[],
            verified_items=verified,
            corrected_documentation=corrected_docs
        )
    
    def strict_validate(
        self,
        documentation: str,
        parsed_structure: dict[str, Any],
        max_iterations: int = 3
    ) -> ValidationResult:
        """Perform strict validation with multiple passes."""
        current_docs = documentation
        all_hallucinations = []
        all_corrections = []
        
        for iteration in range(max_iterations):
            result = self.validate(current_docs, parsed_structure)
            
            if result.is_valid:
                logger.info(f"Validation passed after {iteration + 1} iterations")
                return ValidationResult(
                    is_valid=True,
                    hallucinations=all_hallucinations,
                    corrections=all_corrections,
                    verified_items=result.verified_items,
                    corrected_documentation=result.corrected_documentation
                )
            
            all_hallucinations.extend(result.hallucinations)
            all_corrections.extend(result.corrections)
            current_docs = result.corrected_documentation
            
            logger.info(f"Validation iteration {iteration + 1}: found {len(result.hallucinations)} issues")
        
        # Final fallback validation
        final_result = self._fallback_validation(current_docs, parsed_structure)
        
        return ValidationResult(
            is_valid=final_result.is_valid,
            hallucinations=all_hallucinations + final_result.hallucinations,
            corrections=all_corrections,
            verified_items=final_result.verified_items,
            corrected_documentation=final_result.corrected_documentation
        )
