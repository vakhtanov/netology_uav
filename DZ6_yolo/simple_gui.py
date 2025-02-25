# модуль simple_gui.py

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout


class ImageRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка интерфейса
        self.setWindowTitle('Окно интерфейса')
        self.setGeometry(100, 100, 1400, 900)

        layout = QVBoxLayout()

        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.button = QPushButton('Кнопка', self)
        layout.addWidget(self.button)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageRecognitionApp()
    window.show()
    sys.exit(app.exec_())