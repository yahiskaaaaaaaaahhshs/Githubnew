from flask import Flask, request, jsonify, abort
import os
from functools import wraps

app = Flask(__name__)

# API Configuration
CORRECT_API_KEY = "yashikaaa"

def load_bin_data():
    bin_data = {}
    file_path = os.path.join(os.path.dirname(__file__), 'bin.txt')
    if not os.path.exists(file_path):
        return bin_data
        
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 3:
                bin_number = parts[0].strip()
                status = parts[1].strip()
                description = parts[2].strip()
                bin_data[bin_number] = {
                    'status': status,
                    'description': description
                }
    return bin_data

bin_db = load_bin_data()

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key') or request.headers.get('X-API-KEY')
        if api_key != CORRECT_API_KEY:
            abort(401, description="Invalid API key. Use ?key=yashikaaa")
        return view_function(*args, **kwargs)
    return decorated_function

@app.route('/bin/<bin_number>', methods=['GET'])
@require_api_key
def lookup_bin(bin_number):
    # Exact match check
    if bin_number in bin_db:
        return jsonify({
            'bin': bin_number,
            'status': bin_db[bin_number]['status'],
            'description': bin_db[bin_number]['description'],
            'success': True
        })
    
    # Prefix match check (first 6 digits)
    for stored_bin in bin_db:
        if bin_number.startswith(stored_bin):
            return jsonify({
                'bin': bin_number,
                'status': bin_db[stored_bin]['status'],
                'description': bin_db[stored_bin]['description'],
                'success': True,
                'matched_prefix': stored_bin
            })
    
    return jsonify({
        'bin': bin_number,
        'success': False,
        'message': 'BIN not found'
    }), 404

@app.route('/')
def home():
    return """
    BIN Lookup API<br>
    Usage: /bin/&lt;bin_number&gt;?key=yashikaaa<br>
    Example: <a href="/bin/400005?key=yashikaaa">/bin/400005?key=yashikaaa</a>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
