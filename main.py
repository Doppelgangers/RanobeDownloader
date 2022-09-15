import os
import sys
import time

from handlers import Browser, ParserAkniga, ConfigManager, Checking_dependencies
from handlers import DownloaderAudio    #TODO: Обработать 407 при скачивании
from handlers import SplitManager   #TODO: Добавить args and kwargs


import pyfiglet


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
