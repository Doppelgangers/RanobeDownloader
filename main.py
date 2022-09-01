import datetime
import time

import os
from multiprocessing import Pool

import pyfiglet
import requests
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def getHTML(url, bg=True):
    # Вход: ссылка на сайт
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
    except Exception as a:
        print(a)
        return False
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


def numToStr(num=0):
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


def getDuration(file_name):
    # Узнаёт длительность аудиокомпозиции по имении файла
    f = MP3('1.mp3')
    secs = round(f.info.length)
    return secs


def converterTimeMMSS(sec):
    # Преобразование секунд в время в минты+секунды 156сек = 2:36
    time = ''
    time = time + str(sec // 60) + '.' + str(sec % 60)
    return time


def splitCMD(path_mp3split='C:\mp3splt', command_list=[]):
    # Создание и запуск утилиты на разрезку файлов
    with open(r"command.bat", "w") as file:
        # Включаем кодировку с поддержкой русского языка
        file.write('chcp 1251 >nul \n')
        # Переходем к сплитеру
        file.write('cd ' + path_mp3split + ' & .\mp3splt.exe' + ' \n')
        # Переходим к месту расположению этого скрпипта
        file.write('cd ' + os.path.dirname(os.path.abspath(__file__)) + ' \n')
        # Записываем команды из массива
        for i in range(int(len(command_list))):
            # print('--Writed split command '+ str(i+1) )
            # Создаём комманду для разделения
            file.write(command_list[i] + ' \n')

    # Переходим вы текущюю деректорию
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Запускаем созданный скрипт
    os.startfile("command.bat")


def cerate_command_split(array='', name_dir=""):
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
        command = f"mp3splt {str(this_file)}.mp3 {str(time_start)} {str(time_end)}"

        # Имя файла
        command = command + f" -o @t=\"{array[i]['name']}\""

        # Название композиции
        command = command + f" -g [@t=\"{array[i]['name']}\"] "

        if name_dir:
            command = command + ' -d ' + '"' + name_dir + '"'
        else:
            command = command + ' -d ' + '"' + datetime.datetime.now() + '"'
        command_list.append(command)
        # print(command_list[i])

    dat = command_list[-1]
    dat = dat.split('.mp3')
    dat = dat[0].replace('mp3splt', '').strip()
    dat = int(dat)
    for i in range(dat):
        num = i + 1
        command_list.append(f'del {num}.mp3')
    command_list.append('del command.bat')

    return command_list


def main():
    print(pyfiglet.figlet_format(" R A N O B E  ", font='doom'))
    url = input('Введите URL на аудиокнигу сайта akniga.org: ')
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
    main()
