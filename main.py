import os
import logging
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
load_dotenv()  # Load environment variables from .env file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Initialize OpenAI Client ---
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    client = OpenAI(api_key=openai_api_key)
    logger.info("OpenAI client initialized successfully.")
except ValueError as e:
    logger.error(f"Configuration Error: {e}")
    # You might want to exit or handle this differently depending on deployment
    client = None
except Exception as e:
    logger.error(f"Unexpected error initializing OpenAI client: {e}")
    client = None

# --- Pydantic Models ---
class PromptRequest(BaseModel):
    """Request model for receiving the natural language prompt."""
    prompt: str

class ERDiagramResponse(BaseModel):
    """Response model for returning the generated Mermaid code."""
    mermaid_code: str
    explanation: str | None = None # Optional field for LLM reasoning or errors

# --- FastAPI App Instance ---
app = FastAPI(
    title="Natural Language to ER Diagram Tool",
    description="API to convert natural language database descriptions into Mermaid ER diagrams using AI.",
    version="0.1.0",
)

# --- CORS Configuration ---
# Define allowed origins (use "*" for broad development access, be more specific in production)
# For allowing file:/// access, "*" is often the easiest approach during local dev.
origins = [
    "*",
    # If you were serving your frontend from http://localhost:3000, you'd add:
    # "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins allowed to make requests
    allow_credentials=True, # Allow cookies (not strictly needed here, but often useful)
    allow_methods=["*"],    # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],    # Allow all headers (including Content-Type)
)

# --- Helper Function: Construct OpenAI Prompt ---
def create_system_prompt() -> str:
    """Creates the system prompt for the OpenAI API call."""
    return """
You are an expert database designer AI. Your task is to analyze a natural language description of a database schema provided by the user and generate a corresponding Entity-Relationship (ER) diagram using Mermaid.js syntax.

Please generate the ER diagram using Mermaid.js syntax with the following structure:
- Use `erDiagram` as the starting keyword.
- Define entities with their attributes inside curly braces.
- Use `"PK"` and `"FK"` in quotes to mark primary and foreign keys.
- Define relationships between entities with proper cardinality and labels.

Follow these steps precisely:
1. **Identify Entities:** Determine the main entities (tables) mentioned in the description.
2. **Identify Attributes:** For each entity, list its attributes (columns). If possible, infer data types (like int, string, datetime) and identify potential primary keys (PK) and foreign keys (FK). Mark them clearly using the format `"PK"` or `"FK"` in quotes.
3. **Identify Relationships:** Determine the relationships between entities. Specify the cardinality (one-to-one, one-to-many, many-to-many) using Mermaid syntax:
    * One-to-One: `||--||`
    * One-to-Many: `||--o{` (or `}|--o{` if identifying)
    * Many-to-Many: `}o--o{`
    * Zero/One-to-One: `|o--||`
    * Zero/One-to-Many: `|o--o{`
    * Use relationship labels to describe the connection (e.g., `places`, `contains`).
4. **Format Output:** Generate *only* the Mermaid.js code block for the ER diagram.
    * Start the output *exactly* with `erDiagram`.
    * Define entities using the `ENTITY { ... }` syntax.
    * Define attributes within the curly braces, one per line, including type and PK/FK markers in quotes.
    * Define relationships *after* the entity definitions using the format `ENTITY1 <relationship> ENTITY2 : label`.
    * Do NOT include any introductory text, explanations, apologies, markdown formatting (like ```mermaid ... ```), or closing remarks in your response. Only the raw Mermaid code is allowed.

Example Output Format:
erDiagram
    ENTITY1 ||--o{ ENTITY2 : relationship_label
    ENTITY2 ||--|| ENTITY3 : another_relationship_label

    ENTITY1 {
        int attribute1 "PK"
        string attribute2
        datetime attribute3 "FK"
    }
    ENTITY2 {
        int attribute1 "PK"
        string attribute2
    }
    ENTITY3 {
        int attribute1 "PK"
        string attribute2
    }
"""

def create_user_prompt(description: str) -> str:
    """Creates the user prompt containing the specific database description."""
    return f"""
Please generate the Mermaid ER diagram code based on the following database description:

"{description}"
"""

# --- API Endpoint ---
@app.post("/generate-er-diagram",
          response_model=ERDiagramResponse,
          summary="Generate ER Diagram from Natural Language",
          description="Takes a natural language prompt describing a database and returns Mermaid.js code for an ER diagram.")
async def generate_er_diagram(request: PromptRequest = Body(...)):
    """
    Processes the user's natural language prompt and attempts to generate
    a Mermaid ER diagram using the OpenAI API.
    """
    if not client:
        logger.error("OpenAI client is not available.")
        raise HTTPException(status_code=503, detail="AI service is unavailable due to configuration error.")

    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    logger.info(f"Received prompt: {request.prompt[:100]}...") # Log truncated prompt

    system_prompt = create_system_prompt()
    user_prompt = create_user_prompt(request.prompt)

    try:
        logger.info("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4-turbo", # Or "gpt-4", "gpt-3.5-turbo" depending on availability/needs
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2, # Lower temperature for more deterministic output
            max_tokens=1000, # Adjust as needed
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        logger.info("Received response from OpenAI API.")

        # Extract the response content
        mermaid_code = response.choices[0].message.content

        if not mermaid_code:
             logger.warning("OpenAI returned an empty response.")
             raise HTTPException(status_code=500, detail="AI service returned an empty response.")

        # Basic validation/cleanup (optional but recommended)
        mermaid_code = mermaid_code.strip()
        if not mermaid_code.startswith("erDiagram"):
            logger.warning(f"AI response did not start with 'erDiagram'. Response: {mermaid_code[:200]}...")
            # Decide whether to raise error or try to use it anyway
            # For now, we'll return it but log a warning
            explanation = "Warning: AI response format might be incorrect (did not start with 'erDiagram')."
            return ERDiagramResponse(mermaid_code=mermaid_code, explanation=explanation)

        logger.info(f"Successfully generated Mermaid code starting with: {mermaid_code[:50]}...")
        return ERDiagramResponse(mermaid_code=mermaid_code)

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"AI service error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# --- Root Endpoint (Optional) ---
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the NL to ER Diagram API. Use the /docs endpoint for API documentation."}

# --- Run with Uvicorn (for local development) ---
# You would typically run this using: uvicorn main:app --reload
# The following block is mainly for making the script directly runnable (though not standard for FastAPI)
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    # Make sure OPENAI_API_KEY is set before running
    if not os.getenv("OPENAI_API_KEY"):
       print("Error: OPENAI_API_KEY environment variable not set.")
       print("Please create a .env file with OPENAI_API_KEY=your_key or set the environment variable.")
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)