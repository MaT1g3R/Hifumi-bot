from os.path import join
from unittest import TestCase, main

from core.data_controller import DataController


class TestDataController(TestCase):
    """
    Unittests for the DataController class
    """

    def setUp(self):
        """
        Setup before each test case
        """
        self.db = DataController(join('test_data', 'mock_db'))

    def tearDown(self):
        """
        Delete all data in mock_db after each test case
        :return:
        """
        conn = self.db.connection
        cur = self.db.cursor
        tables_sql = '''
        SELECT name FROM sqlite_master WHERE type=?
        '''
        cur.execute(tables_sql, ['table'])
        all_tables = [t[0] for t in cur.fetchall()]

        for name in all_tables:
            delete_sql = """
            DELETE FROM '{}'
            """.format(name)
            cur.execute(delete_sql)
        conn.commit()
        conn.close()

    def test_write_tag(self):
        """
        Test case for write_tag
        """
        site = 'foo'
        tag = 'bar'
        self.db.write_tag(site, tag)
        sql = '''
        SELECT tag FROM main.nsfw_tags WHERE site='{}'
        '''.format(site)
        self.db.cursor.execute(sql)
        res = self.db.cursor.fetchone()[0]
        self.assertEqual(tag, res)

    def test_write_tag_list(self):
        """
        Test case for write_tag_list
        """
        site = 'foo'
        lst = ['bar', 'baz']
        self.db.write_tag_list(site, lst)
        sql = '''
        SELECT tag FROM main.nsfw_tags WHERE site='{}'
        '''.format(site)
        self.db.cursor.execute(sql)
        res = [t[0] for t in self.db.cursor.fetchall()]
        self.assertListEqual(lst, res)

    def test_tag_in_db_true(self):
        """
        Test for tag_in_db when it returns true
        """
        tag = 'foo'
        site = 'bar'
        self.db.write_tag(site, tag)
        self.assertTrue(self.db.tag_in_db(site, tag))

    def test_tag_in_db_no_site(self):
        """
        Test for tag_in_db when it returns False because site is not found
        """
        tag = 'foo'
        site = 'bar'
        wrong_site = 'baz'
        self.db.write_tag(site, tag)
        self.assertFalse(self.db.tag_in_db(wrong_site, tag))

    def test_tag_in_db_no_tag(self):
        """
        Test for tag_in_db when it returns False because tag is not found
        """
        tag = 'foo'
        site = 'bar'
        wrong_tag = 'baz'
        self.db.write_tag(site, tag)
        self.assertFalse(self.db.tag_in_db(site, wrong_tag))

    def test_fuzzy_match_tag_fail_site(self):
        """
        Test for fuzzy_match_tag when site is not found
        """
        site = 'foo'
        wrong_site = 'bar'
        tag = 'baz'
        self.db.write_tag(site, tag)
        self.assertIsNone(self.db.fuzzy_match_tag(wrong_site, tag))

    def test_fuzzy_match_tag_fail_tag(self):
        """
        Test for fuzzy_match_tag when tag is not found
        """
        site = 'foo'
        tag = 'bar'
        wrong_tag = 'baz'
        self.db.write_tag(site, tag)
        self.assertIsNone(self.db.fuzzy_match_tag(site, wrong_tag))

    def test_fuzzy_match_tag_front(self):
        """
        Test for fuzzy match tag when the front of the tag in db matched the
        search query
        """
        tag = 'foo'
        tag_to_match = 'f'
        site = 'bar'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_fuzzy_match_tag_middle(self):
        """
        Test for fuzzy match tag when the middle of the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'a'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_fuzzy_match_tag_end(self):
        """
        Test for fuzzy match tag when the back of the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'ar'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_fuzzy_match_tag_full(self):
        """
        Test for fuzzy match tag when the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'bar'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_get_set(self):
        """
        Test for get/set an entry, for cases where the server is a unique key
        """
        self.__get_set(self.db.set_prefix, self.db.get_prefix)
        self.__get_set(self.db.set_language, self.db.get_language)

    def test_get_fail(self):
        """
        Test case for failed to get an entry from the db
        """
        self.__get_fail(self.db.set_language, self.db.get_language)
        self.__get_fail(self.db.set_prefix, self.db.get_prefix)

    def test_add_entry(self):
        """
        Test for adding an entry
        """
        self.__add_with_list(self.db.add_role, self.db.get_role_list)
        self.__add_with_list(self.db.set_mod_log, self.db.get_mod_log)

    def test_add_entry_overwrite(self):
        """
        Test for adding an entry when it overrides the value
        """
        self.__add_overwrite_with_list(self.db.add_role, self.db.get_role_list)
        self.__add_overwrite_with_list(self.db.set_mod_log, self.db.get_mod_log)
        self.__set_overwrite(self.db.set_language, self.db.get_language)
        self.__set_overwrite(self.db.set_prefix, self.db.get_prefix)

    def test_remove_entry(self):
        """
        Test for remove entry
        """
        self.__remove_with_list(
            self.db.add_role, self.db.remove_role, self.db.get_role_list
        )

        self.__remove_with_list(
            self.db.set_mod_log, self.db.remove_mod_log, self.db.get_mod_log
        )

    def test_remove_entry_no_server(self):
        """
        Test for remove entry for a non-existing server
        """
        self.__remove_no_server_with_list(
            self.db.add_role, self.db.remove_role, self.db.get_role_list
        )

        self.__remove_no_server_with_list(
            self.db.set_mod_log, self.db.remove_mod_log, self.db.get_mod_log)

    def test_remove_entry_no_entry(self):
        """
        Test for removeentry for a non-existing entry
        """
        self.__remove_no_entry_with_list(
            self.db.add_role, self.db.remove_role, self.db.get_role_list
        )

        self.__remove_no_entry_with_list(
            self.db.set_mod_log, self.db.remove_mod_log, self.db.get_mod_log)

    def test_get_entry_list(self):
        """
        Test for get a list of entry
        """
        self.__get_list(self.db.add_role, self.db.get_role_list)
        self.__get_list(self.db.set_mod_log, self.db.get_mod_log)

    def test_get_entry_list_empty(self):
        """
        Test for get a list of entry when it is empty
        """
        self.__get_list_empty(self.db.add_role, self.db.get_role_list)
        self.__get_list_empty(self.db.set_mod_log, self.db.get_mod_log)

    def test_warning(self):
        """
        Test adding and getting warning count
        """
        server = 'foo'
        user = 'bar'
        other_server = 'baz'
        other_user = 'qux'
        self.assertEqual(0, self.db.get_warn(server, user))
        self.db.add_warn(server, user)
        self.assertEqual(1, self.db.get_warn(server, user))
        self.db.add_warn(server, user)
        self.assertEqual(2, self.db.get_warn(server, user))
        self.assertTrue(
            0 == self.db.get_warn(other_server, user) ==
            self.db.get_warn(server, other_user)
        )

    def test_remove_warning(self):
        """
        Test remove 1 from a user's warning count
        """
        server = 'foo'
        user = 'bar'
        other_server = 'baz'
        other_user = 'qux'
        self.db.add_warn(server, other_user)
        self.db.add_warn(other_server, user)
        self.db.remove_warn(server, user)
        self.db.add_warn(server, user)
        self.db.add_warn(server, user)
        self.db.remove_warn(server, user)
        self.assertEqual(1, self.db.get_warn(server, user))
        self.assertTrue(
            1 == self.db.get_warn(other_server, user) ==
            self.db.get_warn(server, other_user)
        )

    def __get_set(self, func_add, func_get):
        """
        Helper method to test get/set an entry from the db
        """
        server = 'foo'
        entry = 'bar'
        func_add(server, entry)
        self.assertEqual(entry, func_get(server))

    def __get_fail(self, func_add, func_get):
        """
        Helper method to test get entry from the db when the entry doesn't
        exist
        """
        server = 'foo'
        self.assertIsNone(func_get(server))
        entry = 'bar'
        wrong_server = 'baz'
        func_add(server, entry)
        self.assertIsNone(func_get(wrong_server))

    def __set_overwrite(self, func_add, func_get):
        """
        Helper method to test overwriting a value in the db
        """
        server = 'foo'
        old_entry = 'bar'
        new_entry = 'baz'
        func_add(server, old_entry)
        func_add(server, new_entry)
        self.assertEqual(new_entry, func_get(server))

    def __add_with_list(self, func_add, func_get_lst):
        """
        Helper method for testing adding an entry, when the server is not
        a unique key in the db
        """
        server = 'foo'
        entry = 'bar'
        func_add(server, entry)
        self.assertTrue(entry in func_get_lst(server))

    def __add_overwrite_with_list(self, func_add, func_get_lst):
        """
        Helper method for testing adding an entry when it overrides the value,
        when the server is not a unique key in the db
        """
        server = 'foo'
        entry = 'bar'
        func_add(server, entry)
        self.assertTrue(entry in func_get_lst(server))
        func_add(server, entry)
        self.assertEqual(1, len(func_get_lst(server)))

    def __remove_with_list(self, func_add, func_rm, func_lst):
        """
        Helper method for testing remove entry,
        when the server is not a unique key in the db
        """
        server = 'foo'
        entry = 'bar'
        other_roles = ['baz', 'qux']
        for r in [entry] + other_roles:
            func_add(server, r)
        func_rm(server, entry)
        self.assertListEqual(other_roles, func_lst(server))

    def __remove_no_server_with_list(self, func_add, func_rm, func_lst):
        """
        Helper method for testing remove entry from a non-existing server,
        when the server is not a unique key in the db
        """
        server = 'foo'
        wrong_server = 'bar'
        entry_lst = ['baz', 'qux']
        for r in entry_lst:
            func_add(server, r)
        func_rm(wrong_server, entry_lst[0])
        self.assertListEqual(entry_lst, func_lst(server))

    def __remove_no_entry_with_list(self, func_add, func_rm, func_lst):
        """
        Helper method for testing remove entry for a non-existing entry,
        when the server is not a unique key in the db
        """
        server = 'foo'
        wrong_role = 'bar'
        entry_lst = ['baz', 'qux']
        for r in entry_lst:
            func_add(server, r)
        func_rm(server, wrong_role)
        self.assertListEqual(entry_lst, func_lst(server))

    def __get_list(self, func_add, func_lst):
        """
        Helper method for testing get a list of entry
        """
        entry_lst = ['foo', 'bar']
        server = 'baz'
        for r in entry_lst:
            func_add(server, r)
        self.assertEqual(set(entry_lst), set(func_lst(server)))

    def __get_list_empty(self, func_add, func_lst):
        """
        Helper method for testing getting a list of entry when it is empty
        """
        entry_lst = ['foo', 'bar']
        server = 'baz'
        wrong_server = 'qux'
        for r in entry_lst:
            func_add(server, r)
        self.assertListEqual([], func_lst(wrong_server))


if __name__ == '__main__':
    main()
