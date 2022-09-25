import pyfiglet

from multiprocessing import freeze_support

from handlers import Browser, ParserAkniga, Checking_dependencies, SplitManager, DownloaderAudio


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

    url = input('Введите URL на аудиокнигу сайта akniga.org: ')

    browser = Browser()
    html_page = browser.get_page_akniga(url=url)

    print('Сайт получен')

    parser = ParserAkniga(html_code=html_page)
    root_url = parser.get_root_link()
    title = parser.get_title()
    map_akniga = parser.get_audio_map()
    author = parser.get_author()

    print("\n")
    print(f"Название: {title}")
    print(f"Автор: {author}")
    print("\n")

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
    main()
