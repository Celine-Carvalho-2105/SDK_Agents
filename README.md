# Agentic AI Documentation Generator

A production-ready, **hallucination-free** documentation generation system using LangChain, Groq API, and Pinecone.

## Features

- 🎯 **Zero Hallucination**: Every documented item is validated against the parsed AST
- 🔍 **Automatic Code Detection**: SDK, FastAPI, or general Python
- 🧠 **LangChain Agents**: Modular, composable pipeline
- ⚡ **Groq LLM**: Fast inference with llama-3.1-8b-instant
- 🗄️ **Pinecone Integration**: Vector storage for similar code retrieval
- ✅ **Mandatory Validation**: Multi-pass validation removes all hallucinated content

## Installation

### 1. Clone and setup virtual environment

```bash
git clone <repository-url>
cd agentic-doc-generator

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
