from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__)
app.secret_key = "какой-то-сложный-ключ-мудак"  # Поменяй!

# База данных
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

# Регистрация через гугл
blueprint = make_google_blueprint(
    client_id="ТВОЙ_GOOGLE_CLIENT_ID",  # Получишь в консоли гугла
    client_secret="ТВОЙ_GOOGLE_CLIENT_SECRET",  # Это тоже
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")

# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))

# Настройка логина
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html', user=current_user)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаст базу данных
    app.run()
