# Плагин для распонавания изображений
import cv2
from ultralytics import YOLO
import plugins


class Detector(plugins.Base):

    def __init__(self, player=None, executor=None):
        self.player = player  # ссылка на объект плеера (для доступу к методам работы с интерфейсом)
        self.executor = executor  # экземпляр класса ThreadPoolExecutor из модуля concurrent.futures зщя запуска функций в отдельном потоке
        self.process_frame_enabled = True  # переменная говорит плееру, что данный плагин должен получать на обработку кадры

        # Плагины, которые будут загружены раньше текущего
        self.enabled_plugins = {
            'Logger': False,
        }

        self.future = None  # здесь будет ссылка на объект текущей задачи распознавания кадра
        self.results = None  # здесь будут результаты распознавания

    def start(self):
        print("Плагин распознавания подключен")
        # Загрузка обученных весов yolo
        # model = YOLO('yolov5m6u.pt')
        self.model = YOLO('plugins/detector/weights_redcar.pt')


    def process_frame(self, image, *args):
        if self.future is not None:
            if self.future.done():
                self.save_results(self.future)
            else:
                if self.results:
                    image = self.annotate(image.copy())
                return image

        # Запускаем асинхронно задачу детекции объектов
        self.future = self.executor.submit(self.model, image, verbose=False)

        if self.results:
            image = self.annotate(image.copy())

        # results = self.model(image, verbose=False)
        return image

    def save_results(self, future):
        self.results = future.result()
        # print("записали результат распознавания")

    def annotate(self, image):
        # Обработка результатов
        for result in self.results:
            # print(result)
            boxes = result.boxes  # Получение рамок объектов
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # Координаты бокса
                class_id = int(box.cls[0])  # ID класса
                confidence = box.conf[0]  # Уверенность

                # Отображение рамки и метки на изображении
                label = f"{self.model.names[class_id]}: {confidence:.2f}"
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        return image

    def requested_data(self):
        # метод возвращает результаты распознавания по запросу из другого плагина (используется в DroneControl)
        if self.results is None:
            return []
        return self.results[0].boxes


if __name__ == "__main__":
    # Путь к изображению для распознавания
    img_path = 'image.jpg'
    detector = Detector()
    image_processed = detector.process_frame(cv2.imread(img_path))
    # Сохранение или отображение результата
    cv2.imshow("Detected Image", image_processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
