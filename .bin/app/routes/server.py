# routes/server.py
from flask import Blueprint, request, jsonify, render_template
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps
from Server import auth, ollama

server_bp = Blueprint('ai', __name__, url_prefix='')

errors = {
   "connection":{
      "module":{
         "TV":None,
         "Light":None 
      },
   }
}

@server_bp.route("/")
@auth.login_required
def inferance():
   template_path = os.path.join('index.html')

   return render_template(template_path)


@server_bp.route("/api/communicate", methods=["POST"])
@auth.login_required
def communicate_for_errors():
    try:
        data = request.json
        module = data["module"]  
        error = data["error"]   
        err_type = data["type"]  
        action = data.get("action", "report") 

        if action == "reset":
            errors[err_type]["module"][module] = None
            Logger.info(f"Error reset for {module}")
            return jsonify({"status": "success", "message": "Error cleared"}), 200
        else:
            errors[err_type]["module"][module] = error
            return jsonify({"status": "error recorded"}), 200
    
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
        Logger.error(f"Unexpected error in /api/communicate: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
