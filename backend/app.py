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
# import llm_handler
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

        # --- Placeholder for LLM Processing ---
        # In a real scenario, you would send `image_bytes` or `filepath` to an LLM service
        # llm_response = llm_handler.extract_card_info(image_bytes)
        # For now, return mock data
        mock_llm_response = {
            "card_name": "Pikachu (Mock)",
            "hp": 60,
            "pokemon_type": ["Lightning"],
            "attacks": [
                {"name": "Quick Attack", "cost": ["L"], "damage": "10", "description": "Flip a coin. If heads, this attack does 10 more damage."},
                {"name": "Thunderbolt", "cost": ["L", "C", "C"], "damage": "50", "description": "Discard all Energy attached to Pikachu."}
            ],
            "weakness": {"type": "Fighting", "value": "x2"},
            "set_name": "Mock Set",
            "card_number": "25/100",
            "rarity": "Common"
        }
        # Simulate merging with schema to ensure all fields are present
        processed_data = POKEMON_CARD_SCHEMA.copy()
        processed_data.update(mock_llm_response)

        # --- Placeholder for Database Storage ---
        # db_handler.store_card_data(processed_data)

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