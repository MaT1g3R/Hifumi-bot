from unittest import TestCase, main

from scripts.helpers import combine_dicts, strip_letters, suplement_dict, \
    dict_has_empty, get_system_name


class TestHelpers(TestCase):
    """
    Unittest for helpers.py
    """

    def test_combine_dicts(self):
        """
        General test case for combine_dicts
        """
        d1 = {'a': 1, 'b': 2}
        d2 = {'a': 2, 'c': 10}
        combined = {'a': 3, 'b': 2, 'c': 10}
        self.assertDictEqual(combine_dicts([d1, d2]), combined)

    def test_combine_dicts_none(self):
        """
        Test case for combine_dicts when there're None values in one of the
        dicts
        """
        d1 = {'a': None, 'b': 3, 'c': 22}
        d2 = {'a': 1, 'b': 1, 'c': None}
        combined = {'a': 1, 'b': 4, 'c': 22}
        self.assertDictEqual(combined, combine_dicts([d1, d2]))

    def test_combine_dicts_multiple(self):
        """
        Test case for combine_dicts on 3 or more dicts
        """
        d1 = {'a': 1}
        d2 = {'a': 2, 'b': 21}
        d3 = {'a': 12, 'c': 11, 'b': 10}
        combined = {'a': 12 + 2 + 1, 'b': 10 + 21, 'c': 11}
        self.assertDictEqual(combined, combine_dicts([d1, d2, d3]))

    def test_combine_dicts_nested(self):
        """
        Test case for combine_dicts with nested dicts
        """
        d1 = {'a': {'b': 1, 'c': 2}, 'b': 3}
        d2 = {'a': {'b': 2, 'd': 12}, 'd': 4}
        combined = {'a': {'b': 3, 'c': 2, 'd': 12}, 'b': 3, 'd': 4}
        self.assertDictEqual(combined, combine_dicts([d1, d2]))

    def test_suplement_dict(self):
        """
        Test case for suplement_dict
        """
        d1 = {'a': 'foo', 'b': 'bar'}
        d2 = {'a': 'baz'}
        expected = {'a': 'baz', 'b': 'bar'}
        self.assertDictEqual(expected, suplement_dict(d1, d2))

    def test_get_system_name(self):
        """
        Test case for get_system_name
        """
        res = get_system_name()
        self.assertFalse('-' in res)
        self.assertTrue(res)

    def test_strip_letters(self):
        """
        Test case for strip_letters
        """
        msg = 'AAA12.32BBB33.11CCC100'
        expected = ['12.32', '33.11', '100']
        self.assertListEqual(expected, strip_letters(msg))

    def test_strip_letters_none(self):
        """
        Test case for strip_letters when there're no numbers in the string
        """
        msg = 'foo.asdsa.weqe.asd'
        self.assertFalse(strip_letters(msg))

    def test_dict_has_empty_none(self):
        """
        Test case for dict_has_empty when there's a None value in the dict
        """
        d = {'a': 'foo', 'b': {'c': None, 'd': 12}}
        self.assertTrue(dict_has_empty(d))

    def test_dict_has_empty_str(self):
        """
        Test case for dict_has_empty when there's a empty string in the dict
        """
        d = {'a': 'foo', 'b': {'c': '', 'd': 12}}
        self.assertTrue(dict_has_empty(d))

    def test_dict_has_empty_lst(self):
        """
        Test case for dict_has_empty when there's a empty list in the dict
        """
        d = {'a': 'foo', 'b': {'c': [], 'd': 12}}
        self.assertTrue(dict_has_empty(d))

    def test_dict_has_empty_not_empty(self):
        """
        Test case for dict_has_empty when there's no empty values
        """
        d = {'a': 'foo', 'b': {'c': 0, 'd': 12}}
        self.assertFalse(dict_has_empty(d))


if __name__ == '__main__':
    main()
