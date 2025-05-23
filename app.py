from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

# Load BIN database into memory
def load_bin_database():
    bin_db = {}
    with open('bin.txt', 'r') as file:
        for line in file:
            line = line.strip()
            if line and '|' in line:
                bin_num, details = line.split('|', 1)
                bin_db[bin_num] = details.strip()
    return bin_db

bin_db = load_bin_database()

# Valid API key
VALID_API_KEY = "yashikaaa"

def validate_card_details(cc, mm, yy, cvv):
    """Validate card details format"""
    if not (cc.isdigit() and len(cc) >= 6):
        return False, "Invalid card number"
    if not (mm.isdigit() and 1 <= int(mm) <= 12):
        return False, "Invalid month"
    if not (yy.isdigit() and len(yy) in [2,4]):
        return False, "Invalid year"
    if not (cvv.isdigit() and len(cvv) in [3,4]):
        return False, "Invalid CVV"
    return True, ""

@app.route('/check_bin', methods=['GET'])
def check_bin():
    # Get parameters
    api_key = request.args.get('key')
    card_data = request.args.get('format')
    
    # Validate API key
    if api_key != VALID_API_KEY:
        return jsonify({
            "error": "Invalid API key",
            "status": "unauthorized"
        }), 401
    
    # Parse card data
    if not card_data or '|' not in card_data:
        return jsonify({
            "error": "Invalid format",
            "message": "Format should be cc|mm|yy|cvv or cc|mm|yyyy|cvv",
            "status": "invalid_format"
        }), 400
    
    parts = card_data.split('|')
    if len(parts) != 4:
        return jsonify({
            "error": "Invalid format",
            "message": "Format should be cc|mm|yy|cvv or cc|mm|yyyy|cvv",
            "status": "invalid_format"
        }), 400
    
    cc, mm, yy, cvv = parts
    is_valid, validation_msg = validate_card_details(cc, mm, yy, cvv)
    if not is_valid:
        return jsonify({
            "error": validation_msg,
            "status": "invalid_card_details"
        }), 400
    
    # Extract BIN (first 6 digits)
    bin_num = cc[:6]
    
    # Check for exact BIN match in database
    if bin_num in bin_db:
        details = bin_db[bin_num]
        # Determine status from emoji
        status = "success" if "✅" in details else "failed"
        return jsonify({
            "card": card_data,
            "bin": bin_num,
            "response": details,
            "status": status,
            "match": "exact"
        })
    else:
        # Check for partial matches (optional)
        partial_matches = {k: v for k, v in bin_db.items() if k.startswith(bin_num[:4])}
        if partial_matches:
            return jsonify({
                "card": card_data,
                "bin": bin_num,
                "response": "No exact BIN match",
                "similar_bins": partial_matches,
                "status": "partial_match"
            })
        return jsonify({
            "card": card_data,
            "bin": bin_num,
            "response": "BIN not found in database",
            "status": "unknown",
            "match": "none"
        })

@app.route('/')
def home():
    return "BIN Checker API is running. Use /check_bin endpoint with your API key."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
