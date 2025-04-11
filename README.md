# NL to ER Diagram

This project allows users to generate Entity-Relationship (ER) diagrams from natural language descriptions using AI. It leverages OpenAI's GPT models to interpret database schema descriptions and outputs ER diagrams in Mermaid.js syntax.

## Features

- **Natural Language Input**: Users can describe their database schema in plain English.
- **Mermaid.js Output**: The application generates ER diagrams in Mermaid.js format, which can be rendered directly in the browser.
- **Interactive Web Interface**: A simple frontend for users to input their descriptions and view the generated diagrams.
- **FastAPI Backend**: A backend API to process user input and generate Mermaid.js code using OpenAI's GPT models.
- **Error Handling**: Provides detailed error messages for invalid input or backend issues.

## How It Works

1. The user enters a natural language description of their database schema in the web interface.
2. The frontend sends the description to the backend API.
3. The backend processes the input using OpenAI's GPT model and generates Mermaid.js code for the ER diagram.
4. The frontend renders the diagram using Mermaid.js and displays the raw Mermaid code.

## Project Structure

- **Frontend**:
  - `index.html`: The main HTML file containing the user interface.
  - `script.js`: Handles user interactions, sends requests to the backend, and renders the Mermaid.js diagrams.

- **Backend**:
  - `main.py`: A FastAPI application that processes user input and generates Mermaid.js code using OpenAI's GPT models.
  - `requirements.txt`: Lists the Python dependencies required for the backend.

- **Sample Input**:
  - `sample prompt`: Contains an example of a natural language description for generating an ER diagram.
  - `I would like to generate an ER diagram w.md`: A detailed example of a database schema description.

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js (optional, for frontend development)
- An OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jpendyala/nl-to-er-diagram.git
   cd nl-to-er-diagram
