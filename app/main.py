"""Main entry point for the documentation generator."""

import sys
import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from app.pipeline import DocumentationPipeline, PipelineResult
from utils.helpers import setup_logging

console = Console()
logger = setup_logging()


def print_result(result: PipelineResult):
    """Pretty print the pipeline result."""
    console.print()
    console.print(Panel(
        f"[bold green]Documentation Generated Successfully[/bold green]\n\n"
        f"[bold]Code Type:[/bold] {result.code_type.value}\n"
        f"[bold]Validation:[/bold] {'✅ Passed' if result.validation_passed else '⚠️ Issues corrected'}\n"
        f"[bold]Hallucinations Removed:[/bold] {result.hallucinations_removed}\n"
        f"[bold]Output Path:[/bold] {result.output_path}",
        title="Pipeline Result",
        border_style="green"
    ))
    
    console.print()
    console.print("[bold]Generated Documentation Preview:[/bold]")
    console.print()
    
    # Show first 2000 chars of documentation
    preview = result.documentation[:2000]
    if len(result.documentation) > 2000:
        preview += "\n\n... [truncated - see full output in file]"
    
    console.print(Markdown(preview))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate documentation from Python code using AI"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to Python file or '-' for stdin"
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--no-pinecone",
        action="store_true",
        help="Disable Pinecone vector storage"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output files"
    )
    
    args = parser.parse_args()
    
    # Read input code
    if args.input == "-" or (not args.input and not sys.stdin.isatty()):
        code = sys.stdin.read()
    elif args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            console.print(f"[red]Error: File not found: {args.input}[/red]")
            sys.exit(1)
        code = input_path.read_text(encoding="utf-8")
    else:
        # Interactive mode - show example
        console.print(Panel(
            "[bold]Agentic AI Documentation Generator[/bold]\n\n"
            "Usage:\n"
            "  python -m app.main <python_file.py>\n"
            "  cat code.py | python -m app.main -\n\n"
            "Running demo with sample code...",
            border_style="blue"
        ))
        
        # Demo with sample code
        code = SAMPLE_SDK_CODE
    
    try:
        # Initialize pipeline
        pipeline = DocumentationPipeline(
            use_pinecone=not args.no_pinecone,
            output_dir=args.output
        )
        
        # Process code
        console.print("[bold]Processing code...[/bold]")
        result = pipeline.process(code, save_output=not args.no_save)
        
        # Print result
        print_result(result)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Pipeline error")
        sys.exit(1)


# Sample code for demo
SAMPLE_SDK_CODE = '''
"""SDK for interacting with the Weather API."""

from typing import Optional, List
from datetime import datetime


class WeatherClient:
    """Client for fetching weather data."""
    
    def __init__(self, api_key: str, base_url: str = "[api.weather.com](https://api.weather.com)"):
        """Initialize the weather client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url
    
    def get_current_weather(self, city: str, units: str = "metric") -> dict:
        """Get current weather for a city.
        
        Args:
            city: Name of the city
            units: Temperature units (metric/imperial)
            
        Returns:
            Dictionary with weather data
        """
        pass
    
    def get_forecast(
        self,
        city: str,
        days: int = 7,
        include_hourly: bool = False
    ) -> List[dict]:
        """Get weather forecast.
        
        Args:
            city: Name of the city
            days: Number of days to forecast
            include_hourly: Include hourly breakdown
            
        Returns:
            List of forecast data
        """
        pass
    
    async def get_historical_data(
        self,
        city: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get historical weather data.
        
        Args:
            city: Name of the city
            start_date: Start of date range
            end_date: End of date range (optional)
            
        Returns:
            List of historical weather records
        """
        pass


class WeatherAlert:
    """Represents a weather alert."""
    
    def __init__(self, alert_type: str, severity: str, message: str):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary."""
        return {
            "type": self.alert_type,
            "severity": self.severity,
            "message": self.message
        }
'''


if __name__ == "__main__":
    main()
