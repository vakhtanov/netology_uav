import math

import cv2
import numpy as np
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import TextNode, NodePath


import plugins


class SimCamera:
    # Класс определяющий положение и управление камерой
    x: float = -40  # Положение камеры по оси X
    y: float = 0  # Положение камеры по оси Y
    z: float = 80  # Положение камеры по оси Z
    yaw: float = 0  # Угол поворота камеры по горизонтали
    pitch: float = -60  # Угол наклона камеры по вертикали
    roll: float = 0  # Угол вращения камеры
    zoom: float = 1  # Уровень приближения камеры
    yaw_speed: float = 0  # Скорость поворота камеры по горизонтали
    pitch_speed: float = 0  # Скорость наклона камеры
    roll_speed: float = 0  # Скорость вращения камеры
    speed: float = 20  # Скорость вращения камеры

    def rotate_camera_right(self):
        # print('поворачиваем камеру вправо')
        self.yaw_speed = -self.speed / self.zoom

    def rotate_camera_left(self):
        # print('поворачиваем камеру влево')
        self.yaw_speed = self.speed / self.zoom

    def rotate_camera_up(self):
        # print('поворачиваем камеру вверх')
        self.pitch_speed = self.speed / self.zoom

    def rotate_camera_down(self):
        # print('поворачиваем камеру вниз')
        self.pitch_speed = -self.speed / self.zoom

    def stop_camera_rotation(self):
        # print('останавливаем поворот камеры')
        self.yaw_speed = 0
        self.pitch_speed = 0

    def zoom_in_camera(self):
        print('приближаем камеру')
        pass

    def zoom_out_camera(self):
        print('отдаляем камеру')
        pass

    def stop_camera_zoom(self):
        print('останавливаем приближение камеры')
        pass

class SimCar:
    # Класс определяющий состояние машины
    def __init__(self):
        self.moving_forward = False
        self.moving_backward = False
        self.turning_left = False
        self.turning_right = False

    def move_forward(self):
        self.moving_forward = True

    def move_backward(self):
        self.moving_backward = True

    def turn_left(self):
        self.turning_left = True

    def turn_right(self):
        self.turning_right = True

    def stop_move_forward(self):
        self.moving_forward = False

    def stop_move_backward(self):
        self.moving_backward = False

    def stop_turn_left(self):
        self.turning_left = False

    def stop_turn_right(self):
        self.turning_right = False


class Simulator(plugins.Base):
    def __init__(self, player=None, executor=None):
        self.player = player
        self.app = None

        self.enabled_plugins = {
            'Logger': False,
            'Detector': False,
            'DroneControl': False,
            # ... Добавьте другие плагины сюда (названия файлов и признак критичности для работы текущего плагина)
        }

        self.camera = SimCamera()
        self.car = SimCar()

        # привязываем кнопки
        if player is not None:
            # передаем ссылку на функцию поворота камеры
            # print('назначаем кнопки управления')

            movement_keys = {
                "right": (self.camera.rotate_camera_right, self.camera.stop_camera_rotation),
                "left": (self.camera.rotate_camera_left, self.camera.stop_camera_rotation),
                "up": (self.camera.rotate_camera_up, self.camera.stop_camera_rotation),
                "down": (self.camera.rotate_camera_down, self.camera.stop_camera_rotation),
                "=": (self.camera.zoom_in_camera, self.camera.stop_camera_zoom),
                "+": (self.camera.zoom_in_camera, self.camera.stop_camera_zoom),
                "-": (self.camera.zoom_out_camera, self.camera.stop_camera_zoom),
                # управление машинкой
                "w": (self.car.move_forward, self.car.stop_move_forward),
                "s": (self.car.move_backward, self.car.stop_move_backward),
                "a": (self.car.turn_left, self.car.stop_turn_left),
                "d": (self.car.turn_right, self.car.stop_turn_right),
            }

            for key, (press_action, release_action) in movement_keys.items():
                # Привязываем действия к клавишам для движения машинки
                self.player.main_window.add_key_action(key, press_action, release_action)

            # self.player.main_window.add_key_action('left', self.camera.rotate_camera_left,
            #                                        self.camera.stop_camera_rotation)


    def start(self):
        print("Плагин 3D симулятора подключен")
        if self.player is not None:
            self.player.main_window.context_menu.add_action('Запустить симулятор',
                                                            self.start_sim)

    # Запуск симулятора
    def start_sim(self, menu_item=None):
        print("Запуск симулятора")
        if self.player is None:  # значит запуск не из плеера
            # print('Запуск sim в оконном режиме')
            self.app = Sim3DApp()
        else:
            # print('Запуск sim в безоконном режиме')
            way = [[20, 35], [50, 50], [90, 45], [95, 0],
                   [75, -35], [20, -40], [-35, -45], [-70, -20],
                   [-100, 35], [-55, 50], [-30, 5], [30, -5], [60, 10],
                   [95, -10], [100, -50], [-20, -55], [-60, -65],
                   [-90, -60], [-105, -45], [-105, 30], [-20, 45], [0, 10]]
            # way = [[30, 30], [60, 20], [-50, -30], [-60, 30]]
            self.app = Sim3DApp(offscreen=True, way=way, get_tm=self.get_telemetry_data)  # чтобы скрыть окно панды3д
        if self.player is not None:
            self.app.set_frame_callback(self.player.process_frame)  # чтобы кадры передавались в плеер
        self.app.set_sim_camera(self.camera)  # передаем объект с данными положения и состояния камеры
        self.app.set_sim_car(self.car)  # передаем объект с данными о машинке

        self.app.run()

    def get_telemetry_data(self):
        return self.request_data("DroneControl")

    def close(self):
        # print('Закрываем симулятор')
        if self.app is not None:
            self.app.userExit()


class Sim3DApp(ShowBase):
    def __init__(self, offscreen=None, way=None, get_tm=None):
        self.__sim_camera = None  # здесь будет объект камеры симулятора
        self.__sim_car = None  # здесь будет объект машинки
        self.__get_tm = get_tm  # метод, в котором будем запрашивать телеметрию

        # проверка, чтобы не создавать новый экземпляр окна при запуске из плеера
        if offscreen is None:
            ShowBase.__init__(self)
        else:
            ShowBase.__init__(self, windowType='offscreen')

        self.way = way if way is not None else None  # точки маршрута
        if self.way is not None:
            self.way_point_id = 0  # стартовая точка
        else:
            self.way_point_id = None
        # отладка

        self.__send_frame = None  # здесь будет функция для отправки кадра в главный модуль
        self.frame_id: int = 0

        self.scene = self.loader.loadModel(path_to_model, noCache=False)
        self.scene.reparentTo(self.render)
        self.scene.setPos(0, 0, 0)  # (x, z, y)  0, 0 - центр. Размер сцены 240x136 м

        # Загрузка модели машинки
        self.car = self.loader.loadModel(path_to_car_model, noCache=True)
        self.car.reparentTo(self.render)

        # Настройка положения и масштаба модели
        self.car.setPos(0, 0, 0)
        self.car.setScale(2, 2, 2)

        # Устанавливаем позицию камеры относительно родителя
        self.camera.reparentTo(self.render)
        self.camera.setPos(0, -50, 50)  # Позиция камеры

        # Скорость движения машинки
        self.speed = 4
        self.turn_speed = 1  # Скорость поворота

        # Создание текстового узла для отображения позиции машинки
        self.position_text = TextNode("position_text")
        self.position_text.setText("Position: X=0, Y=0, Z=0")
        self.position_text.setTextColor(1, 1, 1, 1)
        self.position_text.setAlign(TextNode.ALeft)
        self.position_text_node_path = self.aspect2d.attachNewNode(self.position_text)
        self.position_text_node_path.setPos(-1.3, 0, 0.9)
        self.position_text_node_path.setScale(0.05)

        # Запуск обновления положения машинки
        self.taskMgr.add(self.update, "update")
        self.taskMgr.doMethodLater(1.0 / 30.0, self.get_image_and_process, "GetImageAndProcessTask")

        self.setFrameRateMeter(True)

    def update(self, task):
        dt = globalClock.getDt()

        # Обновление положения камеры
        tm_data = self.__get_tm() if self.__get_tm is not None else None
        if tm_data is not None:
            self.camera.setPos(tm_data.y, tm_data.x, -tm_data.z)
            # print('позиция в симуляторе', tm_data.x, tm_data.y, tm_data.z)
            self.__sim_camera.yaw = -math.degrees(tm_data.yaw)
        else:
            self.__sim_camera.yaw += self.__sim_camera.yaw_speed * dt
        self.__sim_camera.pitch += self.__sim_camera.pitch_speed * dt
        self.camera.setHpr(self.__sim_camera.yaw, self.__sim_camera.pitch, self.__sim_camera.roll)

        # обновляем положение машинки
        if self.way is not None:
            self.car_waypoint_move()

        if self.__sim_car.moving_forward:
            self.car.setY(self.car, self.speed * dt)
        if self.__sim_car.moving_backward:
            self.car.setY(self.car, -self.speed * dt)
        if self.__sim_car.turning_left:
            self.car.setH(self.car.getH() + self.turn_speed * dt * (-1 if self.__sim_car.moving_backward else 1))
        if self.__sim_car.turning_right:
            self.car.setH(self.car.getH() - self.turn_speed * dt * (-1 if self.__sim_car.moving_backward else 1))

        # Обновление текста с текущей позицией машинки
        position = self.car.getPos()
        rotation = self.car.getHpr()
        self.position_text.setText(
            f"Position: X={position.getX():.2f}, Y={position.getY():.2f}, Z={position.getZ():.2f}\n"
            f"Rotation: H={rotation.getX():.2f}, P={rotation.getY():.2f}, R={rotation.getZ():.2f}\n"
            f"Camera: Yaw={self.__sim_camera.yaw:.2f}, Pitch={self.__sim_camera.pitch:.2f}, Roll={self.__sim_camera.roll:.2f}\n"
            f"Camera_pos: "
            f"X={self.camera.getPos().getX():.2f}, "
            f"Y={self.camera.getPos().getY():.2f}, "
            f"Z={self.camera.getPos().getZ():.2f}")

        return task.cont

    def car_waypoint_move(self):
        # функция рассчитывает скорость и направление для движения по точкам
        position = self.car.getPos()
        car_x, car_y = position.getX(), position.getY()
        rotation = self.car.getHpr()
        car_yaw = rotation.getX()
        # print('Следующая точка:', self.way_point_id, self.way[self.way_point_id], (car_x, car_y))

        # расчет расстояния до следующей точки
        next_way_point_x, next_way_point_y = self.way[self.way_point_id]
        dx, dy = next_way_point_x - car_x, next_way_point_y - car_y
        way_point_distance = math.sqrt(dx ** 2 + dy ** 2)
        if way_point_distance < 4:  # если приблизились к точке, переходим к следующей
            self.way_point_id += 1
            if self.way_point_id >= len(self.way):
                self.way_point_id = 0
            next_way_point_x, next_way_point_y = self.way[self.way_point_id]
            dx, dy = next_way_point_x - car_x, next_way_point_y - car_y
            way_point_distance = math.sqrt(dx ** 2 + dy ** 2)
            print('Переходим к следующей точке', self.way_point_id, (next_way_point_x, next_way_point_y))

        self.__sim_car.stop_move_backward()
        self.__sim_car.move_forward()

        ang2point = math.degrees(math.atan2(dy, dx))  # 0 - от оси x, [-180, 180]
        d_ang = ang2point - 90 - car_yaw
        if d_ang < -180:
            d_ang += 360
        if d_ang > 180:
            d_ang -= 360

        self.turn_speed = int(min(50, abs(d_ang) * 10))

        if d_ang < 0:
            self.__sim_car.stop_turn_left()
            self.__sim_car.turn_right()
        elif d_ang > 0:
            self.__sim_car.stop_turn_right()
            self.__sim_car.turn_left()

    def get_image_and_process(self, task):
        # Получить изображение из буфера кадров
        screenshot = self.win.getScreenshot()
        self.frame_id += 1
        ramImage = screenshot.getRamImage()
        data = np.frombuffer(ramImage, dtype=np.uint8)
        data = data.reshape(screenshot.getYSize(), screenshot.getXSize(), 4)
        data = data[:, :, :3]  # Отбросить альфа-канал
        data_rgb = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

        # Перевернуть изображение по вертикали
        data_flipped = cv2.flip(data_rgb, 0)

        if self.__send_frame is not None:
            self.__send_frame(data_flipped, self.frame_id)

        # Запланировать следующее получение изображения
        return task.cont

    def set_frame_callback(self, callback):
        # колбек для отправки кадра в главный модуль
        self.__send_frame = callback

    def set_sim_camera(self, camera):
        self.__sim_camera = camera

    def set_sim_car(self, car):
        self.__sim_car = car

path_to_model = "../plugins/3dsim/landscape_z.gltf"
path_to_car_model = "../plugins/3dsim/car_2z.gltf"

if __name__ == '__main__':
    path_to_model = "3dsim/landscape_z.gltf"
    path_to_car_model = "3dsim/car_2z.gltf"

    sim = Simulator()
    sim.start_sim()
