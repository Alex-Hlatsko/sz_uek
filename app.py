from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

# Функция для запуска проекта из main.py
def run_project():
    process = subprocess.Popen(["python", "main.py"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode("utf-8")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_project', methods=['POST'])
def run_project_route():
    result = run_project()  # Запускаем проект при нажатии на кнопку
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
