import pyfiglet

from multiprocessing import freeze_support

from handlers import Browser, ParserAkniga, Checking_dependencies, SplitManager, DownloaderAudio


def main():
    Checking_dependencies.test()

    print(pyfiglet.figlet_format(" R A N O B E  ", font='doom'))

    url = input('Введите URL на аудиокнигу сайта akniga.org: ')

    browser = Browser()
    html_page = browser.get_page_akniga(url=url)

    print('Сайт получен')

    parser = ParserAkniga(html_code=html_page)
    root_url = parser.get_root_link()
    title = parser.get_title()
    map_akniga = parser.get_audio_map()
    author = parser.get_author()

    print(f"Название: {title}")
    print(f"Автор: {author}")

    loader = DownloaderAudio(base_url=root_url)
    loader.multiprocessing_download_all()

    print("Аудиофайлы загруженны")

    splitter = SplitManager(use_config_manager=True)

    commands = splitter.create_commands(offsets_and_names=map_akniga, folder_name=title, number_downloaded_file=loader.downloaded_mp3, author=author)
    splitter.create_cmd(commands)

    print(pyfiglet.figlet_format("E N D", font='doom'))


if __name__ == '__main__':
    freeze_support()
    main()
