import sys
import plugins

class pyversion(plugins.Base):
    def __init__(self, player=None, executor=None):
        self.player = player  # ссылка на объект плеера (используется для добавления кнопок и т.п.)

    def start(self):
            print("Плагин 3D симулятора подключен")
            print(sys.version)
            if self.player is not None:
                self.player.main_window.context_menu.add_action('версия Python',
                                                                self.version)
    def version(self):
        print(sys.version)
