# код модуля ui.py

import sys
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage

from detector import process_image


class ImageRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка интерфейса
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Распознавание изображений с помощью YOLO')
        self.setGeometry(100, 100, 1400, 900)

        layout = QVBoxLayout()

        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.button = QPushButton('Открыть файл изображения', self)
        self.button.clicked.connect(self.open_image)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def open_image(self):
        # Открытие диалога выбора файла
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл изображения", "",
                                                   "Изображения (*.png *.jpg *.jpeg *.bmp)",
                                                   options=options)

        if file_name:
            #print(file_name)
            # Передаем ссылку на файл с изображением в функцию распознавания
            image = process_image(file_name)
            # Передаем ссылку с результатами обнаружения в функцию отображения
            self.display_image(image)

    def display_image(self, image):
        # Конвертация BGR в RGB и преобразование в QPixmap для отображения
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image_rgb.shape
        bytes_per_line = channel * width
        q_img = QPixmap.fromImage(QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888))

        self.label.setPixmap(q_img.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageRecognitionApp()
    window.show()
    sys.exit(app.exec_())