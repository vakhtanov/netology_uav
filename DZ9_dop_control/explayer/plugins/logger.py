# модуль сохраняет информацию из консоли в файл
import os
import time

import plugins

import sys
import datetime
import builtins

import threading


class Logger(plugins.Base):
    def __init__(self, player=None, executor=None):
        self.player = player
        self.filename = f"app_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        self.console_output = True
        # Создаем объект блокировки
        self.print_lock = threading.Lock()

    def write(self, message):
        with open(self.filename, 'a') as file:
            file.write(message)
        if self.console_output:
            sys.__stdout__.write(message)

    def start(self):
        # меняем print на свою функцию
        self.old_print = builtins.print
        builtins.print = self.my_print

        sys.stdout = self
        sys.stderr = self

        logs_path = 'logs'
        os.makedirs(logs_path, exist_ok=True)
        self.filename = os.path.join(logs_path, self.filename)

        print("Плагин для логирования подключен", self.filename)

    def my_print(self, *args, **kwargs):
        output = ' '.join(map(str, args))
        with self.print_lock:
            self.old_print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {output}", **kwargs)
