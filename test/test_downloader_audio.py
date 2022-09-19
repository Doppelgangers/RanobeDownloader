import unittest
import sys

sys.path.insert(1, '..')
from handlers.downloader_audio import DownloaderAudio


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
