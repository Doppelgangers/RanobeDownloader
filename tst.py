import requests


def numToStr(num = 0):
    #Утилита для преобразования числа в строку номер , например число 1 или 2 будет преобразованно в '01' или '02' соответственно
    string = ''
    if len( str(num) ) == 1:
        string = string + '0' + str(num)
    else: string = str(num)
    return string


num = 1
while True:
    data = numToStr(num)

    r = requests.get(f'https://m2.akniga.club/b/63690/bUvZdqwKeBmPu59AJsisdg,,/{data}. Маруяма Куганэ - Паладин Святого Королевства. Часть 2.mp3' , stream=True)
    print(f'{data}  :  {r.status_code}')
    num += 1
