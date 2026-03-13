import os
import json
from google.protobuf.json_format import MessageToDict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure API key from environment variable
# If the variable is not set, this will fail (as it should)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

genai.configure(api_key=api_key)

# The list of available tools (your commands)
tools = [
    {
        "function_declarations": [
            {"name": "add_contact", "description": "Add a new contact with details."},
            {"name": "edit_contact", "description": "Edit contact fields."},
            {"name": "add_note", "description": "Add a new note with text."},
            {"name": "search_contact", "description": "Search contacts by name, address, phone, email, or birthday."},
            {"name": "search_note", "description": "Search notes by text or tags."},
            {"name": "delete_note", "description": "Delete a note by ID."},
            {"name": "help", "description": "Show help message."},
            {"name": "exit", "description": "Quit the assistant."}
        ]
    }
]

system_instruction = """
You are a helpful assistant. Always use the following argument names for tool calls:
- For contact name, use 'name'.
- For contact phone, use 'phone' (as a single string).
"""

model = genai.GenerativeModel(
    model_name='models/gemini-3-flash-preview',
    tools=tools,
    system_instruction=system_instruction
)

def get_ai_command(user_query: str) -> dict:
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(user_query)
        
        # Access the function call structure
        function_call = response.candidates[0].content.parts[0].function_call
        
        # FIX: Manual conversion from MapComposite to standard dictionary
        # This iterates over keys/values of the MapComposite object
        args_dict = {key: value for key, value in function_call.args.items()}
        
        return {
            "function": function_call.name,
            "args": args_dict
        }
    except Exception as e:
        return {"text": f"Error: {str(e)}"}