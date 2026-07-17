# routes/ai.py
from flask import Blueprint, request, jsonify, render_template
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps
from Server import auth, ollama

ai_bp = Blueprint('AI', __name__, url_prefix='/api')

@ai_bp.route("/ai", methods=["POST"])
@auth.login_required
def handle_ai():
    try:
        content = request.get_json(silent=True)

        if content is None:
            return jsonify({
                "error": "JSON body required"
            }), 400
        user_input = content["prompt"]
    
        response = ollama.chat(model='phi3', messages=[
        {'role': 'system', 'content': 'You are a helpful assistant. Provide extremely concise, short, and direct answers in one or two sentences max.'},
        {'role': 'user', 'content': user_input}
        ])   

        ai_text = response['message']['content']
        
        return jsonify({"response": ai_text}), 200

    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400

    except Exception as e:
        Logger.error(f"Unexpected error in /api/ai: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
    