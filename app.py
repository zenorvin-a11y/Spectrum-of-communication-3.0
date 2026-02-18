import os
import sys
from flask import Flask, render_template, redirect, url_for, request

print(f"=== СПЕКТР ОБЩЕНИЯ === Версия 3.0 (Черно-голубая)")
print(f"Python: {sys.version.split()[0]}")

# Импорт Flask-Dance
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    FLASK_DANCE_AVAILABLE = True
    print("✅ Google авторизация доступна")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"⚠️ Google авторизация недоступна: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "spectrum-secret-key-2026-black-blue")

# Настройка Google OAuth (ИСПРАВЛЕНО)
if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if client_id and client_secret:
        try:
            # ВАЖНО: явно указываем redirect_to и authorization_url
            google_bp = make_google_blueprint(
                client_id=client_id,
                client_secret=client_secret,
                scope=["profile", "email"],
                redirect_to="glavnaya",  # Куда идти после входа
                login_url="/login/google",  # URL для входа
                authorized_url="/login/google/authorized"  # URL для редиректа
            )
            app.register_blueprint(google_bp, url_prefix="/login")
            print("✅ Google вход настроен")
            print(f"   Redirect URI: https://spectrum-of-communication-3-0.onrender.com/login/google/authorized")
        except Exception as e:
            print(f"❌ Ошибка настройки Google: {e}")
    else:
        print("⚠️ Ключи Google не найдены в окружении")

# Главная страница
@app.route('/')
def glavnaya():
    """Главная страница сайта"""
    user_info = None
    if FLASK_DANCE_AVAILABLE and google:
        try:
            # Проверяем авторизацию
            if hasattr(google, 'authorized') and google.authorized:
                resp = google.get("/oauth2/v2/userinfo")
                if resp and resp.ok:
                    user_info = resp.json()
                    print(f"✅ Пользователь вошел: {user_info.get('email')}")
        except Exception as e:
            print(f"Ошибка получения данных пользователя: {e}")
    return render_template('glavnaya.html', user=user_info)

# О нас
@app.route('/o-nas')
def o_nas():
    """Страница О нас"""
    return render_template('o-nas.html')

# Контакты
@app.route('/kontakty')
def kontakty():
    """Страница Контакты"""
    return render_template('kontakty.html')

# Поддержка
@app.route('/podderzhka')
def podderzhka():
    """Страница поддержки"""
    return render_template('podderzhka.html')

# Выход
@app.route('/vyhod')
def vyhod():
    """Выход из аккаунта"""
    if FLASK_DANCE_AVAILABLE and google:
        try:
            # Правильный выход из Flask-Dance
            from flask_dance.consumer import oauth_logout
            oauth_logout(google)
        except:
            # Если не получается, просто забываем токен
            if hasattr(google, 'token'):
                google.token = None
    return redirect(url_for('glavnaya'))

# Обработка формы обратной связи (заглушка)
@app.route('/otpravka', methods=['POST'])
def otpravka():
    email = request.form.get('email', '')
    message = request.form.get('message', '')
    print(f"Сообщение от {email}: {message}")
    return redirect(url_for('podderzhka', status='sent'))

# Проверка работоспособности
@app.route('/health')
def health():
    return {"status": "ok", "python": sys.version.split()[0]}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
