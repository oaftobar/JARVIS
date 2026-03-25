# JARVIS

An AI coding agent powered by Google's Gemini API that can read files, list directories, write files, and execute Python code within a constrained working directory.

## Features

- **File Operations**: Read and write files with path traversal protection
- **Directory Listing**: List files with size and directory status
- **Code Execution**: Run Python files with optional arguments
- **Agent Loop**: Iteratively calls the LLM with tool results for complex tasks

## Setup

```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uv sync
```

## Usage

```bash
uv run main.py "your prompt here"
uv run main.py "your prompt here" --verbose
```

## Working Directory

The agent is constrained to operate within the `./calculator` directory for security.
