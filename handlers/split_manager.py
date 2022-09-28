import os
from types import NoneType

import mutagen
from mutagen.mp3 import MP3

from .config_manager import ConfigManager


class SplitManager:

    def __init__(self, path_mp3splt: str = "", path_save_to: str = '', path_temp: str = '', use_config_manager: bool = False):

        if use_config_manager:
            conf_mng = ConfigManager()
            path_temp = path if (path := conf_mng.configs["TEMP"]) != "local" else os.path.join(os.getcwd(), "TEMP")
            path_save_to = path if (path := conf_mng.configs["SAVE_TO"]) != "local" else os.getcwd()
            path_mp3splt = path if (path := conf_mng.configs["MP3SPLT_PATH"]) != "local" else os.path.join(os.getcwd(), "mp3splt")

        self.path_mp3split = path_mp3splt

        self.path_temp = path_temp if path_temp else os.path.join(os.getcwd(), "TEMP")

        self.path_save_to = path_save_to if path_save_to else os.getcwd()

    @staticmethod
    def get_duration(path_file: str = 'TEMP/1.mp3') -> int:
        """Узнаёт длительность аудиофайла по его пути"""

        audio = MP3(path_file)
        duration = round(audio.info.length)
        return duration

    @staticmethod
    def converter_time_mmss(sec: int) -> str:
        """ Преобразование секунд в время в минты+секунды 156сек = 2:36 """
        if type(sec) == int:
            return str(sec // 60) + '.' + str(sec % 60)
        else:
            raise TypeError(f"""converter_time_mmss accepts only the integer value""")

    def create_commands(self, offsets_and_names: list, folder_name: str, number_downloaded_file: int, **kwargs) -> list:
        """ Создацние списка команд для утилиты разделения """
        offset = 0
        current_file = 1
        max_duration = self.get_duration(os.path.join(self.path_temp, '1.mp3'))
        mp3spliter = Mp3splt(os.path.join(self.path_mp3split, 'mp3splt'), os.path.join(self.path_save_to, folder_name))
        for i in range(len(offsets_and_names)):

            if (offsets_and_names[i]['offset'] - offset) >= max_duration:
                current_file += 1
                offset = offsets_and_names[i]['offset']
                try:
                    max_duration = self.get_duration(os.path.join(self.path_temp, str(current_file) + '.mp3'))
                except mutagen.MutagenError as e:
                    raise mutagen.MutagenError(e)

            start = offsets_and_names[i]['offset'] - offset

            try:
                end = offsets_and_names[i + 1]['offset'] - offset
            except IndexError:
                end = max_duration

            time_start = self.converter_time_mmss(start)
            time_end = self.converter_time_mmss(end)

            mp3spliter.add(
                output_file=f"{str(current_file)}.mp3",
                name=offsets_and_names[i]['name'],
                time_start=time_start,
                time_end=time_end,

                number=i+1,
                author=kwargs.get('author'),
            )

        for i in range(number_downloaded_file):
            mp3spliter.commands_list.append(f'del {i + 1}.mp3')
        mp3spliter.commands_list.append('del command.bat')

        return mp3spliter.commands_list

    def run_cmd(self):
        """ Запускает созданный cmd """
        os.startfile(os.path.join(self.path_temp, "command.bat"))

    def create_cmd(self, commands: list, run_after_creation: bool = True):
        """ Создание и консольной утилиты """
        with open(os.path.join(self.path_temp, r"command.bat"), "w", encoding="cp1251") as file:
            file.write('chcp 1251 >nul \n')
            # Переходим к месту расположению этого скрпипта
            file.write('cd ' + self.path_temp + ' \n')
            # Записываем команды из массива
            for command in commands:
                # Записываем комманды для утилиты mp3splt
                file.write(command + "\n")

        if run_after_creation:
            self.run_cmd()


class Mp3splt:

    def __init__(self, path_mp3splt: str, path_save_to: str = ''):
        self.path_mp3splt = path_mp3splt
        self.path_save_to = path_save_to
        self.commands_list = []

    def add(self, **kwargs):
        """ NECESSARY:
                -output_file: str
                -name: str
                -time_start: str
                -time_end: str
            NO NECESSARY:
                -number: int
                -author: str
        """
        self.commands_list.append(self.compose_command(**kwargs))

    @staticmethod
    def init_argument(kwargs: dict, name: str, valid_type: type, necessary: bool = True):

        if name in kwargs:

            if type((value := kwargs[name])) is valid_type:
                return value
            elif not necessary and type(kwargs[name]) is NoneType:
                return
            else:
                raise ValueError(f"kwargs {name} not {valid_type}")

        elif not necessary:
            return

        else:
            raise AttributeError(f"Not found kwargs {name}")

    def compose_command(self, **kwargs):
        """ Создаёт команды для mp3splt """

        command = f""" "{self.path_mp3splt}" """

        output_file = self.init_argument(kwargs, "output_file", str)
        name = self.init_argument(kwargs, "name", str)
        time_start = self.init_argument(kwargs, "time_start", str)
        time_end = self.init_argument(kwargs, "time_end", str)

        number = self.init_argument(kwargs, "number", int, necessary=False)
        author = self.init_argument(kwargs, "author", str, necessary=False)

        command += f""" {output_file} """
        command += f""" {time_start} """
        command += f""" {time_end} """
        command += f""" -o "{name}" """

        sub_command = " -g ["
        sub_command += f"""@t="{name}","""

        if author:
            sub_command += f"""@a="{author}","""

        if number:
            sub_command += f"""@N={number},"""

        sub_command += "] "
        command += sub_command
        command += f""" -d "{self.path_save_to}" """

        return command
