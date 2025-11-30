from flask import Flask, request, jsonify
# from flask_cors import CORS # Removed to avoid installation issues
import main
import os

app = Flask(__name__)
# CORS(app) # Removed

# Manual CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    try:
        response = main.chatbot_response(user_input)
        
        # Handle tuple/list response (text + image)
        if isinstance(response, (list, tuple)) and len(response) == 2:
            return jsonify({
                "response": response[0],
                "image": response[1]
            })
        else:
            return jsonify({
                "response": response
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/quick_action', methods=['POST'])
def quick_action():
    data = request.json
    action = data.get('action', '')
    
    try:
        # We need to pass a mock chat history as handle_quick_action expects it
        # But for the API, we just want the response text
        # So we can just call chatbot_response directly for most actions
        # Or reuse handle_quick_action logic but extract the response
        
        # Simpler approach: just call chatbot_response with the action text
        # as handle_quick_action basically does that + updates history
        response = main.chatbot_response(action)
        
        if isinstance(response, (list, tuple)) and len(response) == 2:
            return jsonify({
                "response": response[0],
                "image": response[1]
            })
        else:
            return jsonify({
                "response": response
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear():
    try:
        main.clear_chat()
        return jsonify({"status": "success", "message": "Chat cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-image', methods=['POST'])
def save_image():
    try:
        data = request.json
        image_url = data.get('image_url')
        
        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400
            
        # Create directory if not exists
        save_dir = "generated_images"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Generate filename
        import time
        import requests
        filename = f"design_{int(time.time())}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        # Download and save
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return jsonify({
                "status": "success", 
                "message": "Image saved successfully",
                "path": os.path.abspath(filepath)
            })
        else:
            return jsonify({"error": "Failed to download image"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
