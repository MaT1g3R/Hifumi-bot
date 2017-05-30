import os
from unittest import TestCase, main

from scripts.file_io import read_json, write_json, read_all_files


class TestFileIO(TestCase):
    """
    Unittests for file_io.py
    """

    def setUp(self):
        """
        Setup before each test case
        :return:
        """
        self.foo = {
            "a": "a",
            "b": ["b", "c", "d"],
            "c": {"d": "d", "e": ["e", "f", "g"]}
        }
        self.bar = ["ssss", "ddddd", {"1212": "dsadasdsa"}]
        self.test_files_path = os.path.join('test_data', 'test_files')

    def tearDown(self):
        """
        Tear down after each test case
        """
        path = os.path.join('test_data', 'test_files', 'temp.json')
        if os.path.isfile(path):
            os.remove(path)

    def test_read_json(self):
        """
        Test read_json function
        """
        foo = read_json(open(os.path.join(self.test_files_path, 'foo.json')))
        bar = read_json(open(os.path.join(self.test_files_path, 'bar.json')))
        self.assertDictEqual(foo, self.foo)
        self.assertListEqual(bar, self.bar)

    def test_write_json(self):
        """
        Test write json function
        """
        temp_dict = {
            '111': 'adas',
            'asdsad': ['asd', 3, 'ddd'],
            'asd': {
                'a': '12121',
                '2': ['asdsad', 1111, 30303]
            }
        }
        path = os.path.join(self.test_files_path, 'temp.json')
        write_json(open(path, 'w+'), temp_dict)
        self.assertDictEqual(temp_dict, read_json(open(path)))

    def test_read_all_files(self):
        """
        Test read_all_files function
        """
        files = ['bar.json', 'foo.json', 'baz.txt', 'qux.png']
        file_paths = [os.path.join(self.test_files_path, f) for f in files]
        self.assertEqual(
            set(file_paths), set(read_all_files(self.test_files_path))
        )


if __name__ == '__main__':
    main()
