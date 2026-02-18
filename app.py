import os
import sys
from flask import Flask, render_template, redirect, url_for

# Проверка версии Python
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Попытка импорта Flask-Dance (может не работать)
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    FLASK_DANCE_AVAILABLE = True
    print("Flask-Dance импортирован успешно")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"Flask-Dance не импортирован: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sdflkjsdflkjsdflkjsdflkjsdflkj")

# Настройка Google OAuth (только если библиотека загружена)
if FLASK_DANCE_AVAILABLE:
    try:
        blueprint = make_google_blueprint(
            client_id=os.environ.get("GOOGLE_CLIENT_ID"),
            client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
            scope=["profile", "email"]
        )
        app.register_blueprint(blueprint, url_prefix="/login")
        print("Google Blueprint зарегистрирован")
    except Exception as e:
        print(f"Ошибка регистрации Google Blueprint: {e}")

@app.route('/')
def home():
    user_info = None
    if FLASK_DANCE_AVAILABLE and google and google.authorized:
        try:
            resp = google.get("/oauth2/v2/userinfo")
            if resp.ok:
                user_info = resp.json()
                print(f"Пользователь вошёл: {user_info.get('email')}")
        except Exception as e:
            print(f"Ошибка получения данных пользователя: {e}")
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
    app.run(host='0.0.0.0', port=port, debug=True)
