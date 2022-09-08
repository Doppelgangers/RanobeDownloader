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


class WebDriver_Manager:

    def download_chrome_driver(self):

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

        if not "." in vers_chrome:
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

    def __init__(self , executable_path_chromedriwer = 'chromedriver.exe' ):
        self.options = self.create_browser_options()

    def create_browser_options(self, background_mode: bool = True , hide_images: bool = True, skip_wait_load_page: bool = True) -> webdriver.ChromeOptions:
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
        try:
            driver = webdriver.Chrome( options = self.options )

        except selenium_exceptions.SessionNotCreatedException as e:
            if ('This version of ChromeDriver' in e.args[0]):
                print(e.args[0] , "Обновите ChromeDriver в  настройках")
                exit()

        except selenium_exceptions.WebDriverException as e:
            if (error := e.args[0]) == 'unknown error: cannot find Chrome binary':
                print("Google Chrome не найдён в пути по умолчанию\nУстановите google crome.")
                exit()

        except Exception as e:
            print("Произошла ошибка\n\n" , e.args[0])
            exit()

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(    EC.presence_of_element_located((By.CSS_SELECTOR, 'audio[src]'))   )
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
            print("Произошла ошибка\n\n" , e.args[0])
            exit()

        html = driver.page_source
        driver.close()
        driver.quit()
        return html

class ParserAkniga:
    soup = None
    def __init__(self, html_code ):
        self.soup = BeautifulSoup(html_code, "lxml")

    def get_root_link(self) -> str:
        audio_blocks = self.soup.findAll('audio')
        for i in range(len(audio_blocks)):
            try:
                print( f"Основа ссылок для скачивания {audio_blocks[i]['src']}")
                return audio_blocks[i]['src']
            except KeyError:
                pass
    def get_title(self) -> str:
        return self.soup.find('h1', class_= 'caption__article-main').text
    def get_list(self) -> list:
        # Получает имена всех аудиокомпозиций и их отступы
        bookList = []

        item = self.soup.findAll(class_="chapter__default")
        name = self.soup.findAll(class_="chapter__default--title")
        item.pop(0)
        name.pop(0)

        for i in range(len(item)):
            bookList.append(
                {
                'name': name[i].text,
                'offset': item[i]['data-pos']
                }
            )

        # [ {'name' : "Name 1" , 'offset' : "0" } ... ]
        return bookList






def test_url(url):
    # Функция проверяет работоспособность url и возвращает статус страницы
    try:
        data = requests.get(url, stream=True, timeout=2, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'})
        status_code = data.status_code
        return status_code
    except Exception:
        return 407

def numToStr(num: int):
    # Утилита для преобразования числа в строку номер , например число 1 или 2 будет преобразованно в '01' или '02' соответственно
    string = ''
    if len(str(num)) == 1:
        string = string + '0' + str(num)
    else:
        string = str(num)
    return string

def cheker(base_url):
    valid_links = []
    num = 1
    while True:
        url = base_url.replace(',,/01', ',,/' + numToStr(num))
        code = test_url(url)

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


def download_one(data):
    url, file_name = data

    try:
        file = requests.get(url, stream=True, timeout=3, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'})
    except requests.exceptions.Timeout:
        print("Error enter , reconect")
        download_one(data)

    print('Download', url)

    ch = 0
    with open(str(file_name) + '.mp3', 'wb') as f:
        for chank in file.iter_content(chunk_size=1024 * 1024):
            if chank:
                ch = ch + 1
                # print(ch)
                f.write(chank)

    print("Downloaded: " + str(file_name) + '.mp3')



def multiprocessing_download_all(url_first_download_link):
    links = cheker(url_first_download_link)
    with Pool(processes=os.cpu_count()) as pool:
        pool.map(download_one, links)

    return len(links)


def getDuration(file_name = '1.mp3'):
    # Узнаёт длительность аудиокомпозиции по имении файла
    f = MP3(file_name)
    secs = round(f.info.length)
    return secs


def converterTimeMMSS(sec):
    # Преобразование секунд в время в минты+секунды 156сек = 2:36
    time = ''
    time = time + str(sec // 60) + '.' + str(sec % 60)
    return time

def splitCMD( command_list: list ):
    # Создание и запуск утилиты на разрезку файлов
    with open(r"command.bat", "w") as file:
        # Включаем кодировку с поддержкой русского языка
        file.write('chcp 1251 >nul \n')
        # Переходим к месту расположению этого скрпипта
        file.write('cd ' + os.path.dirname(os.path.abspath(__file__)) + ' \n')
        # Записываем команды из массива
        for i in range(int(len(command_list))):
            # Записываем комманды для утилиты mp3splt
            file.write(command_list[i] + ' \n')

    # Переходим в текущюю деректорию
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Запускаем созданный скрипт
    os.startfile("command.bat")


def cerate_command_split(array: list, folder_name: str, number_downloaded_file: int , path_mp3split: str) -> list:
    # Создацние списка команд для утилиты разделения
    # Принимает array , список имён и отступов
    # Результатом работы скрипта является список команд для mp3split
    offsets = 0
    this_file = 1
    max_duratin = getDuration('1.mp3')

    command_list = []
    for i in range( len(array) ):

        if ( int(array[i]['offset']) - offsets) >= max_duratin:
            this_file += 1
            offsets = int(array[i]['offset'])
            try:
                max_duratin = getDuration(str(this_file) + '.mp3')
            except mutagen.MutagenError:
                return

        start = int(array[i]['offset']) - offsets

        try:
            end = int(array[i + 1]['offset']) - offsets
        except IndexError:
            end = max_duratin
        time_start = converterTimeMMSS(start)
        time_end = converterTimeMMSS(end)

        #Указываем входной файл и временые отрезки
        command = f"{os.path.join(path_mp3split , 'mp3splt')}  {str(this_file)}.mp3 {str(time_start)} {str(time_end)}"

        # Имя файла
        command += f""" -o @t="{array[i]['name']}" """

        # Название композиции
        command += f""" -g [@t="{array[i]['name']}"] """

        root_folder = CONFIG['SAVE_TO']
        command += f""" -d "{os.path.join( root_folder, folder_name)}" """

        command_list.append(command)

    for i in range( number_downloaded_file ):
        num = i + 1
        command_list.append(f'del {num}.mp3')
    command_list.append('del command.bat')
    return command_list

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
                    ConfigManager.edit_config("MP3SPLT_PATH" , input("\n\n\nВведите путь к mp3slpt \nПример: D:\programs\mp3splt\n\nПуть: ") )
                    CONFIG = ConfigManager.get_configs()
                case "3":
                    exit()
                case _:
                    print("Такого действия нет.")

            if os.path.exists( os.path.join( CONFIG["MP3SPLT_PATH"] , 'mp3splt.exe' ) ):
                break
#=======================================================================================================================
    if not os.path.exists(CONFIG["SAVE_TO"]):
        ConfigManager.edit_config("SAVE_TO", '')

    if not os.path.exists( os.path.join( os.getcwd() , 'chromedriver.exe' ) ):
        download_chrom_driver()

class Validator:
    @classmethod
    def mp3splt(cls, value):
        if os.path.exists( os.path.join( value , 'mp3splt.exe' ) ):
            return True
        else:
            print(f"По пути {value} не был обнаружен файл mp3.splt.exe")
            return False
    @classmethod
    def save_to(cls , value):
        if os.path.exists( value ):
            return True
        else:
            print(f"По пути {value} папки не существует.")
            return False
def edit_config(key , value , validator):
    global CONFIG

    while True:
        if value == "stop":
            return

        if validator(value) :
            ConfigManager.edit_config(key , value)
            CONFIG = ConfigManager.get_configs()
            return
        value = input("\nВведите корректный путь или введите stop, что бы выйти\nВвод: ")
def settings_menu():
    global CONFIG
    print( '\n',pyfiglet.figlet_format("S e t t i n g s", font='doom') )

    while True:
        print(f"""
============================================= Н А С Т Р О Й К И ========================================================
1) Изменить путь к mp3splt === { '[=EMPTY=]' if ( (path:=CONFIG['MP3SPLT_PATH']) == '') else path } 
2) Изменить путь сохранения папкок с аудиокнигой === { '[=EMPTY=]' if ( (path:=CONFIG['SAVE_TO']) == '')  else  path } 
3) Вернуться
========================================================================================================================
""")
        match input("Выберете действие: "):
            case '1':
                edit_config( 'MP3SPLT_PATH' , input("\nВведите путь к mp3splt.exe\nПример: D:\programs\mp3splt\n(Для отмены введеите: stop)\n\nВвод:  "), Validator.mp3splt)
            case '2':
                edit_config( 'SAVE_TO' , '\nУкажите куда сохранять папки с аудиокнигами\nПример: C:/Users/root/Desktop\n(Для отмены введеите: stop)\n\nВвод: ', Validator.save_to)
            case '3':
                return
            case _:
                print("Такой команды нет")



def main():
    global CONFIG
    checking_dependencies()
    print(pyfiglet.figlet_format(" R A N O B E  ", font='doom'))
    print('Что бы открыть настройки введите: settings\n')

    url = input('Введите URL на аудиокнигу сайта akniga.org: ')

    if url.strip() == "settings":
        settings_menu()
        main()

    dirSave = input('Введите название папки в которую будет сохранено всё: ')

    html = getHTML(url=url)

    downloadURL = getSRC(html)
    title = getTitle(html)

    if dirSave == "0":
        dirSave = title

    numbers_files = multiprocessing_download_all(downloadURL)


    print('Downlowded : ' + str(numbers_files) + ' files')

    listFiles = getList(html)
    os.path.join(CONFIG['MP3SPLT_PATH'], 'mp3splt')
    commands = cerate_command_split(array=listFiles, folder_name=dirSave, number_downloaded_file=numbers_files, path_mp3split=CONFIG['MP3SPLT_PATH'])

    splitCMD(command_list=commands)

    print(pyfiglet.figlet_format("E N D", font='doom'))



if __name__ == '__main__':
    CONFIG = ConfigManager.get_configs()
    # main()
    download_chrome_driver()

