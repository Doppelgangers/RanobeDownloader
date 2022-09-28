# import pyfiglet
import os
import time

# from multiprocessing import freeze_support

from handlers import Browser, ParserAkniga, Checking_dependencies, SplitManager, DownloaderAudio, ConfigManager


def edit_path(name_config: str):
    conf = ConfigManager()
    while True:
        value = input("Для выхода введите 0.\nВведите новый путь: ")
        if os.path.exists(value):
            conf.edit_config(name_config, value)
            print("Новый путь успешно установлен!")
            return
        elif value == "0":
            return
        else:
            print("Путь указан неверно.")


def settings():
    conf = ConfigManager()
    while True:
        print(f"""
        ============================== Выберете действие ========================>>
            Выберете что хотите изменить:

            1 - Востановить настройки по умолчанию.
            2 - Изменить путь сохранения файлов. (Текущий путь: {conf.configs.get("SAVE_TO")})
            3 - Системные настройки. 

            0 - Закрыть настрокйи.
        =========================================================================>>
        """)

        match input().strip():
            case "0":
                return
            case "1":
                if os.path.isfile("config.json"):
                    os.remove("config.json")
                if os.path.isfile("chromedriver.exe"):
                    os.remove("chromedriver.exe")
                if os.path.isdir("TEMP"):
                    os.rmdir("TEMP")
                print("Настройки по умолчанию были успешно установленны!")
            case "2":
                edit_path("SAVE_TO")
            case "3":
                while True:
                    print(f"""
                    ======================== Системные = настройки ==========================>>
                        Выберете что хотите изменить:
    
                        1 - Путь к временным файлам: {conf.configs.get("TEMP")}
                        2 - Путь к mp3slplt.exe: {conf.configs.get("MP3SPLT_PATH")}
    
                        0 - Назад.
                    =========================================================================>>
                    """)
                    match input().strip():
                        case "0":
                            break
                        case "1":
                            edit_path("TEMP")
                        case "2":
                            edit_path("MP3SPLT_PATH")
                        case _:
                            print("Такого параметра нет, введите число.")

            case _:
                print("Такого параметра нет, введите число.")


def main():
    Checking_dependencies.test()

    print(r"""
 ______    ___    _   _   _____  ______   _____   
 | ___ \  / _ \  | \ | | |  _  | | ___ \ |  ___|  
 | |_/ / / /_\ \ |  \| | | | | | | |_/ / | |__    
 |    /  |  _  | | . ` | | | | | | ___ \ |  __|   
 | |\ \  | | | | | |\  | \ \_/ / | |_/ / | |___   
 \_| \_| \_| |_/ \_| \_/  \___/  \____/  \____/  
""")

    print("""
Что бы открыть настройки введите вместо URL команду "settings".
Для выхода введите команду "exit"
    """)

    url = input('Введите URL на аудиокнигу сайта akniga.org: ').strip()

    if url.lower() == "settings":
        settings()
        return

    if url.lower() == "exit":
        return False

    if "https://akniga.org/" not in url:
        print("URL Должен начанаться с https://akniga.org/...")
        return

    browser = Browser()
    html_page = browser.get_page_akniga(url=url)

    if html_page is None:
        print("Такой страницы не существует , проверьте URL")
        return

    print('Сайт получен')

    parser = ParserAkniga(html_code=html_page)
    root_url = parser.get_root_link()
    title = parser.get_title()
    map_akniga = parser.get_audio_map()
    author = parser.get_author()

    print(f"\nНазвание: {title}")
    print(f"Автор: {author}\n")

    loader = DownloaderAudio(base_url=root_url)
    loader.download_all()

    print("Аудиофайлы загруженны")

    splitter = SplitManager(use_config_manager=True)

    commands = splitter.create_commands(offsets_and_names=map_akniga, folder_name=title, number_downloaded_file=loader.downloaded_mp3, author=author)

    splitter.create_cmd(commands)

    print(r"""
  _____   _   _  ______ 
 |  ___| | \ | | |  _  \
 | |__   |  \| | | | | |
 |  __|  | . ` | | | | |
 | |___  | |\  | | |/ / 
 \____/  \_| \_/ |___/  
 """)


if __name__ == '__main__':
    Flag = True
    while Flag:
        try:
            Flag = True if main() is None else False
        except Exception as e:
            print("Произошла ошибка! " , e)
