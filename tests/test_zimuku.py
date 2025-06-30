import os
import sys
import tempfile
import zipfile
import unittest
# from lib import zimuku_agent as zmkagnt

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
lib_path = os.path.join(project_root, 'resources', 'lib')
sys.path.insert(0, lib_path)

import zimuku_agent

class Logger:
    def log(self, module, msg, level=0):
        lvls = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL')
        print('[%s]%s: %s' % (lvls[level], module, msg))


class Unpacker:
    def __init__(self, folder):
        self.folder = folder

    def unpack(self, path):
        zip_ref = zipfile.ZipFile(path, 'r')
        file_list = zip_ref.namelist()
        parent = ''
        if file_list[0][-1:] == '/':
            parent = file_list.pop(0)
            file_list = [x.replace(parent, '') for x in file_list]

        zip_ref.extractall(self.folder)

        return os.path.join(self.folder, parent), file_list


class TestZimukuAgent(unittest.TestCase):
    def setUp(self):

        self.tmp_dir_obj = tempfile.TemporaryDirectory()
        self.tmp_folder = self.tmp_dir_obj.name

        self.base_url = 'http://srtku.com'

        return super().setUp()

    def get_agent(self, settings):
        return zimuku_agent.Zimuku_Agent(
            self.base_url, self.tmp_folder, Logger(),
            Unpacker(self.tmp_folder),
            settings)

    def test_pass_captcha(self):
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})
        headers, http_body=agent.get_page(self.base_url)
        self.assertGreaterEqual(http_body.decode('utf-8').find('<a href="/newsubs">'), 0)


    def test_search(self):
        # 测试搜索功能
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})

        items = {
            'temp': False, 'rar': False, 'mansearch': False, 'year': '2021', 'season': '4',
            'episode': '17', 'tvshow': '小谢尔顿', 'title': '由一个黑洞引发的联想',
            'file_original_path':
            'Young.Sheldon.S04E17.720p.HEVC.x265-MeGusta.mkv',
            '3let_language': ['eng']}
        result = agent.search(items['tvshow'], items)
        self.assertNotEqual(len(result), 0)

    def test_search2(self):
        # 测试搜索功能
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})

        items = {
            'temp': False, 'rar': False, 'mansearch': False, 'year': '1989', 'season': '1', 'episode': '3', 'tvshow': '孤鸽镇', 'title': '草原',
            'file_original_path': 'F:\\Downton.Abbey.2010.S06E02.1080p.BluRay.DD.2.0.x265.10bit-monster6688.mkv',
            '3let_language': ['', 'eng']}
        result = agent.search(items['tvshow'], items)
        self.assertNotEqual(len(result), 0)

    def test_search3(self):
        # 测试对搜索结果再次进行剧集过滤的功能
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})

        items = {'temp': False, 'rar': False, 'mansearch': False, 'year': '2022', 'season': '1', 'episode': '1', 'tvshow': 'Reborn Rich', 'title': 'Soonyang’s Loyal Servant',
                 'file_original_path': 'C:\\Reborn.Rich.S01E01.Episode.1.1080p.DSNP.WEB-DL.AAC2.0.H.264-MARK.mkv', '3let_language': ['chi', '', 'eng']}
        result = agent.search(items['tvshow'], items)
        self.assertEqual(len(result), 2)

    def test_search4(self):
        # 测试搜索——字幕链接只有类似“第7季第8集”的字样
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})

        items = {
            'temp': False, 'rar': False, 'mansearch': False, 'year': '2021', 'season': '7',
            'episode': '8', 'tvshow': '小谢尔顿', 'title': '电子脚镣和塑料垃圾房',
            'file_original_path':
            'Young.Sheldon.S07E08.720p.HEVC.x265-MeGusta.mkv',
            '3let_language': ['eng']}
        result = agent.search(items['tvshow'], items)
        self.assertNotEqual(len(result), 0)

    def test_deep_search(self):
        # 搜索不在第一页的字幕
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})

        items = {
            'temp': False, 'rar': False, 'mansearch': False, 'year': '2021', 'season': '12',
            'episode': '3', 'tvshow': '生活大爆炸', 'title': '',
            'file_original_path': 'v.mkv',
            '3let_language': ['eng']}
        result = agent.search('生活大爆炸', items)
        self.assertEqual(len(result), 3)

    def test_search_movie(self):
        agent = self.get_agent({'subtype': 'srt', 'sublang': 'dualchs'})

        items = {
            'temp': False, 'rar': False, 'mansearch': False, 'year': '2018', 'season': '',
            'episode': '', 'tvshow': '', 'title': 'Free Solo',
            'file_original_path':
            'Free.Solo.2018.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTG.mkv',
            '3let_language': ['', 'eng']}
        result = agent.search('Free Solo', items)
        self.assertEqual(len(result), 8)

    def test_download(self):
        # 测试下载功能
        agent = self.get_agent({'subtype': 'none', 'sublang': 'none'})

        l1, l2, l3 = agent.download(self.base_url + '/detail/154168.html')
        self.assertIsNotNone(l1)
        self.assertIsNotNone(l3)
        self.assertEqual(len(l1), 9)

    def test_filter_sub(self):
        # 测试基于插件偏好设置的字幕过滤功能
        l1 = ['Mare.of.Easttown.S01E03-TEPES.简体&英文.ass',
              'Mare.of.Easttown.S01E03-TEPES.简体&英文.srt',
              'Mare.of.Easttown.S01E03-TEPES.简体.ass',
              'Mare.of.Easttown.S01E03-TEPES.简体.srt',
              'Mare.of.Easttown.S01E03-TEPES.繁体&英文.ass',
              'Mare.of.Easttown.S01E03-TEPES.繁体&英文.srt',
              'Mare.of.Easttown.S01E03-TEPES.繁体.ass',
              'Mare.of.Easttown.S01E03-TEPES.繁体.srt',
              'Mare.of.Easttown.S01E03-TEPES.英文.srt']
        l2 = l1
        l3 = ['c:\\Mare.of.Easttown.S01E03-TEPES.简体&英文.ass',
              'c:\\Mare.of.Easttown.S01E03-TEPES.简体&英文.srt',
              'c:\\Mare.of.Easttown.S01E03-TEPES.简体.ass',
              'c:\\Mare.of.Easttown.S01E03-TEPES.简体.srt',
              'c:\\Mare.of.Easttown.S01E03-TEPES.繁体&英文.ass',
              'c:\\Mare.of.Easttown.S01E03-TEPES.繁体&英文.srt',
              'c:\\Mare.of.Easttown.S01E03-TEPES.繁体.ass',
              'c:\\Mare.of.Easttown.S01E03-TEPES.繁体.srt',
              'c:\\Mare.of.Easttown.S01E03-TEPES.英文.srt']

        agent = self.get_agent({'subtype': 'srt', 'sublang': 'none'})

        self.assertEqual(len(agent.get_preferred_subs(l1, l2, l3)[0]), 5)

        agent.set_setting({'subtype': 'none', 'sublang': 'cht'})
        self.assertEqual(len(agent.get_preferred_subs(l1, l2, l3)[0]), 2)

        agent.set_setting({'subtype': 'ass', 'sublang': 'dualchs'})
        self.assertEqual(len(agent.get_preferred_subs(l1, l2, l3)[0]), 1)

    def test_garbled_archive(self):
        # 测试文件名乱码的压缩包是否能正确处理
        agent = self.get_agent({'subtype': 'none', 'sublang': 'none'})
        url = self.base_url + '/detail/154168.html'    # 乱码字幕
        l1, _, _ = agent.download(url)
        self.assertIn('young.sheldon.s04e18.720p.hdtv.x264-syncopy.英文.srt', l1)
        url = self.base_url + '/detail/155101.html'    # 正常字幕
        l1, _, _ = agent.download(url)
        self.assertIn('black.monday.s03e01.720p.web.h264-ggez.繁体.srt', l1)

    def test_cut_filename(self):
        # 测试文件名是否能被正确截短
        agent = self.get_agent(
            {'subtype': 'none', 'sublang': 'none'})
        url = self.base_url + '/detail/155101.html'
        l1, l2, _ = agent.download(url)
        for fn in l1:
            self.assertIn('black.monday.s03e01.720p.web.h264-ggez', fn)
        for fn in l2:
            self.assertNotIn('black.monday.s03e01.720p.web.h264-ggez', fn)

    def test_sub_rating(self):
        agent = self.get_agent({'subtype': 'none', 'sublang': 'none'})
        items = {
            'temp': False, 'rar': False, 'mansearch': False, 'year': '', 'season': '2',
            'episode': '4', 'tvshow': '9号秘事', 'title': '',
            'file_original_path':
            'tv.mkv', '3let_language': ['eng']}
        result = agent.search('9号秘事', items)
        self.assertEqual(len(result), 1)
        sub = result[0]
        self.assertEqual(sub['rating'], '4')


if __name__ == '__main__':
    unittest.main()
