from flask import Flask, request, jsonify
from flask_cors import CORS
import main
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

if __name__ == '__main__':
    print("🚀 Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
