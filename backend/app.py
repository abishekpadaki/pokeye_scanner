import os
import base64
import uuid
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv() # Load environment variables from .env file

app = Flask(__name__, static_folder='../frontend')

# Configuration
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- LLM and DB Handlers (to be implemented later) ---
import llm_handler # Updated: Import the llm_handler
# import db_handler

# --- JSON structure for Pokémon card (example) ---
POKEMON_CARD_SCHEMA = {
    "card_name": "Unknown",
    "hp": None,
    "pokemon_type": [],
    "evolves_from": None,
    "attacks": [
        {
            "name": "Attack 1",
            "cost": [],
            "damage": "",
            "description": ""
        }
    ],
    "weakness": {
        "type": None,
        "value": None
    },
    "resistance": {
        "type": None,
        "value": None
    },
    "retreat_cost": [],
    "card_number": "",
    "rarity": "",
    "illustrator": "",
    "set_name": "",
    "additional_info": ""
}

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # Serves other files like style.css, script.js from frontend directory
    return send_from_directory(app.static_folder, path)

@app.route('/api/scan-card', methods=['POST'])
def scan_card():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400

    image_data_url = data['image']
    
    try:
        # Decode the base64 image data
        # The data URL format is "data:image/[type];base64,[data]"
        header, encoded = image_data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        
        # Optional: Save the image to a file for inspection/debugging
        image_format = header.split('/')[1].split(';')[0] # e.g. jpeg, png
        filename = f"scan_{uuid.uuid4()}.{image_format}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create an Image object from bytes for potential processing or saving
        image = Image.open(io.BytesIO(image_bytes))
        image.save(filepath) # Save the image
        
        app.logger.info(f"Image received and saved to {filepath}")

        # --- LLM Processing ---
        llm_response = llm_handler.extract_card_info_gemini(image_bytes)

        if 'error' in llm_response:
            app.logger.error(f"LLM processing failed: {llm_response['error']}")
            # Send back the LLM error and potentially the raw response if available
            error_detail = {"error": f"LLM processing error: {llm_response['error']}"}
            if "raw_response" in llm_response:
                error_detail["llm_raw_response"] = llm_response["raw_response"]
            return jsonify(error_detail), 500

        # Merge LLM response with our schema to ensure all fields are present
        # and to maintain a consistent structure.
        processed_data = POKEMON_CARD_SCHEMA.copy() 
        # We need to be careful here. If the LLM returns a field with a valid value (e.g. hp: 0),
        # and our schema has hp: None, we want the LLM's value.
        # However, if the LLM omits a field, we want our schema's default.
        # A simple update might not be enough if the LLM returns partial sub-objects (e.g. only attack name).
        # For now, let's do a smart update.
        
        for key, schema_default_value in POKEMON_CARD_SCHEMA.items():
            if key in llm_response and llm_response[key] is not None:
                # If the key is in LLM response and not None, use LLM's value
                if isinstance(schema_default_value, dict) and isinstance(llm_response[key], dict):
                    # For nested dicts (like weakness, resistance), merge them
                    processed_data[key] = schema_default_value.copy()
                    processed_data[key].update(llm_response[key])
                elif isinstance(schema_default_value, list) and isinstance(llm_response[key], list):
                    # For lists (like attacks, pokemon_type), ensure items are structured if needed
                    # For attacks, the schema has a list of dicts
                    if key == "attacks" and llm_response[key]:
                        updated_attacks = []
                        attack_schema = POKEMON_CARD_SCHEMA["attacks"][0] if POKEMON_CARD_SCHEMA["attacks"] else {}
                        for llm_attack in llm_response[key]:
                            if isinstance(llm_attack, dict):
                                current_attack = attack_schema.copy()
                                current_attack.update(llm_attack)
                                updated_attacks.append(current_attack)
                            else:
                                updated_attacks.append(llm_attack) # or handle error
                        processed_data[key] = updated_attacks
                    else:
                        processed_data[key] = llm_response[key]
                else:
                    processed_data[key] = llm_response[key]
            # Else, it keeps the default from POKEMON_CARD_SCHEMA.copy()

        app.logger.info(f"LLM Processed Data: {processed_data}")

        # --- Placeholder for Database Storage ---
        # db_handler.store_card_data(processed_data, filename, llm_response)

        return jsonify(processed_data)

    except base64.binascii.Error as e:
        app.logger.error(f"Base64 decoding error: {e}")
        return jsonify({"error": "Invalid base64 image data"}), 400
    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Make sure to set FLASK_ENV=development for debug mode in .env or here
    # app.run(debug=True, host='0.0.0.0') # host='0.0.0.0' makes it accessible on network
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true", 
            host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"),
            port=int(os.environ.get("FLASK_RUN_PORT", 5000))) 