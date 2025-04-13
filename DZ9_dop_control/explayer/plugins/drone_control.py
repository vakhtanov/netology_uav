import time

import plugins
import threading
from pymavlink import mavutil  # библиотека Python для работы с протоколом MAVLink


class Drone:
    # Дадакласс хранит информацию о положении дрона
    x: float = 0
    y: float = 0
    z: float = 0
    yaw: float = 0
    pitch: float = 0
    roll: float = 0


class DroneControl(plugins.Base):
    last_detection_time = time.time()

    def __init__(self, player=None, executor=None):
        self.player = player  # ссылка на объект плеера (для доступу к методам работы с интерфейсом)
        # Плагины, которые будут загружены раньше текущего
        self.enabled_plugins = {
            'Logger': False,
            'Detector': False,
        }

        # привязываем кнопки подключения телеметрии и активации преследования
        if player is not None:
            # назначаем кнопки управления
            self.player.main_window.add_key_action("1", self.connect_to_drone)  # по нажатию 1 будет подключен дрон
            self.player.main_window.add_key_action("2", self.start_auto_mode)  # по нажатию 2 дрон полетит на обнаруженный объект

        self.master = None  # ссылка на объект подключения к дрону
        self.drone = None  # здесь будем хранить данные о положении дрона

    # Подключение к дрону при нажатии кнопки 1
    def connect_to_drone(self):
        print("Подключаемся к дрону по протоколу mavlink")
        connection = 'tcp:127.0.0.1:14550'
        if self.master is None:
            try:
                self.master = mavutil.mavlink_connection(connection)
                # Устанавливаем интервалы получения сообщений телеметрии
                self.request_message_interval(self.master, 'SIMSTATE', 20)
                self.request_message_interval(self.master, 'LOCAL_POSITION_NED', 20)

                self.drone = Drone()
            except Exception as e:
                print(f"Ошибка подключения: {e}")
                return
        elif self.running:
            self.close_connection()
            return
        self.running = True
        self.thread = threading.Thread(target=self.listen_to_drone)
        self.thread.daemon = True  # Чтобы поток завершался при закрытии программы
        self.thread.start()
        return

    def start(self):
        print("Плагин управления дроном подключен")

    def listen_to_drone(self):
        while self.running:
            try:
                msg = self.master.recv_match(blocking=True, timeout=1)
                if msg.get_type() == 'SIMSTATE':
                    self.drone.yaw = msg.yaw
                    self.drone.pitch = msg.pitch
                    self.drone.roll = msg.roll
                    # print(f"Сообщение SIM_STATE: {msg}")
                elif msg.get_type() == 'LOCAL_POSITION_NED':
                    self.drone.x = msg.x
                    self.drone.y = msg.y
                    self.drone.z = msg.z
                    # print(f"Сообщение LOCAL_POSITION_NED: {msg}")
                    detect_result = self.request_data('Detector')
                    self.active_track(detect_result)

            except Exception as e:
                print(f"Ошибка приема сообщения: {e}")
                self.running = False

    def active_track(self, detect_result):
        if not len(detect_result):
             # если ничего не обнаружили
            ######### Блок для кода ДЗ #########
            # Добавьте сюда код поведения аппарата, если машинка не обнаружена
            lost_time = time.time() - self.last_detection_time
            #print('объект не найден',lost_time)
            if  lost_time >= 2:
                #print('режим поворота')
                rc4_value = 1550
                self.master.mav.rc_channels_override_send(
                    self.master.target_system,  # ID системы
                    self.master.target_component,  # ID компонента
                    0, 1500, 1500, rc4_value, 0, 0, 0, 0  # Значения для RC1 - RC8 (оставьте нулями, если не используете)
                 )
                 ########################################################################################
        else:
            self.last_detection_time = time.time() #Vakhtanov
            for box in detect_result:
                dx = box.xywhn[0][0] - 0.5  # определяем смещение относительно центра
                rc4_value = int(dx * 200) + 1500  # рассчитываем команду для поворота

                dy = box.xywhn[0][1] - 0.5  # рассчитываем команду для тангажа (движение вперет/назад)
                rc2_value = int(dy * 500) + 1500

                #print('команда для rc4', dx, rc4_value, dy, rc2_value)
                # Отправляем команду на изменение значения RC4
                self.master.mav.rc_channels_override_send(
                    self.master.target_system,  # ID системы
                    self.master.target_component,  # ID компонента
                    0, rc2_value, 1500, rc4_value, 0, 0, 0, 0  # Значения для RC1 - RC8 (оставьте нулями, если не используете)
                )

    def close_connection(self):
        # Закрываем подключение Mavlink
        self.running = False
        time.sleep(0.2)
        if self.master is not None:
            self.master.close()
            self.master = None
        print("Соединение с дроном закрыто")

    def start_auto_mode(self):
        print("Включаем автоматический режим")
        if self.master is not None:
            mavutil.mavfile.set_mode(self.master, 2, 0, 0)  # 2 - идентификатор режима AltHold
        else:
            print("Дрон не подключен")

    def requested_data(self):
        # print("Запрошены данные телеметрии")
        if self.drone is None:
            return
        return self.drone

    # Метод для установки интервала отправки сообщений телеметрии из полетного контроллера
    @staticmethod
    def request_message_interval(master, message_input: str, frequency_hz: float):
        message_name = "MAVLINK_MSG_ID_" + message_input
        message_id = getattr(mavutil.mavlink, message_name)

        # Установка нового интервала
        master.mav.command_long_send(master.target_system, master.target_component,
                                     mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, message_id, 1e6 / frequency_hz, 0,
                                     0, 0, 0, 0)
        print(f"Requested {message_input, message_id} successfully")


if __name__ == "__main__":
    dc = DroneControl()
    dc.start()
