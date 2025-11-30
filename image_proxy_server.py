"""
Simple Proxy Server for Hugging Face API
Solves CORS issues
"""

from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# Manual CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

HF_API_KEY = "hf_YOUR_API_KEY_HERE" # Replace with your actual key if needed
# HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5" # 410 Gone
HF_API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"

@app.route('/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        # Call Hugging Face API
        response = requests.post(
            HF_API_URL,
            headers={
                'Authorization': f'Bearer {HF_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'inputs': f'interior design, {prompt}, professional photography, 8k, detailed, high quality'
            }
        )
        
        if response.status_code == 200:
            # Return image directly
            return Response(response.content, mimetype='image/png')
        else:
            return jsonify({'error': response.text}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 Image Generation Proxy Server")
    print("Running on http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=False)

