# Code Translator Purple Agent (Participant)

This repository contains the implementation of the **Purple Agent**, a participant agent for the Code Translator competition. Its primary role is to receive code translation requests and use a Large Language Model (Google Gemini) to translate the code from a source language to a target language.

## Overview

The Purple Agent acts as a specialized worker.
1.  **Receive Task**: It listens for A2A messages containing code translation requests.
2.  **Translate**: It parses the request and invokes Google's Gemini models (`gemini-2.5-flash`, etc.) to perform the translation. It includes a retry mechanism with multiple model fallbacks in case of errors.
3.  ** Respond**: It returns the translated code in a structured JSON format.

## Repository Structure

-   **`src/`**: Source code for the agent.
    -   **`agent.py`**: The core logic. It handles the `run` loop, parses the input (JSON or text), constructs the prompt for Gemini, and manages model fallbacks and status updates.
    -   **`server.py`**: The entry point. It configures the A2A Agent Card, Capabilities, and Skills, and starts the Starlette/Uvicorn server.
    -   **`messenger.py`**: Utility module handling HTTP communication. It includes the `Messenger` class for talking to other agents and `send_message` logic using `httpx`.
    -   **`executor.py`**: Manages the execution context (`Executor` class), validating requests, managing task state, and invoking the agent instance for each conversation/context.
-   **`tests/`**: Test suite.
    -   **`test_agent.py`**: Integration and conformance tests to verify the agent's behavior and A2A protocol compliance.
    -   **`conftest.py`**: Pytest fixtures.
-   **`Dockerfile`**: Container configuration.
-   **`pyproject.toml`**: Dependency management.

## Setup & Installation

### Prerequisites

-   Python 3.13+
-   A **Google GenAI API Key** (Gemini)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd code_translator_purple_agent
    ```

2.  **Create a virtual environment** (optional):
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install .
    # Or explicitly
    pip install "a2a-sdk[http-server]" uvicorn google-genai python-dotenv
    # For testing
    pip install pytest pytest-asyncio httpx
    ```

4.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    ```

## Running the Agent

### Locally

To start the agent server:

```bash
python src/server.py
```

By default, the server runs on `http://127.0.0.1:9009`.
You can customize the params:

```bash
python src/server.py --host 0.0.0.0 --port 8081
```

### Using Docker

1.  **Build the image**:
    ```bash
    docker build -t purple-agent .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 9009:9009 --env GOOGLE_API_KEY=your_api_key purple-agent
    ```

## Usage

This agent is typically called by the **Green Agent** (Judge) or another orchestrator. It expects a message with the following JSON structure:

```json
{
  "code_to_translate": "def add(a, b): return a + b",
  "source_language": "python",
  "target_language": "javascript"
}
```

The agent will respond with a JSON message:

```json
{
  "translated_code": "function add(a, b) { return a + b; }"
}
```

## Testing

To verify the agent is working correctly:

1.  **Install test dependencies**:
    ```bash
    pip install .[test]
    ```

2.  **Run tests**:
    ```bash
    pytest tests/
    ```

    The tests check:
    -   **Agent Card**: Accessing `/.well-known/agent-card.json`.
    -   **Message Handling**: Sending a dummy translation request and checking if the response is valid.