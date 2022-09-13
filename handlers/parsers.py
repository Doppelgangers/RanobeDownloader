from bs4 import BeautifulSoup


class ParserAkniga:
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
                return audio_blocks[i]['src']
            except KeyError:
                pass

    def get_title(self) -> str:
        return self.soup.find('h1', class_='caption__article-main').text

    def get_audio_map(self) -> list:
        """Получает список словарей с названием главы и отступами """
        """ [ {'name' : "Name 1" , 'offset' : 0 } ... ]"""
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

        return data
