import time
import requests
from bs4 import BeautifulSoup

from mutagen.mp3 import MP3
from selenium import webdriver
import os


def getHTML(url):
    #Получает html в котором сожержится audio
    #Вход ссылка
    #Выход html
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        html = driver.page_source
        return html
    except Exception as a:
        print(a)
        return False
    finally:
        driver.close()


def getSRC(html):
    #Парсит html контент в поисках ссылки на audio
    #Вход html
    #Выход ссылка на аудиофаил
    soup = BeautifulSoup(html, "lxml")
    el = soup.findAll('audio')
    for i in range( len(el) ):
        try:
            print('LINK = '+ el[i]['src'] )
            return el[i]['src']
        except:
            pass


def getList(html):
    #Получает имена всех аудиокомпозиций и их отступы
    #Вход html
    #Выход списоок имя аудиофайла и его отступ
    bookList = []
    soup = BeautifulSoup(html, "lxml")
    item = soup.findAll(class_="chapter__default")
    name = soup.findAll(class_="chapter__default--title")
    item.pop(0)
    name.pop(0)
    for i in range(len(item)):
        print(item[i]['data-pos'])
        print( name[i].text )
        bookList.append({
        'name':   name[i].text,
        'offset': item[i]['data-pos']
        })
    return bookList

def numToStr(num = 0):
    #Утилита для преобразования числа в строку номер , например число 1 или 2 будет преобразованно в '01' или '02' соответственно
    string = ''
    if len( str(num) ) == 1:
        string = string + '0' + str(num)
    else: string = str(num)
    return string

def downloadAll(base_url):
    #Загрузака всех аудио файлов с текущего сайта
    #Вход , ссылка на афудио
    #Выход , количество скаченных файлов
    i = 0
    error = 0
    while True:
        i = i + 1
        url = base_url.replace(',,/01', ',,/' + numToStr(i))
        try:
            file = requests.get(url , stream=True)
        except:
            if error<10:
                error = error + 1
                print('Error connect ... ')
                time.sleep(2)
                print('Reconnect')
                i = i - 1
                continue
                # file = requests.get(url , stream=True)
            else:
                print('Error , script is STOPed')
                return

        if file.status_code != 200:
            print("is_UNSET --> " + url)
            return i - 1

        print("is_set --> " + url)

        print('Download')

        try:
            ch = 0
            with open(str(i)+'.mp3', 'wb') as f:
                for chank in file.iter_content(chunk_size=1024 * 1024):
                    if chank:
                        ch = ch + 1
                        print(ch)
                        f.write(chank)
            print( "Downloaded: " + str(i))
        except:
            print ('Error download: ' + url)

def getDuration( file_name ):
    #Узнаёт длительность аудиокомпозиции по имении файла
    f = MP3('1.mp3')
    secs = round(f.info.length)
    return secs


def converterTimeMMSS(sec):
    #Преобразование секунд в время в минты+секунды 156сек = 2:36
    time = ''
    time = time + str( sec//60 ) + '.' + str( sec%60 )
    return time

def splitCMD(path_mp3split = 'C:\mp3splt' , command_list=[] ):
    #Создание и запуск утилиты на разрезку файлов
    with open(r"command.bat", "w") as file:
        # Включаем кодировку с поддержкой русского языка
        file.write('chcp 1251 >nul \n')
        # Переходем к сплитеру
        file.write('cd ' + path_mp3split + ' & .\mp3splt.exe' + ' \n')
        # Переходим к месту расположению этого скрпипта
        file.write( 'cd '+ os.path.dirname(os.path.abspath(__file__)) +  ' \n'  )
        #Записываем команды из массива
        for i in range( int( len( command_list ) ) ):
            print('--Writed split command '+ str(i+1) )
            # Создаём комманду для разделения
            file.write(command_list[i] + ' \n')


    # Переходим вы текущюю деректорию
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #Запускаем созданный скрипт
    os.startfile("command.bat")


def cerate_command_split(array='' , name_dir = ""):
    # Создацние списка команд для утилиты разделения
    # Принимает name_dir -> если указанно то сохраняет в папку с указанным именем 1
    # Принимает array , список имён и отступов
    # Результатом работы скрипта является список команд для mp3split
    offsets = 0
    this_file = 1
    max_duratin = getDuration('1.mp3')

    command_list = []
    for i in range( int( len( array ) ) ):

        if (int(array[i]['offset'])-offsets) >= max_duratin:
            this_file = this_file + 1
            offsets =  int(array[i]['offset'])
            try:
                max_duratin = getDuration(str(this_file)+'.mp3')
            except:
                print('End')
                return

        start = int(array[i]['offset']) - offsets
        try:
            end = int(array[i+1]['offset']) - offsets
        except:
            end = max_duratin
        time_start = converterTimeMMSS(start)
        time_end = converterTimeMMSS(end)
        command = f"mp3splt {str(this_file)}.mp3 {str(time_start)} {str(time_end)} -o \"{array[i]['name']}\"  "
        command = command + f" -g [@t=\"{array[i]['name']}\"] "
        if len(name_dir) > 1:
            command = command + ' -d ' + '"'+name_dir +'"'
        command_list.append(command)
        print(command_list[i])
    print('END create commcnd for mp3split')
    return command_list

def clear(max):
    #Удаляет временные файлы
    for i in range( int( max ) ):
        try:
            os.remove(f'{i+1}.mp3')
            print(f'Delated {i+1}.mp3 ')
        except:
            print('ERROR DEL')
    try:
        os.remove('command.bat')
    except:
        print("error { remove('command.bat') }")


def main():
    url = input('Введите URL на аудиокнигу сайта akniga.org: ')
    dirSave = input('Введите название папки в которую будет сохранено всё: ')
    html = getHTML(url=url)
    downloadURL = getSRC(html)
    numbers_files = downloadAll(downloadURL)
    print( 'Downlowded : ' +  str(numbers_files) + ' files')
    listFiles = getList(html)

    commands = cerate_command_split(listFiles , name_dir=dirSave)
    splitCMD(path_mp3split='C:\mp3splt' , command_list= commands)

    d=input("Удалить файл  Y/N: ")
    if d =='y' or d=='Y':
        clear(numbers_files)
    elif d== 'n' or d=='N':
        print('End')





if __name__ == '__main__':
    main()





