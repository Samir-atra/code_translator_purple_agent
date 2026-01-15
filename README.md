# Code Translator Purple Agent (Participant)

This repository contains the **Purple Agent** (Participant) for the Code Translator system. It is designed to receive code translation tasks from an evaluator (Green Agent) and return the translated code using the [Agent-to-Agent (A2A) Protocol](https://a2a-protocol.org/).

## Overview

The Purple Agent acts as a "Researcher" or "Developer" translator. When it receives a task containing source code, it:
1.  Analyzes the code using `gemini-2.5-flash`.
2.  Translates it to the requested target language (or inferred target).
3.  Returns the translation as a structured artifact.

## Architecture

*   **Framework**: `a2a-sdk` (Python)
*   **Model**: Gemini 2.5 Flash (via `google-genai`)
*   **Communication**: Agent-to-Agent (A2A) Protocol
*   **Runtime**: Uvicorn

## Prerequisites

*   Python 3.13+
*   [uv](https://github.com/astral-sh/uv) (recommended)
*   Google GenAI API Key

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd code_translator_purple_agent
    ```

2.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

3.  **Install Dependencies:**
    Using `uv`:
    ```bash
    uv sync
    ```

## Running the Agent

### Local Execution
To run the agent server locally:

```bash
uv run src/server.py --host 0.0.0.0 --port 9009
```

The agent will listen on port 9009 (default).

### Docker Execution
To build and run using Docker:

1.  **Build the image:**
    ```bash
    docker build -t code-translator-purple .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 9009:9009 --env-file .env code-translator-purple
    ```

## Project Structure

*   `src/agent.py`: Core agent logic. Receives messages, calls Gemini, and returns artifacts.
*   `src/server.py`: Server entry point.
*   `src/messenger.py`: Helper for A2A communication.
*   `src/executor.py`: Task execution handling.