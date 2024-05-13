import sys
import subprocess
from window.Window import Window
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

def run_project():
    process = subprocess.Popen(["python", "main.py"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode("utf-8")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('window/styles.qss', 'r', encoding="utf-8") as f:
        style = f.read()
        app.setStyleSheet(style)

    window = Window()

    run_button = QPushButton("Run Project")
    run_button.clicked.connect(lambda: window.show_result(run_project()))

    layout = QVBoxLayout()
    layout.addWidget(run_button)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())
