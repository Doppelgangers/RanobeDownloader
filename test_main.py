import unittest

from main import ParserAkniga


class TestParserAkniga(unittest.TestCase):

    def test_get_root_link(self):
        html_page = ParserAkniga(ParserAkniga.get_html_for_file('test_akniga.html'))
        self.assertEqual(html_page.get_root_link(), r"https://m2.akniga.club/b/66331/WYCpcDymnxMSvu5NVIDyRg,,/01. Анеко Юсаги - Становление Героя Щита 21.mp3")

    def test_get_title(self):
        html_page = ParserAkniga(ParserAkniga.get_html_for_file('test_akniga.html'))
        self.assertEqual(html_page.get_title(), r"Анеко Юсаги - Становление Героя Щита 21")

    def test_get_audio_map(self):
        html_page = ParserAkniga(ParserAkniga.get_html_for_file('test_akniga.html'))
        true_list = [{'name': '01 Герой Щита v21 - Пролог 01', 'offset': 0}, {'name': '02 Герой Щита v21 - Пролог 02', 'offset': 901}, {'name': '03 Герой Щита v21 - Глава 01 01', 'offset': 1615}, {'name': '04 Герой Щита v21 - Глава 01 02', 'offset': 2232}, {'name': '05 Герой Щита v21 - Глава 02 01', 'offset': 3192}, {'name': '06 Герой Щита v21 - Глава 02 02', 'offset': 4281}, {'name': '07 Герой Щита v21 - Глава 03 01', 'offset': 4882}, {'name': '08 Герой Щита v21 - Глава 03 02', 'offset': 5618}, {'name': '09 Герой Щита v21 - Глава 04 01', 'offset': 6237}, {'name': '10 Герой Щита v21 - Глава 04 02', 'offset': 6979}, {'name': '11 Герой Щита v21 - Глава 05 01', 'offset': 7912}, {'name': '12 Герой Щита v21 - Глава 05 02', 'offset': 8945}, {'name': '13 Герой Щита v21 - Глава 06 01', 'offset': 9757}, {'name': '14 Герой Щита v21 - Глава 06 02', 'offset': 10242}, {'name': '15 Герой Щита v21 - Глава 06 03', 'offset': 10845}, {'name': '16 Герой Щита v21 - Глава 07 01', 'offset': 11578}, {'name': '17 Герой Щита v21 - Глава 07 02', 'offset': 12299}, {'name': '18 Герой Щита v21 - Глава 07 03', 'offset': 13214}, {'name': '19 Герой Щита v21 - Глава 08 01', 'offset': 14031}, {'name': '20 Герой Щита v21 - Глава 08 02', 'offset': 14765}, {'name': '21 Герой Щита v21 - Глава 09 01', 'offset': 15495}, {'name': '22 Герой Щита v21 - Глава 09 02', 'offset': 16363}, {'name': '23 Герой Щита v21 - Глава 09 03', 'offset': 17157}, {'name': '24 Герой Щита v21 - Глава 10 01', 'offset': 18034}, {'name': '25 Герой Щита v21 - Глава 10 02', 'offset': 19005}, {'name': '26 Герой Щита v21 - Глава 11', 'offset': 19570}, {'name': '27 Герой Щита v21 - Глава 12', 'offset': 20164}, {'name': '28 Герой Щита v21 - Глава 13', 'offset': 20978}, {'name': '29 Герой Щита v21 - Эпилог', 'offset': 21858}]
        self.assertEqual(html_page.get_audio_map(), true_list)

from main import DownloaderAudio

class TestDownloaderAudio(unittest.TestCase):

    def test_num_to_str(self):
        self.assertEqual('00', DownloaderAudio.num_to_str(0))
        self.assertEqual('01', DownloaderAudio.num_to_str(1))
        self.assertEqual('02', DownloaderAudio.num_to_str(2))
        self.assertEqual('03', DownloaderAudio.num_to_str(3))
        self.assertEqual('04', DownloaderAudio.num_to_str(4))
        self.assertEqual('05', DownloaderAudio.num_to_str(5))
        self.assertEqual('06', DownloaderAudio.num_to_str(6))
        self.assertEqual('07', DownloaderAudio.num_to_str(7))
        self.assertEqual('08', DownloaderAudio.num_to_str(8))
        self.assertEqual('09', DownloaderAudio.num_to_str(9))
        self.assertEqual('10', DownloaderAudio.num_to_str(10))
        self.assertEqual('11', DownloaderAudio.num_to_str(11))

from main import  SplitManager

class TestSplitManager(unittest.TestCase):

    def test_get_duration(self):
        self.assertEqual(SplitManager.get_duration("test_audio.mp3"), 765)

    def test_converter_time_mmss(self):
        self.assertEqual( SplitManager.converter_time_mmss(100), "1.40")

    def test_compose_command(self):
        splitter = SplitManager(path_mp3splt='', root_folder='D:/')
        command = splitter.compose_command('1', 'shield-hero', '1.22', "2.44", 'akniga')
        self.assertEqual(command, """mp3splt 1.mp3 1.22 2.44 -o @t="shield-hero"  -g [@t="shield-hero"]  -d "D:/akniga" """)


class TestWebDriverManager(unittest.TestCase):
