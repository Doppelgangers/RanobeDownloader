import os
import time
import zipfile
from multiprocessing import Pool

from settings import ConfigManager

import mutagen
import pyfiglet
import requests
from mutagen.mp3 import MP3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WebDriverManager:

    @staticmethod
    def download_chrome_driver():

        if os.path.exists(os.path.join(os.getcwd(), "chromedriver.exe")):
            os.remove('chromedriver.exe')
            time.sleep(0.5)

        chrome_info_file = os.path.expandvars(r"%localappdata%/Google/Chrome/User Data/Last Version")

        if not os.path.exists(chrome_info_file):
            with open(chrome_info_file, 'r') as f:
                vers_chrome = f.readline()

        else:
            print("""
            Не удалось определить версию вашего браузера google chrome. 
            Если у все нет google chrome то его необходимо установить. 

            Введите версию ваешго google chrome вручную.
            Пример: 105.0.5195.54

            """)
            vers_chrome = input("Ваша версия: ").strip()

        if "." not in vers_chrome:
            print(f"Версия {vers_chrome} указанна не корректно")
            return False

        vers_chrome = vers_chrome.split('.')[:-1]
        vers_chrome = '.'.join(vers_chrome)

        vers = requests.get(f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{vers_chrome}')
        if (errorcode := vers.status_code) == 404:
            print(
                f"Error: {errorcode}\nТакой версии браузера не найдено\nВведите версию корректно или скачайте webdriver под ваш GoogleChrome самостоятельно(поместить в {os.getcwd()} ).")
            return False

        file = requests.get(f"https://chromedriver.storage.googleapis.com/{vers}/chromedriver_win32.zip", stream=True,
                            timeout=3)

        if (errorcode := file.status_code) == 404:
            print(
                f"Error: {errorcode}\nВерсии chromedriver {vers_chrome} не найдено\nПопробуйте загрузить webdriver под ваш GoogleChrome самостоятельно(поместить в {os.getcwd()} ).")
            return False

        # ===Загрузка=архива=с=драйвером============================================================================
        with open('chromedriver.zip', "wb") as f:
            for chank in file.iter_content(chunk_size=1024 * 1024):
                if chank:
                    f.write(chank)

        # ===Распаковка=архива=с=драйвером============================================================================
        with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
            zip_ref.extractall()

        os.remove('chromedriver.zip')
        print(f"Downloaded chromedriver: v{vers}")
        return True


class Browser:
    options = None

    def __init__(self):
        self.options = self.create_browser_options()

    @staticmethod
    def create_browser_options(background_mode: bool = True, hide_images: bool = True,
                               skip_wait_load_page: bool = True) -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        if hide_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

        if background_mode:
            options.headless = True

        if skip_wait_load_page:
            caps = DesiredCapabilities().CHROME
            caps["pageLoadStrategy"] = "none"
        return options

    def get_akniga(self, url: str):
        driver = ''
        try:
            driver = webdriver.Chrome(options=self.options)

        except selenium_exceptions.SessionNotCreatedException as e:
            if 'This version of ChromeDriver' in e.args[0]:
                print(e.args[0], "Обновите ChromeDriver в  настройках")
                exit()

        except selenium_exceptions.WebDriverException as e:
            if (error := e.args[0]) == 'unknown error: cannot find Chrome binary':
                print(f"{error}\nGoogle Chrome не найдён в пути по умолчанию\nУстановите google chrome.")
                exit()

        except Exception as e:
            print("Произошла ошибка\n\n", e.args[0])
            exit()

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'audio[src]')))
        except selenium_exceptions.TimeoutException:
            print(f"""
===================================================

Не удалось получить доступ к сайту.

Возможные причины ошибки:
    • Нет подключения к интернуту/сайт не доступен
    • Слишком частые запросы к сайту
    • Неверный url

===================================================
        """)
            exit()
        except Exception as e:
            print("Произошла ошибка\n\n", e.args[0])
            exit()

        html = driver.page_source
        driver.close()
        driver.quit()
        return html


class ParserAkniga:
    soup = None

    def __init__(self, html_code):
        self.soup = BeautifulSoup(html_code, "lxml")

    @staticmethod
    def get_html_for_file(filename):
        html_code = ""
        with open(filename, 'r', encoding="utf-8") as f:
            html_list = f.readlines()
        for line in html_list:
            html_code += line
        return html_code

    def get_root_link(self) -> str:
        audio_blocks = self.soup.findAll('audio')
        for i in range(len(audio_blocks)):
            try:
                # print(f"Основа ссылок для скачивания {audio_blocks[i]['src']}")
                return audio_blocks[i]['src']
            except KeyError:
                pass

    def get_title(self) -> str:
        return self.soup.find('h1', class_='caption__article-main').text

    def get_audio_map(self) -> list:
        # Получает имена всех аудиокомпозиций и их отступы
        data = []

        item = self.soup.findAll(class_="chapter__default")
        name = self.soup.findAll(class_="chapter__default--title")
        item.pop(0)
        name.pop(0)

        for i in range(len(item)):
            data.append(
                {
                    "name": name[i].text,
                    "offset": int(item[i]['data-pos'])
                }
            )

        # [ {'name' : "Name 1" , 'offset' : "0" } ... ]
        # name:str , offset: int
        return data


class DownloaderAudio:
    base_url = ''

    def __init__(self, base_url):
        self.base_url = base_url

    @staticmethod
    def num_to_str(number: int):
        # Преобразует число в строку c нулём , например число 1 или 2 будет преобразованно в '01' или '02' соответственно
        string_number = ''
        if len(str(number)) == 1:
            string_number = string_number + '0' + str(number)
        else:
            string_number = str(number)
        return string_number

    def multiprocessing_download_all(self):
        links = self.cheker()
        with Pool(processes=os.cpu_count()) as pool:
            pool.map(self.download_one, links)
        return len(links)

    def download_one(self, data):
        url, file_name = data
        file = ''
        try:
            file = requests.get(url, stream=True, timeout=3, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'})
        except requests.exceptions.Timeout:
            print("Error enter , reconnect")
            self.download_one(data)
        print('Download', url)
        ch = 0
        with open(str(file_name) + '.mp3', 'wb') as f:
            for chank in file.iter_content(chunk_size=1024 * 1024):
                if chank:
                    ch = ch + 1
                    # print(ch)
                    f.write(chank)

        print("Downloaded: " + str(file_name) + '.mp3')

    def cheker(self):
        valid_links = []
        num = 1
        while True:
            url = self.base_url.replace(',,/01', ',,/' + self.num_to_str(num))
            code = self.test_url(url)

            match code:
                case 200:
                    print("Link is valide : ", num)
                    valid_links.append([url, num])
                    num += 1
                case 404:
                    return valid_links
                case 407:
                    print('Reconnecting (407) . . .')
                case _:
                    print(code)

    def test_url(self, url):
        # Функция проверяет работоспособность url и возвращает статус страницы
        try:
            data = requests.get(url, stream=True, timeout=2, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'})
            status_code = data.status_code
            return status_code
        except Exception:
            return 407


class SplitManager:
    path_mp3split = ''
    root_folder = ''

    def __init__(self, path_mp3splt, root_folder=''):
        self.path_mp3split = path_mp3splt

        if root_folder:
            self.root_folder = root_folder
        else:
            self.root_folder = os.getcwd()

    @staticmethod
    def get_duration(file_name: str = '1.mp3') -> int:
        # Узнаёт длительность аудиокомпозиции по имении файла
        audio = MP3(filename=file_name)
        duration = round(audio.info.length)
        return duration

    @staticmethod
    def converter_time_mmss(sec) -> str:
        # Преобразование секунд в время в минты+секунды 156сек = 2:36
        time = ''
        time = time + str(sec // 60) + '.' + str(sec % 60)
        return time

    def compose_command(self, input_filename: str, name: str, time_start: str, time_end: str, folder_name):
        # Указываем входной файл и временые отрезки
        command = f"""{os.path.join(self.path_mp3split, 'mp3splt')} {input_filename}.mp3 {time_start} {time_end}"""

        # Имя файла
        command += f""" -o @t="{name}" """

        # Название композиции
        command += f""" -g [@t="{name}"] """

        command += f""" -d "{os.path.join(self.root_folder, folder_name)}" """

        return command

    def create_commands(self, offsets_and_names: list, folder_name: str, number_downloaded_file: int) -> list:
        # Создацние списка команд для утилиты разделения
        # Результатом работы скрипта является список команд для mp3split

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
                    raise Exception(e)

            start = offsets_and_names[i]['offset'] - offset

            try:
                end = offsets_and_names[i + 1]['offset'] - offset
            except IndexError:
                end = max_duration

            time_start = self.converterTimeMMSS(start)
            time_end = self.converterTimeMMSS(end)

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

    def start_cmd(self, commands: list):
        # Создание и запуск утилиты на разрезку файлов
        with open(r"command.bat", "w") as file:
            file.write('chcp 1251 >nul \n')
            # Переходим к месту расположению этого скрпипта
            file.write('cd ' + os.path.dirname(os.path.abspath(__file__)) + ' \n')
            # Записываем команды из массива
            for comand in commands:
                # Записываем комманды для утилиты mp3splt
                file.write(comand + '\n')

        # Переходим в текущюю деректорию
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        # Запускаем созданный скрипт
        os.startfile("command.bat")


def checking_dependencies():
    # Проверка существования mp3splt====================================================================================
    global CONFIG
    if not os.path.exists(os.path.join(CONFIG["MP3SPLT_PATH"], 'mp3splt.exe')):
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


class Validator:
    @classmethod
    def mp3splt(cls, folder_path):
        if os.path.exists(os.path.join(folder_path, 'mp3splt.exe')):
            return True
        else:
            print(f"По пути {folder_path} не был обнаружен файл mp3.splt.exe")
            return False

    @classmethod
    def save_to(cls, value):
        if os.path.exists(value):
            return True
        else:
            print(f"По пути {value} папки не существует.")
            return False


def edit_config(key, value, validator):
    global CONFIG

    while True:
        if value == "stop":
            return

        if validator(value):
            ConfigManager.edit_config(key, value)
            CONFIG = ConfigManager.get_configs()
            return
        value = input("\nВведите корректный путь или введите stop, что бы выйти\nВвод: ")


def settings_menu():
    global CONFIG
    print('\n', pyfiglet.figlet_format("S e t t i n g s", font='doom'))

    while True:
        print(f"""
============================================= Н А С Т Р О Й К И ========================================================
1) Изменить путь к mp3splt === {'[=EMPTY=]' if ((path := CONFIG['MP3SPLT_PATH']) == '') else path} 
2) Изменить путь сохранения папкок с аудиокнигой === {'[=EMPTY=]' if ((path := CONFIG['SAVE_TO']) == '') else path} 
3) Вернуться
========================================================================================================================
""")
        match input("Выберете действие: "):
            case '1':
                edit_config('MP3SPLT_PATH', input(
                    "\nВведите путь к mp3splt.exe\nПример: D:\programs\mp3splt\n(Для отмены введеите: stop)\n\nВвод:  "),
                            Validator.mp3splt)
            case '2':
                edit_config('SAVE_TO',
                            '\nУкажите куда сохранять папки с аудиокнигами\nПример: C:/Users/root/Desktop\n(Для отмены введеите: stop)\n\nВвод: ',
                            Validator.save_to)
            case '3':
                return
            case _:
                print("Такой команды нет")


def main():
    pass
    # global CONFIG
    # checking_dependencies()
    # print(pyfiglet.figlet_format(" R A N O B E  ", font='doom'))
    # print('Что бы открыть настройки введите: settings\n')
    #
    # url = input('Введите URL на аудиокнигу сайта akniga.org: ')
    #
    # if url.strip() == "settings":
    #     settings_menu()
    #     main()
    #
    # dirSave = input('Введите название папки в которую будет сохранено всё: ')
    #
    # html = getHTML(url=url)
    #
    # downloadURL = getSRC(html)
    # title = getTitle(html)
    #
    # if dirSave == "0":
    #     dirSave = title
    #
    # numbers_files = multiprocessing_download_all(downloadURL)
    #
    #
    # print('Downlowded : ' + str(numbers_files) + ' files')
    #
    # listFiles = getList(html)
    # os.path.join(CONFIG['MP3SPLT_PATH'], 'mp3splt')
    # commands = cerate_command_split(array=listFiles, folder_name=dirSave, number_downloaded_file=numbers_files, path_mp3split=CONFIG['MP3SPLT_PATH'])
    #
    # splitCMD(command_list=commands)
    #
    # print(pyfiglet.figlet_format("E N D", font='doom'))


if __name__ == '__main__':
    splitter = SplitManager('', 'D:/')
    command = splitter.compose_command('1', 'shield-hero', '1.22', "2.44", 'akniga')
    print(command)