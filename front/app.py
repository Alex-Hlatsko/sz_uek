from flask import Flask, render_template
from back import mrp_logic, ghp_logic

app = Flask(__name__)

@app.route('/')
def index():
    mrp_result = mrp_logic.calculate_mrp(data)
    ghp_result = ghp_logic.calculate_ghp(data)
    return render_template('index.html', mrp_result=mrp_result, ghp_result=ghp_result)

if __name__ == '__main__':
    app.run(debug=True)
