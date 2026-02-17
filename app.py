from flask import Flask, render_template
import os

# Создаём приложение
app = Flask(__name__)

# Это главная страница
@app.route('/')
def home():
    return render_template('index.html')

# Это страница "О нас"
@app.route('/about')
def about():
    return render_template('about.html')

# Это страница "Контакты"
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Запуск сервера (это не трогай)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
