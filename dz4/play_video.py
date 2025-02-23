import cv2

print(cv2.__version__)

# Функция для изменения изображения
def annotate(img, x, y, w, h):
    x_start = int(img.shape[1] * x)
    y_start = int(img.shape[0] * y)

    # Определение текста и его параметров
    text = "здесь рамка"
    font = cv2.FONT_HERSHEY_COMPLEX   # установка шрифта
    font_scale = 0.7                  # размер шрифта
    font_color = (0, 125, 125)      # Белый цвет
    line_type = 1                     # тип линии (1-сплошная)

    # Позиция текста на изображении
    text_x = x_start - int(img.shape[1] * w)
    text_y = y_start - int(img.shape[0] * h) - 10

    # Добавление текста на изображение
    cv2.putText(img, text, (text_x, text_y), font, font_scale, font_color, line_type)

    # Домашнее задание: добавьте сюда код рисующий рамку
    # Определение координат для рамки (x_start, y_start, width, height)
    #x_start = 20
    #y_start = 30

    # Вычисление координат правого нижнего угла
    x_end = x_start + int(img.shape[1] * w)
    y_end = y_start + int(img.shape[0] * h)

    color = (0,125,125)
    thickness = 1
    cv2.rectangle(img, (x_start, y_start), (x_end, y_end), color, thickness)

    return img


# Путь к видеофайлу
video_path = '3313_rain.mp4'
video_out_path = '3313_rain_frame.mp4'

# Открытие видеофайла
cap = cv2.VideoCapture(video_path)
# получаем параметры видео
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#определяем кодак для выходногов видео
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#Объект для записи видео
out = cv2.VideoWriter(video_out_path,fourcc,fps,(width,height))

# Проверка открытия файла
if not cap.isOpened():
    print("Ошибка: Не удалось открыть видео.")
    exit()

# Чтение и отображение кадров
while True:
    # Получение кадра
    ret, frame = cap.read()
    if not ret:
        break  # Выход из цикла, если больше нет кадров

    # Рисуем рамку (ДЗ)
    box = [0.5, 0.5, 0.1, 0.1]  # относительные координаты рамки
    # image = annotate(frame, *box)

    image = annotate(frame, *box)

    # Отображение текущего кадра с помощью OpenCV
    cv2.imshow('Video Playback', image)

    #запись кадров
    out.write(image)

    # Ожидание короткий период для управления скоростью воспроизведения
    key = cv2.waitKey(30)  # Настройте это значение для скорости воспроизведения (30 мс ≈ 33 FPS)

    if key == 27:  # Нажмите 'Esc' для выхода
        break

# Освобождение объекта захвата видео
cap.release()
out.release()