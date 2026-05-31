# RepoMirror MCP Server

RepoMirror is a custom-built Model Context Protocol (MCP) server written in Python. It bridges local git repositories directly with large language models (LLMs) running via desktop clients like Cline. By exposing structured codebase analytics over JSON-RPC, it allows local agents to intelligently traverse git timelines, analyze file structures using Abstract Syntax Tree (AST) parsing, and automate software development tasks securely on local hardware.

---

## 🚀 Features

* **Temporal Git Graph Modeling (`get_codebase_graph`)**: Leverages `NetworkX` to construct a real-time chronological dependency graph tracking commits, author metadata, and modified file nodes.
* **AST Structural Deep-Scanning (`analyze_file_functions`)**: Programmatically extracts precise python code structures (function/class definitions, absolute line boundaries), eliminating LLM regex-scraping hallucinations.
* **File Evolution Tracking (`trace_evolution`)**: Traces the history and structural modifications of specific files across the entire repository timeline.
* **100% Local & Private Execution**: Built specifically to connect with local inference engines (e.g., Ollama running `llama3.1`) via Cline, ensuring zero cloud API costs and absolute data privacy.

---

## 🛠️ Architecture Overview

The system architecture decouples the LLM interface from the raw operating system files, using the standardized Model Context Protocol as a secure data pipeline:

1. **User Client (VS Code + Cline)**: Orchestrates the user prompt and delegates background execution permissions.
2. **Local LLM Engine**: Runs token generation locally on the GPU.
3. **RepoMirror MCP Engine**: A Python background process managing repository data collection and AST serialization.

---

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed on your local system:
* Python 3.10 or higher
* Git installed and configured in your system path
* Node.js / npm (for VS Code extension runtimes)

---

## ⚙️ Installation & Local Setup

### 1. Clone & Initialize Environment
Navigate to your working directory and set up a clean Python virtual environment:

```bash
cd F:\Ayush\repomirror-mcp
python -m venv venv

Activate the virtual environment: 
# Windows PowerShell
.\venv\Scripts\Activate.ps1

2. Install Project Dependencies
Install the core networking and parsing libraries required by the MCP engine:

pip install mcp networkx gitpython

🔌 Connecting to Cline (VS Code)
To link RepoMirror with your Cline extension environment, add the server definition block to your global Cline configuration file:
File Path: %APPDATA%\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
Configuration Block:

{
  "mcpServers": {
    "repomirror": {
      "command": "F:\\Ayush\\repomirror-mcp\\venv\\Scripts\\python.exe",
      "args": ["F:\\Ayush\\repomirror-mcp\\server.py"]
    }
  }
}
Note: Ensure all Windows file paths use double backslashes (\\) to maintain valid JSON string escaping rules. 

🔍 Verification & Testing Prompt
Once connected, open a fresh chat inside Cline and test the system end-to-end using this structural health check prompt:
Plaintext
Let's perform a strict structural health check on my repository using our custom tools. 

1. Use the `get_codebase_graph` tool on the `repomirror` server to inspect the latest commit nodes.
2. Run the `analyze_file_functions` tool on `calculator.py` to extract its exact functional line boundaries.
3. Verify that all core arithmetic operations (add, subtract, multiply, divide) are cleanly intact inside the file structures based on the tool's JSON payload.

📝 License
This project is open-source and available under the MIT License.


