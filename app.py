import os
import sys
import json
import datetime
from flask import Flask, render_template, redirect, url_for, request, session, jsonify

print("="*70)
print("СПЕКТР ОБЩЕНИЯ - МАКСИМАЛЬНАЯ ВЕРСИЯ 2026 (Python 3.11)")
print("="*70)
print(f"Python: {sys.version.split()[0]}")
print(f"Дата запуска: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")

# Автовыбор драйвера для SocketIO
try:
    import eventlet
    eventlet.monkey_patch()
    ASYNC_MODE = 'eventlet'
    print("✅ Используем eventlet (быстрый)")
except ImportError:
    try:
        import gevent
        from gevent import monkey
        monkey.patch_all()
        ASYNC_MODE = 'gevent'
        print("✅ Используем gevent (стабильный)")
    except ImportError:
        ASYNC_MODE = 'threading'
        print("⚠️ Используем threading (медленно, но работает)")

from flask_socketio import SocketIO, emit, join_room, leave_room

# Импорт Flask-Dance
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
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "spectrum-max-2026")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_NAME'] = 'spectrum_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 часа

# Настройка SocketIO с автовыбором
socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   async_mode=ASYNC_MODE,
                   logger=False,
                   engineio_logger=False,
                   ping_timeout=60,
                   ping_interval=25,
                   max_http_buffer_size=1000000)

print(f"✅ SocketIO настроен с режимом: {ASYNC_MODE}")

# ========== НАСТРОЙКА GOOGLE OAuth ==========
GOOGLE_AUTH_ENABLED = False
google_bp = None

if FLASK_DANCE_AVAILABLE:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    
    if client_id and client_secret:
        try:
            google_bp = make_google_blueprint(
                client_id=client_id,
                client_secret=client_secret,
                scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
                redirect_to="glavnaya",
                login_url="/login/google",
                authorized_url="/login/google/authorized"
            )
            app.register_blueprint(google_bp, url_prefix="/login")
            print("✅ Google вход настроен")
            print(f"   Redirect URI: https://spectrum-of-communication-3-0.onrender.com/login/google/authorized")
            GOOGLE_AUTH_ENABLED = True
            
            # Обработчик успешного входа
            @oauth_authorized.connect_via(google_bp)
            def google_logged_in(blueprint, token):
                """Обработка успешного входа через Google"""
                resp = blueprint.session.get("/oauth2/v2/userinfo")
                if resp.ok:
                    user_info = resp.json()
                    email = user_info.get('email')
                    
                    # Сохраняем пользователя в сессии
                    session['user_info'] = user_info
                    session.permanent = True
                    
                    # Добавляем в базу если новый
                    if email not in users_db:
                        users_db[email] = {
                            'name': user_info.get('name'),
                            'email': email,
                            'avatar': user_info.get('picture'),
                            'joined': datetime.datetime.now().strftime('%d.%m.%Y'),
                            'settings': {
                                'theme': 'dark',
                                'notifications': True,
                                'sound': True,
                                'microphone': False,
                                'menu_color': '#1a1e24',
                                'text_color': '#ffffff'
                            }
                        }
                        # Добавляем во все группы
                        for group_id in groups_db:
                            if email not in groups_db[group_id]['members']:
                                groups_db[group_id]['members'].append(email)
                    
                    print(f"✅ Пользователь {email} вошёл в систему")
                else:
                    print(f"❌ Ошибка получения данных пользователя: {resp.status_code}")
                    
        except Exception as e:
            print(f"❌ Ошибка настройки Google: {e}")
    else:
        print("⚠️ Google ключи отсутствуют в окружении")

# ========== БАЗА ДАННЫХ ==========
users_db = {}  # {email: {...}}
groups_db = {
    "main": {
        "name": "Общий чат",
        "description": "Главная группа для всех пользователей",
        "members": [],
        "admins": [],
        "messages": [],
        "created": "2026-01-01"
    },
    "random": {
        "name": "Случайный чат",
        "description": "Для свободного общения",
        "members": [],
        "admins": [],
        "messages": [],
        "created": "2026-01-01"
    },
    "tech": {
        "name": "Технический чат",
        "description": "Обсуждение технологий и помощь",
        "members": [],
        "admins": [],
        "messages": [],
        "created": "2026-01-01"
    },
    "games": {
        "name": "Игровой чат",
        "description": "Обсуждение игр",
        "members": [],
        "admins": [],
        "messages": [],
        "created": "2026-01-01"
    }
}
blocked_users = {}  # {email: [blocked_email, ...]}

# ========== УСЛОВИЯ ИСПОЛЬЗОВАНИЯ ==========
TERMS_OF_SERVICE = """
ПРАВИЛА ИСПОЛЬЗОВАНИЯ ПЛАТФОРМЫ "СПЕКТР ОБЩЕНИЯ"

1. ОБЩИЕ ПОЛОЖЕНИЯ
   1.1. Используя платформу "Спектр Общения", вы соглашаетесь с данными правилами.
   1.2. Платформа предоставляется "как есть" без гарантий бесперебойной работы.
   1.3. Мы оставляем за собой право блокировать пользователей за нарушение правил.

2. ПРАВА И ОБЯЗАННОСТИ ПОЛЬЗОВАТЕЛЕЙ
   2.1. Пользователь обязуется не оскорблять других участников.
   2.2. Запрещена публикация спама, рекламы и противоправного контента.
   2.3. Пользователь несёт ответственность за сохранность своих данных.

3. КОНФИДЕНЦИАЛЬНОСТЬ
   3.1. Мы не передаём ваши данные третьим лицам.
   3.2. Вся переписка является конфиденциальной.
   3.3. Мы используем шифрование для защиты сообщений.

4. БЛОКИРОВКИ И ОГРАНИЧЕНИЯ
   4.1. Администраторы имеют право блокировать пользователей за нарушения.
   4.2. Блокировка может быть временной или постоянной.
   4.3. Заблокированный пользователь теряет доступ к чатам.

5. ОТВЕТСТВЕННОСТЬ
   5.1. Администрация не несёт ответственности за действия пользователей.
   5.2. В случае нарушения правил, аккаунт может быть заблокирован без предупреждения.

Дата последнего обновления: 18 февраля 2026 года
"""

# ========== МАРШРУТЫ ==========
@app.route('/')
def glavnaya():
    """Главная страница с чатом"""
    user_info = session.get('user_info')
    
    # Загружаем настройки пользователя
    user_settings = users_db.get(user_info.get('email'), {}).get('settings') if user_info else None
    if not user_settings and user_info:
        user_settings = {
            'theme': 'dark',
            'notifications': True,
            'sound': True,
            'microphone': False,
            'menu_color': '#1a1e24',
            'text_color': '#ffffff'
        }
        if user_info.get('email') in users_db:
            users_db[user_info['email']]['settings'] = user_settings
    
    return render_template('glavnaya.html', 
                          user=user_info, 
                          settings=user_settings,
                          groups=groups_db)

@app.route('/login/google')
def google_login():
    if GOOGLE_AUTH_ENABLED and google_bp:
        return redirect(url_for("google.login"))
    return "Вход через Google временно недоступен", 503

@app.route('/vyhod')
def vyhod():
    session.clear()
    return redirect(url_for('glavnaya'))

@app.route('/profile')
def profile():
    """Страница профиля с настройками"""
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('glavnaya'))
    
    user_settings = users_db.get(user_info.get('email'), {}).get('settings', {
        'theme': 'dark',
        'notifications': True,
        'sound': True,
        'microphone': False,
        'menu_color': '#1a1e24',
        'text_color': '#ffffff'
    })
    
    blocked = blocked_users.get(user_info.get('email'), [])
    
    return render_template('profile.html',
                          user=user_info,
                          settings=user_settings,
                          blocked=blocked,
                          groups=groups_db)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    """Сохранение настроек пользователя"""
    user_info = session.get('user_info')
    if not user_info:
        return jsonify({"error": "Not logged in"}), 401
    
    settings = request.json
    email = user_info.get('email')
    
    if email not in users_db:
        users_db[email] = {}
    users_db[email]['settings'] = settings
    session['user_settings'] = settings
    
    return jsonify({"success": True, "settings": settings})

@app.route('/terms')
def terms():
    """Страница с условиями использования"""
    return render_template('terms.html', terms=TERMS_OF_SERVICE, year=2026)

@app.route('/groups')
def groups():
    """Страница со списком групп"""
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('glavnaya'))
    
    return render_template('groups.html', 
                          user=user_info,
                          groups=groups_db)

@app.route('/group/<group_id>')
def group_detail(group_id):
    """Страница конкретной группы"""
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('glavnaya'))
    
    group = groups_db.get(group_id)
    if not group:
        return "Группа не найдена", 404
    
    return render_template('group.html',
                          user=user_info,
                          group=group,
                          group_id=group_id)

@app.route('/block-user', methods=['POST'])
def block_user():
    """Блокировка пользователя"""
    user_info = session.get('user_info')
    if not user_info:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    block_email = data.get('email')
    user_email = user_info.get('email')
    
    if user_email not in blocked_users:
        blocked_users[user_email] = []
    
    if block_email not in blocked_users[user_email]:
        blocked_users[user_email].append(block_email)
    
    return jsonify({"success": True, "blocked": blocked_users[user_email]})

@app.route('/unblock-user', methods=['POST'])
def unblock_user():
    """Разблокировка пользователя"""
    user_info = session.get('user_info')
    if not user_info:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    unblock_email = data.get('email')
    user_email = user_info.get('email')
    
    if user_email in blocked_users and unblock_email in blocked_users[user_email]:
        blocked_users[user_email].remove(unblock_email)
    
    return jsonify({"success": True, "blocked": blocked_users.get(user_email, [])})

# ========== WEBSOCKET СОБЫТИЯ ==========
@socketio.on('connect')
def handle_connect():
    user_info = session.get('user_info')
    if user_info:
        print(f"🔌 WebSocket подключён: {user_info.get('email')}")
        emit('connected', {'status': 'connected', 'user': user_info})
    else:
        print("🔌 WebSocket подключён (без авторизации)")

@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 WebSocket отключён")

@socketio.on('join_group')
def handle_join_group(data):
    group = data.get('group', 'main')
    user_info = session.get('user_info')
    if user_info and user_info.get('email'):
        join_room(group)
        emit('group_joined', {'group': group, 'user': user_info.get('name')}, room=group)
        print(f"👥 Пользователь {user_info.get('name')} присоединился к группе {group}")

@socketio.on('send_message')
def handle_send_message(data):
    user_info = session.get('user_info')
    if not user_info:
        return
    
    group = data.get('group', 'main')
    message = data.get('message', '').strip()
    
    if not message:
        return
    
    user_email = user_info.get('email')
    
    # Проверяем блокировки
    blocked_emails = blocked_users.get(user_email, [])
    for blocked in blocked_emails:
        if blocked in groups_db.get(group, {}).get('members', []):
            emit('error', {'message': 'Вы не можете отправлять сообщения этому пользователю'}, room=request.sid)
            return
    
    # Сохраняем сообщение
    msg_data = {
        'user': user_info.get('name'),
        'email': user_email,
        'message': message,
        'time': datetime.datetime.now().strftime('%H:%M'),
        'avatar': user_info.get('picture', '/static/logo.png')
    }
    
    if group not in groups_db:
        groups_db[group] = {
            'name': group,
            'description': 'Новая группа',
            'members': [],
            'admins': [],
            'messages': [],
            'created': datetime.datetime.now().strftime('%Y-%m-%d')
        }
    
    groups_db[group]['messages'].append(msg_data)
    emit('new_message', msg_data, room=group)
    print(f"💬 Сообщение от {user_info.get('name')} в {group}: {message[:30]}...")

@socketio.on('typing')
def handle_typing(data):
    user_info = session.get('user_info')
    if user_info:
        emit('user_typing', {
            'user': user_info.get('name'),
            'group': data.get('group')
        }, room=data.get('group'))

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Запуск сервера на порту {port} с режимом {ASYNC_MODE}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
