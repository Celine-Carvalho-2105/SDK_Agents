"""Main documentation generation pipeline."""

import json
import hashlib
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from tools.type_detector import CodeTypeDetector, CodeType
from tools.parser import CodeParser, ParsedCode
from tools.extractor import CodeExtractor
from agents.doc_generator import DocumentationGenerator
from agents.example_generator import ExampleGenerator
from agents.validator import ValidationAgent
from vector_db.pinecone_client import PineconeClient
from utils.helpers import setup_logging, create_output_dir, sanitize_output

logger = setup_logging()


class PipelineResult:
    """Result of the documentation pipeline."""
    
    def __init__(
        self,
        code_type: CodeType,
        parsed_structure: dict,
        extracted_data: dict,
        documentation: str,
        validation_passed: bool,
        hallucinations_removed: int,
        output_path: Optional[Path] = None
    ):
        self.code_type = code_type
        self.parsed_structure = parsed_structure
        self.extracted_data = extracted_data
        self.documentation = documentation
        self.validation_passed = validation_passed
        self.hallucinations_removed = hallucinations_removed
        self.output_path = output_path


class DocumentationPipeline:
    """Complete pipeline for generating validated documentation."""
    
    def __init__(
        self,
        use_pinecone: bool = True,
        output_dir: str = "output"
    ):
        self.type_detector = CodeTypeDetector()
        self.parser = CodeParser()
        self.extractor = CodeExtractor()
        self.doc_generator = DocumentationGenerator()
        self.example_generator = ExampleGenerator()
        self.validator = ValidationAgent()
        
        if use_pinecone:
            self.pinecone = PineconeClient()
        else:
            self.pinecone = None
        
        self.output_dir = output_dir
        
        logger.info("Documentation pipeline initialized")
    
    def process(self, code: str, save_output: bool = True) -> PipelineResult:
        """Process code through the complete pipeline."""
        logger.info("Starting documentation pipeline")
        
        # Step 1: Detect code type
        detection_result = self.type_detector.detect(code)
        code_type = detection_result.code_type
        logger.info(f"Detected code type: {code_type.value} (confidence: {detection_result.confidence:.2f})")
        
        # Step 2: Parse code using AST
        parsed = self.parser.parse(code)
        parsed_dict = self._parsed_to_dict(parsed)
        logger.info(f"Parsed code structure: {len(parsed.classes)} classes, {len(parsed.functions)} functions, {len(parsed.endpoints)} endpoints")
        
        # Step 3: Store in Pinecone (if enabled)
        if self.pinecone and self.pinecone.enabled:
            self._store_in_pinecone(code, parsed_dict, code_type)
            similar_context = self._retrieve_similar_context(code)
            logger.info(f"Retrieved {len(similar_context)} similar code patterns from Pinecone")
        
        # Step 4: Extract structured information
        extracted = self.extractor.extract(parsed, code_type)
        logger.info("Extracted structured code information")
        
        # Step 5: Generate documentation
        documentation = self.doc_generator.generate(
            extracted_data=extracted,
            parsed_structure=parsed_dict,
            code_type=code_type
        )
        logger.info(f"Generated initial documentation ({len(documentation)} chars)")
        
        # Step 6: Generate examples
        documentation = self.example_generator.append_examples_to_docs(
            documentation=documentation,
            parsed_structure=parsed_dict
        )
        logger.info("Added usage examples")
        
        # Step 7: MANDATORY VALIDATION
        validation_result = self.validator.strict_validate(
            documentation=documentation,
            parsed_structure=parsed_dict
        )
        
        final_documentation = validation_result.corrected_documentation
        hallucinations_count = len(validation_result.hallucinations)
        
        if hallucinations_count > 0:
            logger.warning(f"Removed {hallucinations_count} hallucinated items during validation")
        else:
            logger.info("Validation passed - no hallucinations detected")
        
        # Step 8: Save output
        output_path = None
        if save_output:
            output_path = self._save_output(
                documentation=final_documentation,
                code_type=code_type,
                parsed_structure=parsed_dict,
                extracted_data=extracted
            )
            logger.info(f"Saved output to {output_path}")
        
        # Store final documentation in Pinecone
        if self.pinecone and self.pinecone.enabled:
            doc_id = hashlib.md5(final_documentation.encode()).hexdigest()
            self.pinecone.store_documentation(
                doc_id=doc_id,
                documentation=final_documentation,
                metadata={"code_type": code_type.value}
            )
        
        return PipelineResult(
            code_type=code_type,
            parsed_structure=parsed_dict,
            extracted_data=extracted,
            documentation=final_documentation,
            validation_passed=validation_result.is_valid,
            hallucinations_removed=hallucinations_count,
            output_path=output_path
        )
    
    def _parsed_to_dict(self, parsed: ParsedCode) -> dict[str, Any]:
        """Convert ParsedCode to dictionary for JSON serialization."""
        return {
            "classes": [
                {
                    "name": cls.name,
                    "bases": cls.bases,
                    "docstring": cls.docstring,
                    "decorators": cls.decorators,
                    "methods": [
                        {
                            "name": m.name,
                            "parameters": [
                                {
                                    "name": p.name,
                                    "type": p.annotation,
                                    "default": p.default,
                                    "required": p.is_required
                                }
                                for p in m.parameters
                            ],
                            "return_type": m.return_annotation,
                            "decorators": m.decorators,
                            "docstring": m.docstring,
                            "is_async": m.is_async
                        }
                        for m in cls.methods
                    ],
                    "class_variables": cls.class_variables
                }
                for cls in parsed.classes
            ],
            "functions": [
                {
                    "name": f.name,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.annotation,
                            "default": p.default,
                            "required": p.is_required
                        }
                        for p in f.parameters
                    ],
                    "return_type": f.return_annotation,
                    "decorators": f.decorators,
                    "docstring": f.docstring,
                    "is_async": f.is_async
                }
                for f in parsed.functions
            ],
            "endpoints": [
                {
                    "path": e.path,
                    "http_method": e.http_method,
                    "function_name": e.function_name,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.annotation,
                            "default": p.default,
                            "required": p.is_required
                        }
                        for p in e.parameters
                    ],
                    "return_type": e.return_annotation,
                    "response_model": e.response_model,
                    "docstring": e.docstring,
                    "is_async": e.is_async
                }
                for e in parsed.endpoints
            ],
            "imports": parsed.imports,
            "module_docstring": parsed.module_docstring
        }
    
    def _store_in_pinecone(self, code: str, parsed_dict: dict, code_type: CodeType):
        """Store code and parsed structure in Pinecone."""
        # Store code chunks
        self.pinecone.store_code_chunks(
            code=code,
            metadata={"code_type": code_type.value}
        )
        
        # Store parsed structure
        self.pinecone.store_parsed_structure(
            structure=parsed_dict,
            code_type=code_type.value
        )
    
    def _retrieve_similar_context(self, code: str) -> list[dict]:
        """Retrieve similar code patterns from Pinecone."""
        if not self.pinecone or not self.pinecone.enabled:
            return []
        
        # Query with code snippet
        return self.pinecone.retrieve_similar(code[:500], top_k=3)
    
    def _save_output(
        self,
        documentation: str,
        code_type: CodeType,
        parsed_structure: dict,
        extracted_data: dict
    ) -> Path:
        """Save all outputs to files."""
        output_path = create_output_dir(self.output_dir)
        
        # Save documentation as Markdown
        doc_file = output_path / "documentation.md"
        doc_file.write_text(documentation, encoding="utf-8")
        
        # Save parsed structure as JSON
        parsed_file = output_path / "parsed_structure.json"
        parsed_file.write_text(json.dumps(parsed_structure, indent=2), encoding="utf-8")
        
        # Save extracted data as JSON
        extracted_file = output_path / "extracted_data.json"
        extracted_file.write_text(json.dumps(extracted_data, indent=2), encoding="utf-8")
        
        # Save metadata
        metadata = {
            "code_type": code_type.value,
            "generated_at": datetime.now().isoformat(),
            "classes_count": len(parsed_structure.get("classes", [])),
            "functions_count": len(parsed_structure.get("functions", [])),
            "endpoints_count": len(parsed_structure.get("endpoints", []))
        }
        metadata_file = output_path / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        
        return output_path
