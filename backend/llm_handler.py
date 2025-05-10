import os
import google.generativeai as genai
import json
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expected JSON structure for Pokémon card information (ensure this matches app.py and schema.sql indirectly)
POKEMON_CARD_SCHEMA_TEXT = '''{
    "card_name": "String",
    "hp": "Integer or null",
    "pokemon_type": ["List of strings"],
    "evolves_from": "String or null",
    "attacks": [
        {
            "name": "String",
            "cost": ["List of strings (energy types)"],
            "damage": "String (e.g., \"20+\", \"100\") or null",
            "description": "String"
        }
    ],
    "weakness": {
        "type": "String (energy type) or null",
        "value": "String (e.g., \"x2\") or null"
    },
    "resistance": {
        "type": "String (energy type) or null",
        "value": "String (e.g., \"-30\") or null"
    },
    "retreat_cost": ["List of strings (energy types)"],
    "card_number": "String (e.g., \"63/102\")",
    "rarity": "String (e.g., \"Common\", \"Holo Rare\")",
    "illustrator": "String",
    "set_name": "String",
    "additional_info": "String (for abilities, Pokédex entries, flavor text, etc.)"
}'''

def extract_card_info_gemini(image_bytes: bytes) -> dict:
    """
    Extracts Pokémon card information from an image using Google Gemini API.

    Args:
        image_bytes: Bytes of the Pokémon card image.

    Returns:
        A dictionary containing the extracted card information,
        or a dictionary with an error message if extraction fails.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment variables.")
        return {"error": "API key not configured."}

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return {"error": f"Failed to configure Gemini API: {str(e)}"}

    # For vision model, prepare the image part
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Ensure image is in a compatible format (e.g., PNG, JPEG)
        # Gemini API supports JPEG, PNG, WEBP, HEIC, HEIF
        # If the input could be other formats, convert it.
        # For now, assume it's one of these.
        # Example: image.save(img_byte_arr, format='PNG')
    except Exception as e:
        logger.error(f"Invalid image bytes or format: {e}")
        return {"error": f"Invalid image data: {str(e)}"}

    # Using gemini-1.5-flash as it's generally faster and good for this kind of task.
    # You could also use gemini-pro-vision if flash is not available or for potentially higher accuracy.
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""Analyze the provided image of a Pokémon card.
Extract the following information and return it as a valid JSON object.
Ensure the JSON strictly adheres to the structure and data types described below.
If a field is not present on the card or cannot be determined, use null or an empty list/string as appropriate according to the schema.

JSON Schema:
{POKEMON_CARD_SCHEMA_TEXT}

Important Notes:
- For 'pokemon_type', 'attacks[].cost', and 'retreat_cost', provide a list of strings representing energy types (e.g., ["Grass", "Colorless"]).
- For 'hp', if present, it should be an integer.
- For 'attacks', provide a list of attack objects. If there are no attacks, use an empty list [].
- 'additional_info' can capture any other relevant text like Pokémon Powers, Abilities, Pokédex entries, or flavor text not covered by other fields.
- The entire output MUST be a single JSON object. Do not include any text before or after the JSON object.
- Be careful with escape characters within strings in the JSON.
"""

    contents = [
        prompt,
        image 
    ]

    logger.info("Sending request to Gemini API...")
    try:
        response = model.generate_content(contents)
        
        # Attempt to clean and parse the JSON response
        raw_response_text = response.text.strip()
        logger.info(f"Raw LLM response: {raw_response_text[:500]}...") # Log a snippet

        # Sometimes LLMs wrap JSON in ```json ... ``` or just ``` ... ```
        if raw_response_text.startswith("```json"):
            raw_response_text = raw_response_text[7:-3].strip()
        elif raw_response_text.startswith("```"):
            raw_response_text = raw_response_text[3:-3].strip()
            
        card_data = json.loads(raw_response_text)
        logger.info("Successfully parsed JSON response from LLM.")
        # You might want to validate this card_data against the POKEMON_CARD_SCHEMA here
        # to ensure all expected keys are present, perhaps with default values.
        return card_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM response: {e}")
        logger.error(f"LLM Raw Text was: {response.text}")
        return {"error": "Failed to parse LLM response as JSON.", "raw_response": response.text}
    except Exception as e:
        logger.error(f"Error during Gemini API call or processing: {e}")
        # Check if there's safety feedback or other specific details in the response
        # For example, response.prompt_feedback could indicate issues
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
             logger.error(f"Content blocked. Reason: {response.prompt_feedback.block_reason_message}")
             return {"error": f"Content blocked by API. Reason: {response.prompt_feedback.block_reason_message}"}
        return {"error": f"An error occurred while communicating with the LLM: {str(e)}"}

if __name__ == '__main__':
    # This is a simple test. Replace 'path/to/your/card_image.jpg' with an actual image path.
    # Ensure your GOOGLE_API_KEY is set in your environment.
    logger.info("Starting LLM Handler standalone test.")
    try:
        # Create a dummy image for testing if you don't have one handy
        # This requires Pillow to be installed (pip install Pillow)
        # from PIL import Image, ImageDraw
        # img = Image.new('RGB', (200, 300), color = 'red')
        # d = ImageDraw.Draw(img)
        # d.text((10,10), "Test Card", fill=(255,255,0))
        # img_byte_arr = io.BytesIO()
        # img.save(img_byte_arr, format='PNG')
        # test_image_bytes = img_byte_arr.getvalue()
        
        # Or load an actual image:
        # with open('path/to/your/pokemon_card_image.jpg', 'rb') as f:
        #    test_image_bytes = f.read()

        # For now, we'll just indicate it needs a real image or API key.
        if not os.getenv("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY not set. LLM call will fail.")
            print("Please set your GOOGLE_API_KEY environment variable to test.")
        else:
            # To run this test, you'd need an actual image.
            # For example, if you have 'test_card.png' in the same directory:
            # with open('test_card.png', 'rb') as f:
            #     test_image_bytes = f.read()
            #     extracted_info = extract_card_info_gemini(test_image_bytes)
            #     print("\n--- Extracted Information ---")
            #     print(json.dumps(extracted_info, indent=2))
            #     print("-----------------------------")
            print("LLM Handler test requires a sample image and a valid API key.")
            print("To test, uncomment the image loading section and provide an image path.")
            
    except FileNotFoundError:
        logger.error("Test image file not found. Please provide a valid path.")
        print("Test image file not found. Please provide a valid path in the __main__ block.")
    except Exception as e:
        logger.error(f"Error in standalone test: {e}")
        print(f"An error occurred during the test: {e}") 