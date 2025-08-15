# Multi-Agent Google Automation

## Overview

This project implements a **multi-agentic system** capable of automating Google Gmail and Google Calendar tasks through intelligent decision-making. At its core is an **Orchestrator Agent** that routes user requests to specialized agents based on the task type.

- **Mail Agent** → Handles Gmail CRUD operations (Create, Read, Delete) such as sending, reading, deleting, or organizing emails.
- **Calendar Agent** → Handles Google Calendar CRUD operations such as creating events, updating them, reading schedules, or deleting events.

A **Streamlit** frontend allows users to interact with the system in a simple, conversational way, making it possible to manage their Google workspace without manually opening Gmail or Calendar.

---

## Features

- **Orchestrator Agent** that decides whether to call the Mail Agent or Calendar Agent.
- **Mail Agent** to automate Gmail tasks via Google APIs.
- **Calendar Agent** to automate Google Calendar scheduling and management.
- **Google API integration** for Gmail and Calendar (OAuth 2.0).
- **CRUD support** for both email and calendar events.
- **Streamlit-based UI** for a simple chatbot-like interface.
- **Modular utility structure** for easy maintainability and extension.

---

## Project Structure

```
AI-ASSISTANT/
│
├── configs/                  # Configuration files
│   └── config.yaml
│
├── src/
│   ├── utils/                 # Utility functions for agents, APIs, logging, tools
│   │   ├── agent_utils.py
│   │   ├── calendar_api_utils.py
│   │   ├── completion_utils.py
│   │   ├── extraction_utils.py
│   │   ├── logging_utils.py
│   │   └── tools_utils.py
│   │
│   ├── agents.py              # Defines agents
│   ├── api.py                 # API handling
│   ├── engine.py              # Core execution engine
│   ├── orchestrator.py        # Orchestrator logic
│   └── tools.py               # Additional tools
│
├── ui/
│   ├── utils/                 # UI-related utilities
│   └── app.py                 # Streamlit frontend
│
├── venv/                      # Virtual environment
│
├── .env                       # Environment variables
├── .gitignore
├── credentials.json           # Google API credentials
├── token.json                 # Google OAuth token
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
└── config.yaml                # App configuration
```

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/amndzdzdz/ai-assistant.git
cd ai-assistant
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
```

### Configure Google API Credentials

- Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
- Enable **Gmail API** and **Google Calendar API**.
- Download your `credentials.json` and place it in the project root.
- The system will generate `token.json` upon first authentication.

### Run the Streamlit App

```bash
streamlit run ui/app.py
```

---

## Usage

1. Open the Streamlit interface in your browser.
2. Type a request, such as:
   - "Send an email to Alex saying 'Meeting rescheduled to 3 PM'"
   - "Add an event to my calendar for tomorrow at 10 AM titled 'Team Meeting'"
3. The **Orchestrator Agent** decides whether to route the request to the **Mail Agent** or **Calendar Agent**.
4. The appropriate CRUD operation is executed automatically.

---

## 📜 License

This project is licensed under the MIT License.
