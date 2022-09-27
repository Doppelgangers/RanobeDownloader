import os
import requests
from multiprocessing import Pool

from .config_manager import ConfigManager


class DownloaderAudio:
    base_url = ''
    downloaded_mp3 = 0

    def __init__(self, base_url):
        conf_mng = ConfigManager()
        self.path_temp = use_path if (use_path := conf_mng.configs.get("TEMP")) != "local" else os.path.join(os.getcwd(), "TEMP")
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
        self.downloaded_mp3 = len(links)
        return links

    def download_all(self):
        links = self.cheker()

        for link in links:
            while True:
                if self.download_one(data=link):
                    break
                else:
                    print("Загрузка была прерванна. Повтор загрузки.")
        self.downloaded_mp3 = len(links)
        return links

    def download_one(self, data):
        url, file_name = data

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'}
        try:
            with requests.get(url, stream=True, timeout=3, headers=headers) as file:

                print('Download', url)
                ch = 0
                with open(os.path.join(self.path_temp, str(file_name) + '.mp3'), 'wb') as f:
                    for chank in file.iter_content(chunk_size=1024 * 1024):
                        if chank:
                            ch = ch + 1
                            # print(ch)
                            f.write(chank)

                print("Downloaded: " + str(file_name) + '.mp3')
                return True
        except Exception as e:
            print("[def download_one] The download was interrupted!", e)
            return False
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

    @staticmethod
    def test_url(url):
        # Функция проверяет работоспособность url и возвращает статус страницы
        try:
            data = requests.get(url, stream=True, timeout=2, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.58'})
            status_code = data.status_code
            return status_code
        except requests.exceptions.Timeout:
            return 407
