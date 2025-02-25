# ! код необходимо выполнять на локальном компьютере

from datetime import datetime  # модуль для работы с датой и временем

from pymavlink import mavutil  # библиотека для работы с протоколом MAVLink
import time  # нужна, чтобы ставить паузу
import threading  #

# Создаем подключение по протоколу MavLink к полетному контроллеру
def do_connect(connect='tcp:127.0.0.1:14550'):
    master = mavutil.mavlink_connection(connect)

    # Ожидаем heartbeat сигнал для подтверждения, что соединение установилось
    master.wait_heartbeat()

    return master


# Запрашиваем информацию из полетного контроллера
def get_telemetry():
    while True:
        try:
            # функция, принимающая сообщения телеметрии
            msg = master.recv_match(blocking=True, timeout=1)
            if msg is not None:
                # print(msg)
                process_telemetry(msg)

        except Exception as e:
            print(f'Потеряно подключение телеметрии {e}')

# Обработка полученных сообщений телеметрии
def process_telemetry(msg):
    if msg.get_type() == 'GLOBAL_POSITION_INT':
        # чтение высоты
        altitude = round(msg.relative_alt / 1000, 1)
        gps_altitude = round(msg.alt / 1000, 1)

        # Чтение GPS координат
        longitude = msg.lon / 1e7  # Чтение долготы в градусах
        latitude = msg.lat / 1e7  # Чтение широты в градусах

        print(get_time())  # получаем текущее время
        print(f'Высота: {altitude}м', f'Высота (GPS): {gps_altitude}м', f'Lon: {longitude}', f'Высота: {latitude}', sep='\n')
        print()


def get_time():
    now = datetime.now()
    return f'{now.hour:02d}:{now.minute:02d}:{now.second:02d}'



# (1) Подключаемся к БЛА
master = do_connect()

# (2) Создаем поток для получения телеметрии
telemetry_thread = threading.Thread(target=get_telemetry)
telemetry_thread.daemon = True  # Поток будет завершен при завершении основного потока
telemetry_thread.start()

command = input('')  # для технической паузы

# Реализуем цикл с командами дрону

import drone_commands as cmd  # импорт команд управления дроном (arm, takeoff, land)


while True:
    command = input('введите команду: ')

    if command == 'exit':
        break
    elif command == 'arm':
        cmd.arm(master)
    elif command == 'takeoff':
        cmd.takeoff(master, 10)
    elif command == 'land':
        cmd.land(master)
    else:
        print('Неизвестная команда!')
        continue
    print("Выполняю команду -", command)

