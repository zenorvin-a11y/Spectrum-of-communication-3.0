import os
import sys
from flask import Flask, render_template, redirect, url_for

print(f"Python version: {sys.version}")
print(f"Starting application...")

# Импорт Flask-Dance с обработкой ошибок
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    FLASK_DANCE_AVAILABLE = True
    print("Flask-Dance imported successfully")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"Flask-Dance not available: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key-change-this")

# Google OAuth (только если библиотека есть и есть ключи)
if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if client_id and client_secret:
        try:
            blueprint = make_google_blueprint(
                client_id=client_id,
                client_secret=client_secret,
                scope=["profile", "email"]
            )
            app.register_blueprint(blueprint, url_prefix="/login")
            print("Google Blueprint registered")
        except Exception as e:
            print(f"Failed to register Google Blueprint: {e}")
    else:
        print("Google credentials not set in environment variables")
else:
    print("Flask-Dance not available - Google login disabled")

@app.route('/')
def home():
    user_info = None
    if FLASK_DANCE_AVAILABLE and google and google.authorized:
        try:
            resp = google.get("/oauth2/v2/userinfo")
            if resp.ok:
                user_info = resp.json()
        except Exception as e:
            print(f"Error getting user info: {e}")
    return render_template('index.html', user=user_info)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    if FLASK_DANCE_AVAILABLE and google:
        return redirect(url_for("google.logout"))
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
