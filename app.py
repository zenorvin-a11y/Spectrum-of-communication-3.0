import os
import sys
import traceback
from flask import Flask, render_template, redirect, url_for, request

print("="*50)
print("ЗАПУСК ПРИЛОЖЕНИЯ (ДИАГНОСТИЧЕСКАЯ ВЕРСИЯ)")
print("="*50)

print(f"Python версия: {sys.version}")
print(f"GOOGLE_CLIENT_ID найден: {'GOOGLE_CLIENT_ID' in os.environ}")
print(f"GOOGLE_CLIENT_SECRET найден: {'GOOGLE_CLIENT_SECRET' in os.environ}")

# Импорт Flask-Dance
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    from flask_dance.consumer import oauth_authorized
    FLASK_DANCE_AVAILABLE = True
    print("✅ Flask-Dance импортирован")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"❌ Flask-Dance не импортирован: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "spectrum-secret-key-2026")

# Настройка Google OAuth
GOOGLE_AUTH_ENABLED = False
if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    
    if client_id and client_secret:
        try:
            print("🔧 Настройка Google Blueprint...")
            google_bp = make_google_blueprint(
                client_id=client_id,
                client_secret=client_secret,
                scope=["profile", "email"],
                redirect_to="glavnaya"
            )
            app.register_blueprint(google_bp, url_prefix="/login")
            print("✅ Google Blueprint зарегистрирован")
            GOOGLE_AUTH_ENABLED = True
        except Exception as e:
            print(f"❌ Ошибка настройки Google: {e}")
            traceback.print_exc()
    else:
        print("⚠️ Google ключи отсутствуют")

print(f"🚀 Статус Google: {'ВКЛ' if GOOGLE_AUTH_ENABLED else 'ВЫКЛ'}")

# Обработчик успешного входа
@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    print("✅ УСПЕШНЫЙ ВХОД ЧЕРЕЗ GOOGLE!")
    print(f"Токен получен: {token is not None}")
    if token:
        print(f"Token keys: {token.keys() if hasattr(token, 'keys') else 'no keys'}")

@app.route('/')
def glavnaya():
    """Главная страница"""
    user_info = None
    error_info = None
    
    try:
        if GOOGLE_AUTH_ENABLED and google and hasattr(google, 'authorized') and google.authorized:
            print("🔄 Получение данных пользователя...")
            resp = google.get("/oauth2/v2/userinfo")
            print(f"Статус ответа: {resp.status_code if resp else 'No response'}")
            
            if resp and resp.ok:
                user_info = resp.json()
                print(f"✅ Данные получены: {user_info.get('email')}")
            else:
                error_info = f"Ошибка получения данных: {resp.status_code if resp else 'No response'}"
                if resp and hasattr(resp, 'text'):
                    print(f"Текст ошибки: {resp.text}")
    except Exception as e:
        error_info = f"Исключение: {str(e)}"
        print(f"❌ Ошибка: {e}")
        traceback.print_exc()
    
    return render_template('glavnaya.html', user=user_info, error=error_info)

@app.route('/o-nas')
def o_nas():
    return render_template('o-nas.html')

@app.route('/kontakty')
def kontakty():
    return render_template('kontakty.html')

@app.route('/podderzhka')
def podderzhka():
    return render_template('podderzhka.html')

@app.route('/vyhod')
def vyhod():
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
    return redirect(url_for('podderzhka'))

@app.route('/health')
def health():
    return {"status": "ok", "google": GOOGLE_AUTH_ENABLED}

# Обработчик ошибок
@app.errorhandler(500)
def handle_500(error):
    print(f"❌ 500 ERROR: {error}")
    traceback.print_exc()
    return "Внутренняя ошибка сервера. Проверьте логи.", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
