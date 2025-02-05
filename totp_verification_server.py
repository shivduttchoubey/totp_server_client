from flask import Flask, request, jsonify
import pyotp
import json
from functools import wraps
import time

app = Flask(__name__)

# In-memory storage for demonstration (in production, use a secure database)
secrets_store = {}

def rate_limit(max_requests=3, window=60):
    """Basic rate limiting decorator"""
    request_history = {}
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client IP
            client = request.remote_addr
            now = time.time()
            
            # Initialize or clean old requests
            request_history.setdefault(client, [])
            request_history[client] = [t for t in request_history[client] if now - t < window]
            
            # Check rate limit
            if len(request_history[client]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            # Add request timestamp
            request_history[client].append(now)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/register', methods=['POST'])
@rate_limit()
def register():
    """Register a new TOTP secret"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        secret = data.get('secret')
        
        if not user_id or not secret:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Validate secret
        try:
            pyotp.TOTP(secret).now()
        except Exception:
            return jsonify({"error": "Invalid secret"}), 400
            
        secrets_store[user_id] = secret
        
        return jsonify({"message": "Registration successful"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/verify', methods=['POST'])
@rate_limit()
def verify():
    """Verify a TOTP code"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        code = data.get('code')
        
        if not user_id or not code:
            return jsonify({"error": "Missing required fields"}), 400
            
        secret = secrets_store.get(user_id)
        if not secret:
            return jsonify({"error": "User not found"}), 404
            
        # Create TOTP object
        totp = pyotp.TOTP(secret)
        
        # Verify code with ±1 interval tolerance
        if totp.verify(code, valid_window=1):
            return jsonify({"message": "Code verified successfully"}), 200
        else:
            return jsonify({"error": "Invalid code"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')