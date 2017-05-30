from pathlib import Path
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
        self.test_files_path = Path('test_data/test_files')

    def tearDown(self):
        """
        Tear down after each test case
        """
        path = Path('test_data/test_files/temp.json')
        if path.is_file():
            path.unlink()

    def test_read_json(self):
        """
        Test read_json function
        """
        foo = read_json(self.test_files_path.joinpath('foo.json').open())
        bar = read_json(self.test_files_path.joinpath('bar.json').open())
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
        path = self.test_files_path.joinpath('temp.json')
        write_json(path.open(mode='w+'), temp_dict)
        self.assertDictEqual(temp_dict, read_json(path.open()))

    def test_read_all_files(self):
        """
        Test read_all_files function
        """
        files = ['bar.json', 'foo.json', 'baz.txt', 'qux.png']
        file_paths = [self.test_files_path.joinpath(f) for f in files]
        self.assertEqual(
            set(file_paths),
            set(read_all_files(self.test_files_path))
        )


if __name__ == '__main__':
    main()
