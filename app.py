from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Load BIN database into memory
def load_bin_database():
    bin_db = {}
    bin_file_path = os.path.join(os.path.dirname(__file__), 'bin.txt')
    try:
        with open(bin_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and '|' in line:
                    bin_num, details = line.split('|', 1)
                    bin_db[bin_num.strip()] = details.strip()
    except FileNotFoundError:
        print("bin.txt file not found!")
    return bin_db

bin_db = load_bin_database()

# Valid API key
VALID_API_KEY = "OnyxEnvBot/Gate=Vbv"

@app.route('/check_bin', methods=['GET'])
def check_bin():
    # Get parameters
    api_key = request.args.get('key')
    card_data = request.args.get('format')
    
    # Validate API key
    if api_key != VALID_API_KEY:
        return jsonify({
            "response": "Invalid API key",
            "status": "unauthorized"
        }), 401
    
    # Parse card data
    if not card_data or '|' not in card_data:
        return jsonify({
            "response": "Invalid format. Use: cc|mm|yy|cvv",
            "status": "error"
        }), 400
    
    parts = card_data.split('|')
    if len(parts) != 4:
        return jsonify({
            "response": "Invalid format. Use: cc|mm|yy|cvv",
            "status": "error"
        }), 400
    
    cc, mm, yy, cvv = parts
    
    # Validate card number
    if not cc.isdigit() or len(cc) < 6:
        return jsonify({
            "response": "Invalid card number",
            "status": "error"
        }), 400
    
    # Get BIN (first 6 digits)
    bin_num = cc[:6]
    
    # Check if BIN exists in database
    if bin_num in bin_db:
        response_text = bin_db[bin_num]
        status = "found"
    else:
        response_text = "Unknown"
        status = "Unknown"
    
    # Return full response
    return jsonify({
        "bin": bin_num,
        "response": response_text,
        "status": status
    }), 200

# Health check endpoint for Railway
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "BIN Checker API",
        "usage": "/check_bin?key=OnyxEnvBot/Gate=Vbv&format=cc|mm|yy|cvv",
        "status": "running"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
