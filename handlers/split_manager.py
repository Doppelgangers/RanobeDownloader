import os

import mutagen
from mutagen.mp3 import MP3


class SplitManager:

    def __init__(self, path_mp3splt: str, root_folder: str = ''):
        self.path_mp3split = path_mp3splt

        if root_folder:
            self.root_folder = root_folder
        else:
            self.root_folder = os.getcwd()

    @staticmethod
    def get_duration(file_name: str = '1.mp3') -> int:
        """Узнаёт длительность аудиофайла"""
        # Узнаёт длительность аудиокомпозиции по имении файла
        audio = MP3(filename=file_name)
        duration = round(audio.info.length)
        return duration

    @staticmethod
    def converter_time_mmss(sec: int) -> str:
        """ Преобразование секунд в время в минты+секунды 156сек = 2:36 """
        if type(sec) == int:
            return str(sec // 60) + '.' + str(sec % 60)
        else:
            raise TypeError(f"""converter_time_mmss accepts only the integer value""")

    def compose_command(self, input_filename: str, name: str, time_start: str, time_end: str, folder_name) -> str:
        """ Создаёт команду для mp3splt """

        # Указываем входной файл и временые отрезки
        command = f"""{os.path.join(self.path_mp3split, 'mp3splt')} {input_filename}.mp3 {time_start} {time_end}"""

        # Имя файла
        # command += f""" -o @t="{name}" """
        command += f""" -o "{name}" """

        # Название композиции
        command += f""" -g [@t="{name}"] """

        # Путь сохранения файла
        command += f""" -d "{os.path.join(self.root_folder, folder_name)}" """

        return command

    def create_commands(self, offsets_and_names: list, folder_name: str, number_downloaded_file: int) -> list:
        """ Создацние списка команд для утилиты разделения """
        offset = 0
        current_file = 1
        max_duration = self.get_duration('1.mp3')
        command_list = []

        for i in range(len(offsets_and_names)):

            if (offsets_and_names[i]['offset'] - offset) >= max_duration:
                current_file += 1
                offset = offsets_and_names[i]['offset']
                try:
                    max_duration = self.get_duration(str(current_file) + '.mp3')
                except mutagen.MutagenError as e:
                    raise mutagen.MutagenError(e)

            start = offsets_and_names[i]['offset'] - offset

            try:
                end = offsets_and_names[i + 1]['offset'] - offset
            except IndexError:
                end = max_duration

            time_start = self.converter_time_mmss(start)
            time_end = self.converter_time_mmss(end)

            command = self.compose_command(input_filename=str(current_file),
                                           name=offsets_and_names[i]['name'],
                                           time_start=time_start,
                                           time_end=time_end,
                                           folder_name=folder_name
                                           )

            command_list.append(command)

        for i in range(number_downloaded_file):
            command_list.append(f'del {i + 1}.mp3')
        command_list.append('del command.bat')

        return command_list

    def run_cmd (self):
        # Переходим в текущюю деректорию
        os.chdir("\\".join(__file__.split("\\")[:-2]))
        # Запускаем созданный скрипт
        os.startfile("command.bat")

    def create_cmd(self, commands: list, run_after_creation: bool = True):
        """ Создание и консольной утилиты """
        with open(r"command.bat", "w", encoding="cp1251") as file:
            file.write('chcp 1251 >nul \n')
            # Переходим к месту расположению этого скрпипта
            file.write('cd ' + "\\".join(__file__.split("\\")[:-2]) + ' \n')
            # Записываем команды из массива
            for command in commands:
                # Записываем комманды для утилиты mp3splt
                file.write(command + "\n")

        if run_after_creation:
            self.run_cmd()




