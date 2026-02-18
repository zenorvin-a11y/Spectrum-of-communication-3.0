import os
import sys
from flask import Flask, render_template, redirect, url_for, g

print(f"=== SPECTRUM APPLICATION ===")
print(f"Python version: {sys.version}")

# Импорт Flask-Dance с защитой
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    from flask_dance.consumer import oauth_authorized, oauth_before_login
    from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
    FLASK_DANCE_AVAILABLE = True
    print("✅ Flask-Dance imported successfully")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"⚠️ Flask-Dance not available: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key-for-python-3143")

# Настройка Google OAuth
if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if client_id and client_secret:
        try:
            # Создаём blueprint с явным указанием настроек
            google_blueprint = make_google_blueprint(
                client_id=client_id,
                client_secret=client_secret,
                scope=["profile", "email"],
                redirect_to="home"  # Куда перенаправлять после входа
            )
            app.register_blueprint(google_blueprint, url_prefix="/login")
            print("✅ Google Blueprint registered for Python 3.14.3")
        except Exception as e:
            print(f"❌ Failed to register Google Blueprint: {e}")
    else:
        print("⚠️ Google credentials not set in environment variables")
else:
    print("⚠️ Google login disabled")

@app.route('/')
def home():
    """Главная страница"""
    user_info = None
    
    # Безопасная проверка авторизации
    if FLASK_DANCE_AVAILABLE and google:
        try:
            # Проверяем, авторизован ли пользователь
            if hasattr(google, 'authorized') and google.authorized:
                resp = google.get("/oauth2/v2/userinfo")
                if resp and resp.ok:
                    user_info = resp.json()
                    print(f"✅ User logged in: {user_info.get('email')}")
                else:
                    print("⚠️ Failed to get user info")
            else:
                print("ℹ️ User not logged in")
        except Exception as e:
            print(f"❌ Error in home route: {e}")
    
    return render_template('index.html', user=user_info)

@app.route('/about')
def about():
    """Страница О нас"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Страница Контакты"""
    return render_template('contact.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    if FLASK_DANCE_AVAILABLE and google:
        try:
            # Безопасный выход
            if hasattr(google, 'authorized') and google.authorized:
                return redirect(url_for("google.logout"))
        except Exception as e:
            print(f"❌ Error during logout: {e}")
    return redirect(url_for('home'))

@app.route('/health')
def health():
    """Проверка работоспособности"""
    return {"status": "ok", "python": sys.version.split()[0]}

# Обработчик ошибок для отладки
@app.errorhandler(500)
def internal_error(error):
    print(f"❌ 500 Error: {error}")
    return "Internal Server Error - Check logs", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
