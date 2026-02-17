import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google

# ========== СОЗДАЁМ ПРИЛОЖЕНИЕ ==========
app = Flask(__name__)

# Секретный ключ для сессий (можно оставить так)
app.secret_key = "sdflkjsdflkjsdflkjsdflkjsdflkj"

# ========== НАСТРОЙКА БАЗЫ ДАННЫХ ==========
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ========== МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ==========
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))

# ========== НАСТРОЙКА ВХОДА ==========
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== ВХОД ЧЕРЕЗ GOOGLE (ДАННЫЕ БЕРЁМ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) ==========
blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),          # Берётся из Render
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),  # Берётся из Render
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")

# ========== МАРШРУТЫ ==========
@app.route('/')
def home():
    return render_template('index.html', user=current_user)

@app.route('/about')
def about():
    return render_template('about.html', user=current_user)

@app.route('/contact')
def contact():
    return render_template('contact.html', user=current_user)

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        email = resp.json()["email"]
        name = resp.json()["name"]
        
        # Проверяем, есть ли пользователь в базе
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('home'))
    return "Ошибка входа, мудак!"

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# ========== СОЗДАНИЕ БАЗЫ ДАННЫХ ==========
with app.app_context():
    db.create_all()

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
