import os
import sys
from flask import Flask, render_template, redirect, url_for, request

print(f"=== СПЕКТР ОБЩЕНИЯ === Версия 2.0")
print(f"Python: {sys.version.split()[0]}")

# Импорт Flask-Dance с защитой
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    from flask_dance.consumer import oauth_authorized
    FLASK_DANCE_AVAILABLE = True
    print("✅ Google авторизация доступна")
except ImportError as e:
    FLASK_DANCE_AVAILABLE = False
    print(f"⚠️ Google авторизация недоступна: {e}")
    google = None

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "spectrum-secret-key-2026")

# Настройка Google OAuth
if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if client_id and client_secret:
        try:
            google_bp = make_google_blueprint(
                client_id=client_id,
                client_secret=client_secret,
                scope=["profile", "email"],
                redirect_to="glavnaya"
            )
            app.register_blueprint(google_bp, url_prefix="/login")
            print("✅ Google вход настроен")
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
            if hasattr(google, 'authorized') and google.authorized:
                resp = google.get("/oauth2/v2/userinfo")
                if resp and resp.ok:
                    user_info = resp.json()
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

# Выход
@app.route('/vyhod')
def vyhod():
    """Выход из аккаунта"""
    if FLASK_DANCE_AVAILABLE and google:
        try:
            return redirect(url_for("google.logout"))
        except:
            pass
    return redirect(url_for('glavnaya'))

# Поддержка
@app.route('/podderzhka')
def podderzhka():
    """Страница поддержки"""
    return render_template('podderzhka.html', email="zenorvin@gmail.com")

# Обработка формы обратной связи
@app.route('/otpravka-soobscheniya', methods=['POST'])
def otpravka_soobscheniya():
    """Отправка сообщения (заглушка)"""
    name = request.form.get('name', 'Аноним')
    message = request.form.get('message', '')
    print(f"Сообщение от {name}: {message}")
    return redirect(url_for('podderzhka', sent='true'))

# Проверка здоровья
@app.route('/zdorovo')
def zdorovo():
    return {"status": "ok", "time": "работает"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
