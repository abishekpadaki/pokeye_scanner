# Pokeye Scanner

Automated Pokémon card collection tracking using image recognition and LLMs.

## Project Overview

This project captures images of Pokémon cards, extracts structured information using a Large Language Model (LLM) like Gemini, OpenAI, or Anthropic, and stores this information in a PostgreSQL database. It features a simple, mobile-friendly web frontend for card scanning.

## Features

-   **Image Capture**: Uses device camera via a web interface to capture images of Pokémon cards.
-   **Information Extraction**: Sends captured images to an LLM API (e.g., Gemini) to extract details like card name, HP, type, attacks, etc., in a structured JSON format.
-   **Database Storage**: Stores the extracted information in a PostgreSQL database.
-   **Frontend**: Simple HTML/CSS/JS interface for mobile browsers.

## Tech Stack

-   **Frontend**: HTML, CSS, JavaScript
-   **Backend**: Python (Flask)
-   **LLM**: Google Gemini (initial), OpenAI, or Anthropic
-   **Database**: PostgreSQL

## Project Structure

```
pokeye_scanner/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   └── llm_handler.py  # (Module for LLM interaction)
│   └── db_handler.py   # (Module for DB interaction)
├── database/
│   └── schema.sql
└── README.md
```

## Setup and Running

(Instructions to be added as development progresses)

### Prerequisites

-   Python 3.x
-   Node.js (for potential frontend tools, though not strictly necessary for this simple version)
-   PostgreSQL server
-   API Key for an LLM (e.g., Google Gemini API Key)

### Backend Setup

1.  Navigate to the `backend` directory.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Create a `.env` file from `.env.example` and fill in your API keys and database credentials.
6.  Run the Flask app: `flask run` (or `python app.py`)

### Database Setup

1.  Ensure your PostgreSQL server is running.
2.  Create a database (e.g., `pokeye_db`).
3.  Connect to your database and run the script in `database/schema.sql` to create the necessary tables.

### Frontend

1.  Open `frontend/index.html` in your web browser (preferably a mobile browser or using mobile emulation in a desktop browser). 