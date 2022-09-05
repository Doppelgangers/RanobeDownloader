import os
import sys
import zipfile
from multiprocessing import Pool

from settings import ConfigManager

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from mutagen.mp3 import MP3
import pyfiglet



def download_chrom_driver():

    chrome_info_file = os.path.expandvars(r"%localappdata%/Google/Chrome/User Data/Last Version")

    with open(chrome_info_file, 'r') as f:
        vers_chrome = f.readline()

    vers_chrome = vers_chrome.split('.')[:-1]
    vers_chrome = '.'.join(vers_chrome)

    vers = requests.get(f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{vers_chrome}').text

    try:
        file = requests.get(f"https://chromedriver.storage.googleapis.com/{vers}/chromedriver_win32.zip", stream=True, timeout=3)

        with open('chromedriver.zip' , "wb" ) as f:
            for chank in file.iter_content(chunk_size=1024 * 1024):
                if chank:
                    f.write(chank)
    except Exception as e:
        print(f"{e}\n\n\n\n\nВо время загрузки chromedriver произошла ошибка\nПопробуйте загрузить chromedriver для googlehrome в ручную.")
        raise Exception('Error download chromedriwer for your chrome browser.')
#     ============================================================================
#     Распаковка архива с драйвером
    with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
        zip_ref.extractall()
    os.remove('chromedriver.zip')
    print(f"Downloaded chromedriver: v{vers}")
    return True
def getHTML(url, bg=True):
    # Вход: ссылка на сайт
    # Условие ожидания: ждём 10 секунд ссылку на mp3 файл
    # Выход: html код страницы
    try:
        options = webdriver.ChromeOptions()

        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        options.add_argument("--disable-blink-features=AutomationControlled")

        options.headless = True

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"

        driver = webdriver.Chrome(options=options)

        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'audio[src]'))
        )

        html = driver.page_source
        return html

    except Exception as e:
        raise Exception(f"""
        {e}\n\n\n
        Не удалось получить доступ к HTML сайта.
        
        Возможные причины ошибки:
        • Нет подключения к интернуту
        • Не установлен google chrome
        • Установлена неправильная версия chromedriver.exe
        """)

    finally:
        driver.close()


def getSRC(html):
    # Парсит html контент в поисках ссылки на audio
    # Вход html
    # Выход ссылка на аудиофаил
    soup = BeautifulSoup(html, "lxml")
    el = soup.findAll('audio')
    for i in range(len(el)):
        try:
            print('LINK = ' + el[i]['src'])
            return el[i]['src']
        except Exception as e:
            pass


def getList(html):
    # Получает имена всех аудиокомпозиций и их отступы
    # Вход html
    # Выход списоок имя аудиофайла и его отступ
    bookList = []
    soup = BeautifulSoup(html, "lxml")
    item = soup.findAll(class_="chapter__default")
    name = soup.findAll(class_="chapter__default--title")
    item.pop(0)
    name.pop(0)
    for i in range(len(item)):
        # print(item[i]['data-pos'])
        # print( name[i].text )
        bookList.append({
            'name': name[i].text,
            'offset': item[i]['data-pos']
        })
    return bookList


def numToStr(num: int):
    # Утилита для преобразования числа в строку номер , например число 1 или 2 будет преобразованно в '01' или '02' соответственно
    string = ''
    if len(str(num)) == 1:
        string = string + '0' + str(num)
    else:
        string = str(num)
    return string


def test_url(url):
    # Функция проверяет работоспособность url и возвращает статус страницы
    try:
        data = requests.get(url, stream=True, timeout=2, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'})
        status_code = data.status_code
        return status_code
    except Exception:
        return 407


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
    except Exception as e:
        print("exept ", e)
        return False
    print('Download', url)
    try:
        ch = 0
        with open(str(file_name) + '.mp3', 'wb') as f:
            for chank in file.iter_content(chunk_size=1024 * 1024):
                if chank:
                    ch = ch + 1
                    # print(ch)
                    f.write(chank)
        print("Downloaded: " + str(file_name) + '.mp3')
    except:
        print('Error download: ' + url)


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


def splitCMD(path_mp3split: str = 'C:\mp3splt' , command_list: list = []):
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


def cerate_command_split(array: list, name_dir: str):
    # Создацние списка команд для утилиты разделения
    # Принимает name_dir -> если указанно то сохраняет в папку с указанным именем 1
    # Принимает array , список имён и отступов
    # Результатом работы скрипта является список команд для mp3split
    offsets = 0
    this_file = 1
    max_duratin = getDuration('1.mp3')

    command_list = []
    for i in range(int(len(array))):

        if (int(array[i]['offset']) - offsets) >= max_duratin:
            this_file = this_file + 1
            offsets = int(array[i]['offset'])
            try:
                max_duratin = getDuration(str(this_file) + '.mp3')
            except:
                print('End')
                return

        start = int(array[i]['offset']) - offsets
        try:
            end = int(array[i + 1]['offset']) - offsets
        except:
            end = max_duratin
        time_start = converterTimeMMSS(start)
        time_end = converterTimeMMSS(end)

        #Указываем входной файл и временые отрезки
        command = f"{ os.path.join(CONFIG['MP3SPLT_PATH'] , 'mp3splt') }  {str(this_file)}.mp3 {str(time_start)} {str(time_end)}"

        # Имя файла
        command = command + f" -o @t=\"{array[i]['name']}\""

        # Название композиции
        command = command + f" -g [@t=\"{array[i]['name']}\"] "

        command = command + ' -d ' + '"' + name_dir + '"'

        command_list.append(command)
        # print(command_list[i])

    #Исходя из последней команды узнаём номер последнего mp3 файла и удаляем все остальные
    # dat = command_list[-1]
    # dat = dat.split('.mp3')
    # dat = dat[0].replace('mp3splt', '').strip()
    # dat = int(dat)
    dat = int(command_list[-1].split('.mp3')[0].replace('mp3splt', '').strip())
    for i in range(dat):
        num = i + 1
        command_list.append(f'del {num}.mp3')
    command_list.append('del command.bat')
    return command_list

def checking_dependencies():
    # Проверка существования mp3splt====================================================================================
    global CONFIG
    if not os.path.exists( os.path.join( CONFIG["MP3SPLT_PATH"] , 'mp3splt.exe' ) ):
        while True:
            print(
"""
= = = E R R O R = = =
Не найден путь к утилите mp3slpt, если утилита установлена укажите верный путь:
1) Установить mp3.splt
2) Указать путь
3) Выход 
""")
            key = input("Выберете действие: ")

            match key:
                case "1":
                    os.startfile(os.path.join(os.getcwd(),'mp3splt_2.6.2_i386.exe'))
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
    numbers_files = multiprocessing_download_all(downloadURL)
    print('Downlowded : ' + str(numbers_files) + ' files')
    listFiles = getList(html)
    commands = cerate_command_split(listFiles, name_dir=dirSave)
    splitCMD(path_mp3split=r"C:\utils\mp3splt", command_list=commands)
    print(pyfiglet.figlet_format("E N D", font='doom'))



if __name__ == '__main__':
    CONFIG = ConfigManager.get_configs()
    main()
