# Multi-Agent Google Automation

## Overview

This project implements an **agentic system** which automates Google Gmail and Google Calendar tasks through intelligent decision-making. At its core is an **Agent** that chooses between certain tools to complete the user request.

A **Streamlit** frontend allows users to interact with the system in a simple, conversational way, making it possible to manage their Google workspace without manually opening Gmail or Calendar.

An **MCP-Server** hosts the tools and allows for easy integration of additional agents, as well as a distributed system.

---

## Features

- **Agent** that is implemented by pure python without any frameworks.
- **Google API integration** for Gmail and Calendar (OAuth 2.0).
- **CRUD support** for both email and calendar events.
- **MCP Server** which hosts the tools.
- **Streamlit-based UI** for a simple chatbot-like interface.

---

## Project Structure

```
Agent-Assistant/
├── config/
│   ├── __init__.py                   # Marks this directory as a Python package
│   └── config.yaml                   # Main YAML configuration file
├── src/
│   ├── mcp_server/                   # Server-related logic
│   │   ├── __init__.py               # Package marker
│   │   └── tool_server.py            # Implements tool server functionality
│   ├── utils/                        # Utility/helper functions
│   │   ├── __init__.py               # Package marker
│   │   ├── completion_utils.py       # Utilities for handling completions
│   │   ├── config_loader.py          # Loads and parses configuration
│   │   ├── extraction_utils.py       # Text/data extraction helpers
│   │   ├── google_api_utils.py       # Google API integration functions
│   │   ├── logging_.py               # Custom logging setup
│   │   └── tools_utils.py            # General utilities for tools
│   ├── __init__.py                   # Package marker for src
│   ├── agent.py                      # Main agent implementation
│   └── client.py                     # Client-side logic
├── .env                              # Environment variables (API keys, secrets, etc.)
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
└── setup.py                          # Setup script for installing the package
```

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/amndzdzdz/agent-assistant.git
cd agent-assistant
```

### Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### Configure Google API Credentials

- Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
- Enable **Gmail API** and **Google Calendar API**.
- Download your `credentials.json` and place it in the project root.
- The system will generate `token.json` upon first authentication.

### Run the Streamlit App

```bash
streamlit run src/client.py
```

---

## Usage

1. Open the Streamlit interface in your browser.
2. Type a request, such as:
   - "Send an email to yourfriend@gmail.com saying 'Meeting rescheduled to 3 PM'"
   - "Add an event to my calendar for tomorrow at 10 AM titled 'Team Meeting'"
3. The appropriate CRUD operation is executed automatically.

---

## 📜 License

This project is licensed under the MIT License.
