import os
import sys
import unittest

sys.path.insert(1, '..')
from handlers.split_manager import SplitManager


class TestSplitManager(unittest.TestCase):

    def test_init(self):
        splitter = SplitManager("mp3splt")
        self.assertEqual(splitter.path_temp, os.path.join(os.getcwd(), "TEMP"))
        self.assertEqual(splitter.path_save_to, os.getcwd())
        self.assertEqual(splitter.path_mp3split, "mp3splt")

    def test_get_duration(self):
        self.assertEqual(SplitManager.get_duration(os.path.join(f'{os.path.sep}'.join(__file__.split(os.path.sep)[:-1]), "test_file/1.mp3")), 503)

    def test_converter_time_mmss(self):
        self.assertEqual(SplitManager.converter_time_mmss(100), "1.40")

    def test_create_commands(self):
        offsets_and_names = [{'name': '01 Герой Щита v21 - Пролог 01', 'offset': 0},
                             {'name': '02 Герой Щита v21 - Пролог 02', 'offset': 200}]
        folder_name = "Герой Щита v21"
        number_downloaded_file = 1

        splitter = SplitManager("mp3splt",
                                path_temp=os.path.join(f'{os.path.sep}'.join(__file__.split(os.path.sep)[:-1]), "test_file"),
                                path_save_to=r"D:\\")
        commands = splitter.create_commands(offsets_and_names, folder_name, number_downloaded_file)
        self.assertEqual(commands,
                            [
                                ' mp3splt\\mp3splt  1.mp3  0.0  3.20  -o "01 Герой Щита v21 - Пролог 01"  -g '
                                '[@t="01 Герой Щита v21 - Пролог 01",@N=1,]  -d "D:\\\\Герой Щита v21" ',
                                ' mp3splt\\mp3splt  1.mp3  3.20  8.23  -o "02 Герой Щита v21 - Пролог 02"  -g '
                                '[@t="02 Герой Щита v21 - Пролог 02",@N=2,]  -d "D:\\\\Герой Щита v21" ',
                                'del 1.mp3',
                                'del command.bat'
                            ]
                         )
