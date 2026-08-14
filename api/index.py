from flask import Flask, request, jsonify
import requests
import os
import logging
import json
from datetime import datetime

app = Flask(__name__)

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
BASE_URL = "https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan"

# Token ko environment variable se lo, agar nahi hai toh hardcoded use karo
BEARER_TOKEN = os.getenv("TURTLEMINT_TOKEN", "f13517d5a59b689d16aa30c528ccaf7801f823b0f5548f65d6d3793270cfe8d628cea877289aba166e5425c31cfc7a0b")

# ==================== HEADERS ====================
HEADERS = {
    "x-broker": "turtlemint",
    "x-instana-l": "1,correlationType=web;correlationId=9f7a05debcb2c4c8",
    "x-instana-s": "9f7a05debcb2c4c8",
    "authorization": f"Bearer {BEARER_TOKEN}",
    "x-provider": "signzy",
    "sec-ch-ua-platform": '"Android"',
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?1",
    "x-partner-id": "undefined",
    "x-tenant": "turtlemint",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36",
    "content-type": "application/json",
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://turtlemintloans.com/products/personal-loan/customer/MULTI/apply",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
}

COOKIES = {
    "PLAY_SESSION": "b9491e006d593b36da5043bf7febea23a8f2b906-host=http%3A%2F%2Fturtlemintloans.com&X-Forwarded-For=152.59.185.172&broker=turtlemint",
    "category": "partner",
}

# ==================== VALIDATION ====================
def validate_pan(pan):
    """Validate PAN card format"""
    if not pan or len(pan) != 10:
        return False
    if not pan[:5].isalpha():
        return False
    if not pan[5:9].isdigit():
        return False
    if not pan[9].isalpha():
        return False
    return True

# ==================== ROUTES ====================
@app.route("/")
def home():
    return jsonify({
        "api": "PAN to Info API",
        "version": "1.0.0",
        "status": "active",
        "deployed_on": "Vercel",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "API Information",
            "/health": "Health Check",
            "/pan-info": {
                "method": "GET",
                "params": {"pan": "10-digit PAN number"},
                "example": "/pan-info?pan=JCZPS4827P"
            }
        }
    })

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "pan-info-api",
        "environment": "production",
        "timestamp": datetime.now().isoformat(),
        "token_configured": bool(BEARER_TOKEN)
    })

@app.route("/pan-info", methods=["GET"])
def pan_info():
    try:
        # Get PAN from query params
        pan = request.args.get("pan", "").strip().upper()
        
        # Validate PAN
        if not validate_pan(pan):
            return jsonify({
                "success": False,
                "error": "Invalid PAN format",
                "message": "PAN must be 10 characters: first 5 letters, next 4 digits, last 1 letter",
                "example": "JCZPS4827P",
                "provided": pan
            }), 400
        
        # Make API request
        url = f"{BASE_URL}?pan={pan}"
        logger.info(f"Fetching data for PAN: {pan}")
        
        resp = requests.get(
            url,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=15
        )
        
        # Handle response
        if resp.status_code == 200:
            try:
                data = resp.json()
                return jsonify({
                    "success": True,
                    "pan": pan,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Invalid JSON response from upstream",
                    "raw_response": resp.text[:500]
                }), 500
        else:
            logger.warning(f"Upstream error {resp.status_code} for PAN: {pan}")
            return jsonify({
                "success": False,
                "error": "Upstream service error",
                "status_code": resp.status_code,
                "message": resp.text[:500] if resp.text else "No response body",
                "timestamp": datetime.now().isoformat()
            }), resp.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Request timeout",
            "message": "Upstream service took too long to respond"
        }), 504
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "Connection error",
            "message": "Could not connect to upstream service"
        }), 503
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/pan-info"]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "message": "Only GET requests are supported"
    }), 405

# ==================== MAIN ====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
