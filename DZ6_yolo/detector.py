# Код файла detector.py
# ! код необходимо выполнять на локальном компьютере

import cv2
from ultralytics import YOLO

# Загрузка модели YOLOv8 (в данном случае используем модель yolov8n)
model = YOLO('yolov8n.pt')


def process_image(image_path):
    # Загрузка изображения
    image = cv2.imread(image_path)

    # Выполнение детекции объектов
    results = model(image)

    # Обработка результатов
    for result in results:
        #print(result)
        boxes = result.boxes  # Получение рамок объектов

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]  # Координаты бокса
            class_id = int(box.cls[0])  # ID класса
            confidence = box.conf[0]  # Уверенность

            # Отображение рамки и метки на изображении
            label = f"{model.names[class_id]}: {confidence:.2f}"
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return image


if __name__ == "__main__":
    # Путь к изображению для распознавания
    img_path = 'original.jpg'
    image_processed = process_image(img_path)

    # Сохранение или отображение результата
    cv2.imshow("Detected Image", image_processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()