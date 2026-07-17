from flask import Blueprint, render_template_string, request, redirect, url_for, session
from werkzeug.security import check_password_hash
import os
from functools import wraps

auth_bp = Blueprint('auth', __name__)

LOGIN_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>Edge-AI Home Monitoring — Login</title>
  <style>
    body { font-family: system-ui, sans-serif; background:#0f1115; color:#eee;
           display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
    .card { background:#181b22; padding:2rem 2.5rem; border-radius:12px; width:280px; }
    h1 { font-size:1.1rem; margin-bottom:1.2rem; }
    input { width:100%; padding:.6rem; margin-bottom:.8rem; border-radius:6px;
            border:1px solid #333; background:#0f1115; color:#eee; box-sizing:border-box; }
    button { width:100%; padding:.6rem; border:none; border-radius:6px;
             background:#4f8cff; color:#fff; font-weight:600; cursor:pointer; }
    .error { color:#ff6b6b; font-size:.85rem; margin-bottom:.8rem; }
  </style>
</head>
<body>
  <form class="card" method="POST">
    <h1>🔒 Edge-AI Home Hub</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <input type="text" name="username" placeholder="Username" required autofocus>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
"""

class Auth:
    def login_required(self, view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("authenticated"):
                if request.path.startswith("/api/"):
                    return {"error": "Authentication required"}, 401
                return redirect(url_for("auth.login", next=request.path))
            return view_func(*args, **kwargs)
        return wrapped
    
auth = Auth()

ADMIN_USERNAME = os.environ.get("USER", "admin")
ADMIN_PASSWORD = os.environ.get("PASSWORD", "")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        valid_user = username == ADMIN_USERNAME
        valid_pass = bool(ADMIN_PASSWORD) and check_password_hash(ADMIN_PASSWORD, password)

        if valid_user and valid_pass:
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            return redirect(request.args.get("next") or "/")

        error = "Invalid username or password."

    return render_template_string(LOGIN_TEMPLATE, error=error)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))