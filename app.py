from flask import Flask, render_template, request, redirect, session
import os, json, hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = "darkbox-secret-key-change-in-production"

def required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
@required
def index():
    return render_template("index.html", title="Home")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username", "").strip()
        password = data.get("password", "")
        if not username or not password:
            return "Username and password required", 400
        users = {}
        if os.path.exists("users.json"):
            with open("users.json") as f:
                users = json.load(f)
        if username not in users:
            return "Invalid credentials", 401
        if users[username] != hashlib.sha256(password.encode()).hexdigest():
            return "Invalid credentials", 401
        session["logged_in"] = True
        session["username"] = username
        return redirect("/")
    return render_template("login.html", title="Login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        username = data.get("username", "").strip()
        password = data.get("password", "")
        if not username or not password:
            return "Username and password required", 400
        users = {}
        if os.path.exists("users.json"):
            with open("users.json") as f:
                users = json.load(f)
        if username in users:
            return "Username already exists", 400
        users[username] = hashlib.sha256(password.encode()).hexdigest()
        with open("users.json", "w") as f:
            json.dump(users, f)
        return redirect("/login")
    return render_template("register.html", title="Register")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/youtube")
@required
def youtube():
    category = request.args.get("category", "all")
    q = request.args.get("q", "")
    return render_template("youtube.html", title="YouTube", category=category, query=q)

@app.route("/youtube/play/<video_id>")
@required
def youtube_play(video_id):
    return render_template(
        "youtube_play.html",
        video_id=video_id,
        title=request.args.get("title", "YouTube Video")
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
