import os
import sys
from flask import Flask, render_template, redirect, url_for, request

print("="*50)
print("ЗАПУСК ПРИЛОЖЕНИЯ")
print("="*50)

# Проверка версии Python
print(f"Python версия: {sys.version}")

# Проверка переменных окружения (ВАЖНО!)
print("-"*30)
print("ПРОВЕРКА ПЕРЕМЕННЫХ:")
print(f"Все переменные окружения: {list(os.environ.keys())}")
print(f"GOOGLE_CLIENT_ID найден: {'GOOGLE_CLIENT_ID' in os.environ}")
print(f"GOOGLE_CLIENT_SECRET найден: {'GOOGLE_CLIENT_SECRET' in os.environ}")

if 'GOOGLE_CLIENT_ID' in os.environ:
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    print(f"GOOGLE_CLIENT_ID длина: {len(client_id)}")
    print(f"GOOGLE_CLIENT_ID начало: {client_id[:20]}...")
else:
    print("⚠️ GOOGLE_CLIENT_ID ОТСУТСТВУЕТ!")

if 'GOOGLE_CLIENT_SECRET' in os.environ:
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    print(f"GOOGLE_CLIENT_SECRET длина: {len(client_secret)}")
    print(f"GOOGLE_CLIENT_SECRET начало: {client_secret[:10]}...")
else:
    print("⚠️ GOOGLE_CLIENT_SECRET ОТСУТСТВУЕТ!")
print("-"*30)

# Импорт Flask-Dance
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    FLASK_DANCE_AVAILABLE = True
    print("✅ Flask-Dance импортирован")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"❌ Flask-Dance не импортирован: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "spectrum-secret-key-2026-black-blue")

# Настройка Google OAuth (ТОЛЬКО если есть ключи)
GOOGLE_AUTH_ENABLED = False

if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if client_id and client_secret:
        try:
            print("🔧 Настройка Google Blueprint...")
            google_bp = make_google_blueprint(
                client_id=client_id.strip(),
                client_secret=client_secret.strip(),
                scope=["profile", "email"],
                redirect_to="glavnaya"
            )
            app.register_blueprint(google_bp, url_prefix="/login")
            print(f"✅ Google Blueprint зарегистрирован")
            print(f"   Redirect URI: https://spectrum-of-communication-3-0.onrender.com/login/google/authorized")
            GOOGLE_AUTH_ENABLED = True
        except Exception as e:
            print(f"❌ Ошибка настройки Google: {e}")
    else:
        print("⚠️ Google ключи отсутствуют - вход отключён")
else:
    print("⚠️ Flask-Dance не доступен - вход отключён")

print(f"🚀 Статус Google авторизации: {'ВКЛЮЧЕН' if GOOGLE_AUTH_ENABLED else 'ОТКЛЮЧЕН'}")
print("="*50)

@app.route('/')
def glavnaya():
    """Главная страница"""
    user_info = None
    if GOOGLE_AUTH_ENABLED and google and hasattr(google, 'authorized') and google.authorized:
        try:
            resp = google.get("/oauth2/v2/userinfo")
            if resp and resp.ok:
                user_info = resp.json()
                print(f"✅ Пользователь вошёл: {user_info.get('email')}")
        except Exception as e:
            print(f"❌ Ошибка получения данных пользователя: {e}")
    return render_template('glavnaya.html', user=user_info)

@app.route('/o-nas')
def o_nas():
    """Страница О нас"""
    return render_template('o-nas.html')

@app.route('/kontakty')
def kontakty():
    """Страница Контакты"""
    return render_template('kontakty.html')

@app.route('/podderzhka')
def podderzhka():
    """Страница поддержки"""
    return render_template('podderzhka.html')

@app.route('/vyhod')
def vyhod():
    """Выход из аккаунта"""
    if GOOGLE_AUTH_ENABLED and google:
        try:
            from flask_dance.consumer import oauth_logout
            oauth_logout(google)
        except:
            if hasattr(google, 'token'):
                google.token = None
    return redirect(url_for('glavnaya'))

@app.route('/otpravka', methods=['POST'])
def otpravka():
    email = request.form.get('email', '')
    message = request.form.get('message', '')
    print(f"Сообщение от {email}: {message}")
    return redirect(url_for('podderzhka', status='sent'))

@app.route('/health')
def health():
    return {"status": "ok", "python": sys.version.split()[0]}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
