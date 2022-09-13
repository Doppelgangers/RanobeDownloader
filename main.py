import os
import sys

from handlers import Browser, ParserAkniga, ConfigManager, Checking_dependencies
from handlers import DownloaderAudio    #TODO: Обработать 407 при скачивании
from handlers import SplitManager   #TODO: Добавить args and kwargs


import pyfiglet




def checking_dependencies():
    # Проверка существования mp3splt====================================================================================

    if not os.path.exists( 'mp3splt.exe'):
        while True:
            print(
                """
= = = E R R O R = = =
Не найден путь к утилите mp3slpt, если утилита установлена укажите верный путь:
1) Использовать mp3splt по умолчанию
2) Указать путь
3) Выход 
""")
            key = input("Выберете действие: ")

            match key:
                case "1":
                    print('Выбран mp3splt по умолчанию')
                    ConfigManager.edit_config("MP3SPLT_PATH", 'mp3splt')
                case "2":
                    ConfigManager.edit_config("MP3SPLT_PATH", input(
                        "\n\n\nВведите путь к mp3slpt \nПример: D:\programs\mp3splt\n\nПуть: "))
                    CONFIG = ConfigManager.get_configs()
                case "3":
                    exit()
                case _:
                    print("Такого действия нет.")

            if os.path.exists(os.path.join(CONFIG["MP3SPLT_PATH"], 'mp3splt.exe')):
                break
    # =======================================================================================================================
    if not os.path.exists(CONFIG["SAVE_TO"]):
        ConfigManager.edit_config("SAVE_TO", '')

    if not os.path.exists(os.path.join(os.getcwd(), 'chromedriver.exe')):
        pass
        # download_chrom_driver()


def main():
    Checking_dependencies.test()
    conf_mng = ConfigManager()




    print(pyfiglet.figlet_format(" R A N O B E  ", font='doom'))
    url = input('Введите URL на аудиокнигу сайта akniga.org: ')

    browser = Browser()
    html_page = browser.get_page_akniga(url=url)

    print('Сайт получен')

    scraber = ParserAkniga(html_code=html_page)
    root_url = scraber.get_root_link()
    title = scraber.get_title()
    map_akniga = scraber.get_audio_map()

    print("Y")

    loader = DownloaderAudio(base_url=root_url)
    loader.multiprocessing_download_all()

    print("Скаченно")

    splitter = SplitManager(conf_mng.configs["MP3SPLT_PATH"], conf_mng.configs["SAVE_TO"])

    commands = splitter.create_commands(map_akniga, title, loader.downloaded_mp3)
    splitter.create_cmd(commands,False)


    print(pyfiglet.figlet_format("E N D", font='doom'))


if __name__ == '__main__':
    main()
