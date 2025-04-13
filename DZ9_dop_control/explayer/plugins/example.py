'''
Пример плагина, который накладывает на кадр текст и графику средствами opencv
'''
import datetime
import cv2
import os

import plugins  # обязательно для работы автоматической загрузки плагинов


# Определяем свой класс для обработки кадров видео
# Обязательно наследуем 'plugins.Base'
class MyClass(plugins.Base):
    def __init__(self, player=None, executor=None):
        self.player = player  # ссылка на объект плеера (используется для добавления кнопок и т.п.)
        self.executor = executor  #  метод для запуска функций в отдельном потоке
        self.process_frame_enabled = True  # указывает плееру, что каждый кадр надо отправлять на обработку в наш плагин
        
        self.show_url = False

    # Этот метод вызывается при загрузке плагина
    def start(self):
        print("Плагин MyClass подключен", os.getcwd())

        # Пример добавления контекстного меню
        if self.player is not None:
            self.player.main_window.context_menu.add_action('Показать/скрыть url',
                                                            self.menu_action)

    # Метод будет вызван через контекстное меню
    def menu_action(self, menu_item=None):
        print('Нажали контекстное меню')
        self.show_url = not self.show_url

    # Если указали self.process_frame_enabled = True, обязательно должен писутствовать метод process_frame
    # В этот метод отправяются на обработку кадры
    def process_frame(self, frame=None, frame_id=None):
        if frame is None:
            return None

        # Создаем копию кадра, чтобы избежать изменения оригинального кадра
        frame_copy = frame.copy()

        # Получаем текущее время
        current_time = datetime.datetime.now()
        milliseconds = current_time.microsecond // 1000

        # Определяем радиус круга в зависимости от миллисекунд
        if 0 <= milliseconds < 500:
            radius = 50 + milliseconds // 10
        else:
            radius = 100 - (milliseconds - 500) // 10

        # Центр круга
        center = (frame_copy.shape[1] // 2, frame_copy.shape[0] // 2)

        # Рисуем круг
        cv2.circle(frame_copy, center, radius, (0, 0, 200), 2)

        # Добавляем текущее время на кадр
        time_text = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        cv2.putText(frame_copy, time_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame_copy, "Используется тестовый плагин ./plugins/example.py", (10, 80), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_copy, "Открыть другое видео: двойной клик мышкой по окну видео", (10, 100), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_copy, "Добавьте example.py в исключения в файле config.py, чтобы отключить", (10, 120), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
        
        if self.show_url:
          cv2.putText(frame_copy, "Сайт: http://ep.diworld.ru", (10, 180), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 50, 50), 2, cv2.LINE_AA)

        return frame_copy  # возвращаем плееру обработанный кадр

    def close(self):
        print('Вызван метод close в плагине example')
