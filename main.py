import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import requests

class LoginWorker(QThread):
    finished = pyqtSignal(bool, str)  # Успех, Сообщение

    def __init__(self, email, password, code):
        super().__init__()
        self.email = email
        self.password = password
        self.code = code

    def run(self):
        url = "https://api.cryptocards.ws/login"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }
        data = {
            "email": self.email,
            "password": self.password,
            "code": self.code,  # Теперь код 2FA передается в запросе
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                self.finished.emit(True, 'Вы успешно авторизовались!')
            else:
                self.finished.emit(False, f'Ошибка авторизации: {response.status_code}')
        except Exception as e:
            self.finished.emit(False, f'Возникла ошибка при запросе: {e}')

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Авторизация на сайте')
        self.setGeometry(100, 100, 320, 200)

        layout = QVBoxLayout()

        self.emailLabel = QLabel('Email:')
        self.emailInput = QLineEdit()
        self.passwordLabel = QLabel('Пароль:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.codeLabel = QLabel('2-FA Код:')
        self.codeInput = QLineEdit()
        self.loginButton = QPushButton('Войти')
        self.loginButton.clicked.connect(self.handleLogin)

        layout.addWidget(self.emailLabel)
        layout.addWidget(self.emailInput)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordInput)
        layout.addWidget(self.codeLabel)
        layout.addWidget(self.codeInput)
        layout.addWidget(self.loginButton)

        self.setLayout(layout)

    def handleLogin(self):
        email = self.emailInput.text().strip()
        password = self.passwordInput.text().strip()
        code = self.codeInput.text().strip()

        if not email or not password or (self.codeInput.isVisible() and not code):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля')
            return

        self.worker = LoginWorker(email, password, code)
        self.worker.finished.connect(self.onLoginFinished)
        self.worker.start()

    def onLoginFinished(self, success, message):
        if success:
            QMessageBox.information(self, 'Успех', message)
        else:
            QMessageBox.warning(self, 'Ошибка', message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginWindow()
    ex.show()
    sys.exit(app.exec_())