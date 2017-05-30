import sqlite3
from pathlib import Path
from random import choice
from unittest import TestCase, main

from scripts.data_controller import *


def clear_db(conn, cur):
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


class TestDataController(TestCase):
    """
    Unittests for the DataController class
    """

    def setUp(self):
        self.conn = sqlite3.connect(str(Path('test_data/mock_db')))
        self.cur = self.conn.cursor()

    def tearDown(self):
        clear_db(self.conn, self.cur)

    def test_write_tag(self):
        """
        Test case for write_tag_
        """
        site = 'foo'
        tag = 'bar'
        write_tag_(self.conn, self.cur, site, tag)
        sql = '''
        SELECT tag FROM main.nsfw_tags WHERE site='{}'
        '''.format(site)
        self.cur.execute(sql)
        res = self.cur.fetchone()[0]
        self.assertEqual(tag, res)

    def test_write_tag_list(self):
        """
        Test case for write_tag_list_
        """
        site = 'foo'
        lst = ['bar', 'baz']
        write_tag_list_(self.conn, self.cur, site, lst)
        sql = '''
        SELECT tag FROM main.nsfw_tags WHERE site='{}'
        '''.format(site)
        self.cur.execute(sql)
        res = [t[0] for t in self.cur.fetchall()]
        self.assertListEqual(lst, res)

    def test_tag_in_db_true(self):
        """
        Test for tag_in_db_ when it returns true
        """
        tag = 'foo'
        site = 'bar'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertTrue(tag_in_db_(self.cur, site, tag))

    def test_tag_in_db_no_site(self):
        """
        Test for tag_in_db_ when it returns False because site is not found
        """
        tag = 'foo'
        site = 'bar'
        wrong_site = 'baz'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertFalse(tag_in_db_(self.cur, wrong_site, tag))

    def test_tag_in_db_no_tag(self):
        """
        Test for tag_in_db_ when it returns False because tag is not found
        """
        tag = 'foo'
        site = 'bar'
        wrong_tag = 'baz'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertFalse(tag_in_db_(self.cur, site, wrong_tag))

    def test_fuzzy_match_tag_fail_site(self):
        """
        Test for fuzzy_match_tag_ when site is not found
        """
        site = 'foo'
        wrong_site = 'bar'
        tag = 'baz'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertIsNone(fuzzy_match_tag_(self.cur, wrong_site, tag))

    def test_fuzzy_match_tag_fail_tag(self):
        """
        Test for fuzzy_match_tag_ when tag is not found
        """
        site = 'foo'
        tag = 'bar'
        wrong_tag = 'baz'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertIsNone(fuzzy_match_tag_(self.cur, site, wrong_tag))

    def test_fuzzy_match_tag_front(self):
        """
        Test for fuzzy match tag when the front of the tag in db matched the
        search query
        """
        tag = 'foo'
        tag_to_match = 'f'
        site = 'bar'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertEqual(tag, fuzzy_match_tag_(self.cur, site, tag_to_match))

    def test_fuzzy_match_tag_middle(self):
        """
        Test for fuzzy match tag when the middle of the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'a'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertEqual(tag, fuzzy_match_tag_(self.cur, site, tag_to_match))

    def test_fuzzy_match_tag_end(self):
        """
        Test for fuzzy match tag when the back of the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'ar'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertEqual(tag, fuzzy_match_tag_(self.cur, site, tag_to_match))

    def test_fuzzy_match_tag_full(self):
        """
        Test for fuzzy match tag when the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'bar'
        write_tag_(self.conn, self.cur, site, tag)
        self.assertEqual(tag, fuzzy_match_tag_(self.cur, site, tag_to_match))

    def test_get_set(self):
        """
        Test for get/set an entry, for cases where the server is a unique key
        """
        self.__get_set(set_prefix_, get_prefix_)
        self.__get_set(set_language_, get_language_)

    def test_get_fail(self):
        """
        Test case for failed to get an entry from the db
        """
        self.__get_fail(set_language_, get_language_)
        self.__get_fail(set_prefix_, get_prefix_)

    def test_add_entry(self):
        """
        Test for adding an entry
        """
        self.__add_with_list(add_role_, get_role_list_)
        self.__add_with_list(set_mod_log_, get_mod_log_)

    def test_add_entry_overwrite(self):
        """
        Test for adding an entry when it overrides the value
        """
        self.__add_overwrite_with_list(add_role_, get_role_list_)
        self.__add_overwrite_with_list(set_mod_log_, get_mod_log_)
        self.__set_overwrite(set_language_, get_language_)
        self.__set_overwrite(set_prefix_, get_prefix_)

    def test_remove_entry(self):
        """
        Test for remove entry
        """
        self.__remove_with_list(add_role_, remove_role_, get_role_list_)
        self.__remove_with_list(set_mod_log_, remove_mod_log_, get_mod_log_)
        self.__delete(set_language_, delete_language_, get_language_)
        self.__delete(set_prefix_, delete_prefix_, get_prefix_)

    def test_remove_entry_no_server(self):
        """
        Test for remove entry for a non-existing server
        """
        self.__remove_no_server_with_list(add_role_, remove_role_,
                                          get_role_list_)
        self.__remove_no_server_with_list(
            set_mod_log_, remove_mod_log_, get_mod_log_
        )
        self.__delete(set_language_, delete_language_, get_language_)
        self.__delete(set_prefix_, delete_prefix_, get_prefix_)

    def test_remove_entry_no_entry(self):
        """
        Test for removeentry for a non-existing entry
        """
        self.__remove_no_entry_with_list(add_role_, remove_role_,
                                         get_role_list_)
        self.__remove_no_entry_with_list(
            set_mod_log_, remove_mod_log_, get_mod_log_
        )

    def test_get_entry_list(self):
        """
        Test for get a list of entry
        """
        self.__get_list(add_role_, get_role_list_)
        self.__get_list(set_mod_log_, get_mod_log_)

    def test_get_entry_list_empty(self):
        """
        Test for get a list of entry when it is empty
        """
        self.__get_list_empty(add_role_, get_role_list_)
        self.__get_list_empty(set_mod_log_, get_mod_log_)

    def test_warning(self):
        """
        Test adding and getting warning count
        """
        server = 'foo'
        user = 'bar'
        other_server = 'baz'
        other_user = 'qux'
        self.assertEqual(0, get_warn_(self.cur, server, user))
        add_warn_(self.conn, self.cur, server, user)
        self.assertEqual(1, get_warn_(self.cur, server, user))
        add_warn_(self.conn, self.cur, server, user)
        self.assertEqual(2, get_warn_(self.cur, server, user))
        self.assertTrue(
            0 == get_warn_(self.cur, other_server, user) ==
            get_warn_(self.cur, server, other_user)
        )

    def test_remove_warning(self):
        """
        Test remove 1 from a user's warning count
        """
        server = 'foo'
        user = 'bar'
        other_server = 'baz'
        other_user = 'qux'
        add_warn_(self.conn, self.cur, server, other_user)
        add_warn_(self.conn, self.cur, other_server, user)
        remove_warn_(self.conn, self.cur, server, user)
        add_warn_(self.conn, self.cur, server, user)
        add_warn_(self.conn, self.cur, server, user)
        remove_warn_(self.conn, self.cur, server, user)
        self.assertEqual(1, get_warn_(self.cur, server, user))
        self.assertTrue(
            1 == get_warn_(self.cur, other_server, user) ==
            get_warn_(self.cur, server, other_user)
        )

    def test_get_balance(self):
        """
        Test get_balance_
        """
        user, balance = self.__insert_balance()
        self.assertEqual(balance, get_balance_(self.cur, user))
        self.assertEqual(0, get_balance_(self.cur, 'bar'))

    def test_change_balance(self):
        """
        Test change balance
        """
        user, balance = self.__insert_balance()
        other_user = 'bar'
        delta_positive = choice(range(1, 50))
        delta_negative = choice(range(-50, -1))
        change_balance_(self.conn, self.cur, user, delta_negative)
        change_balance_(self.conn, self.cur, other_user, delta_positive)
        self.assertEqual(balance + delta_negative, get_balance_(self.cur, user))
        self.assertEqual(delta_positive, get_balance_(self.cur, other_user))

    def test_get_set_daily(self):
        """
        Test get_daily_ and set_daily_
        """
        user = 'foo'
        self.assertIsNone(get_daily_(self.cur, user))
        set_daily_(self.conn, self.cur, user)
        self.assertAlmostEqual(time(), get_daily_(self.cur, user), delta=10)

    def test_transfer(self):
        """
        Test transfer_balance_
        """
        root = 'foo'
        target = 'bar'
        amout = choice(range(500, 1000))
        transfer_amount = choice(range(100, 300))
        change_balance_(self.conn, self.cur, root, amout)
        change_balance_(self.conn, self.cur, target, amout)
        transfer_balance_(self.conn, self.cur, root, target, transfer_amount)
        self.assertEqual(amout - transfer_amount, get_balance_(self.cur, root))
        self.assertEqual(amout + transfer_amount,
                         get_balance_(self.cur, target))

    def test_transfer_new(self):
        """
        Test transfer_balance_ to a new user
        """
        root = 'foo'
        target = 'bar'
        amount = choice(range(500, 1000))
        transfer_amount = choice(range(100, 300))
        change_balance_(self.conn, self.cur, root, amount)
        transfer_balance_(self.conn, self.cur, root, target, transfer_amount)
        self.assertEqual(amount - transfer_amount, get_balance_(self.cur, root))
        self.assertEqual(transfer_amount, get_balance_(self.cur, target))

    def test_transfer_fail(self):
        """
        Test transfer_balance_ fail
        """
        root = 'foo'
        target = 'bar'
        amount = choice(range(100, 300))
        transfer_amonut = choice(range(500, 1000))
        change_balance_(self.conn, self.cur, root, amount)
        try:
            transfer_balance_(self.conn, self.cur, root, target,
                              transfer_amonut)
            self.fail()
        except TransferError:
            self.assertEqual(amount, get_balance_(self.cur, root))
            self.assertEqual(0, get_balance_(self.cur, target))

    def test_transfer_negative(self):
        """
        Test transfer_balance_ when the root goes in to debt(lol)
        """
        root = 'foo'
        target = 'bar'
        amount = choice(range(100, 300))
        transfer_amonut = choice(range(500, 1000))
        change_balance_(self.conn, self.cur, root, amount)
        transfer_balance_(
            self.conn, self.cur, root, target, transfer_amonut, False
        )
        self.assertEqual(amount - transfer_amonut, get_balance_(self.cur, root))
        self.assertEqual(transfer_amonut, get_balance_(self.cur, target))

    def __insert_balance(self):
        """
        Insert a random balance into the db
        :return: (user, balance)
        """
        user = 'foo'
        balance = choice(range(1, 100))
        sql = '''
                INSERT INTO currency VALUES (?, ?, NULL)
                '''
        self.cur.execute(sql, (user, balance))
        self.conn.commit()
        return user, balance

    def __get_set(self, func_add, func_get):
        """
        Helper method to test get/set an entry from the db
        """
        server = 'foo'
        entry = 'bar'
        func_add(self.conn, self.cur, server, entry)
        self.assertEqual(entry, func_get(self.cur, server))

    def __get_fail(self, func_add, func_get):
        """
        Helper method to test get entry from the db when the entry doesn't
        exist
        """
        server = 'foo'
        self.assertIsNone(func_get(self.cur, server))
        entry = 'bar'
        wrong_server = 'baz'
        func_add(self.conn, self.cur, server, entry)
        self.assertIsNone(func_get(self.cur, wrong_server))

    def __set_overwrite(self, func_add, func_get):
        """
        Helper method to test overwriting a value in the db
        """
        server = 'foo'
        old_entry = 'bar'
        new_entry = 'baz'
        func_add(self.conn, self.cur, server, old_entry)
        func_add(self.conn, self.cur, server, new_entry)
        self.assertEqual(new_entry, func_get(self.cur, server))

    def __add_with_list(self, func_add, func_lst):
        """
        Helper method for testing adding an entry, when the server is not
        a unique key in the db
        """
        server = 'foo'
        entry = 'bar'
        func_add(self.conn, self.cur, server, entry)
        self.assertTrue(entry in func_lst(self.cur, server))

    def __add_overwrite_with_list(self, func_add, func_lst):
        """
        Helper method for testing adding an entry when it overrides the value,
        when the server is not a unique key in the db
        """
        server = 'foo'
        entry = 'bar'
        func_add(self.conn, self.cur, server, entry)
        self.assertTrue(entry in func_lst(self.cur, server))
        func_add(self.conn, self.cur, server, entry)
        self.assertEqual(1, len(func_lst(self.cur, server)))

    def __delete(self, func_add, func_rm, func_get):
        """
        Helper method to testing deleting entries from the db
        """
        server = 'foo'
        other_server = 'bar'
        entry = 'baz'
        func_add(self.conn, self.cur, server, entry)
        func_add(self.conn, self.cur, other_server, entry)
        func_rm(self.conn, self.cur, server)
        self.assertIsNone(func_get(self.cur, server))
        self.assertEqual(func_get(self.cur, other_server), entry)

    def __delete_no_server(self, func_add, func_rm, func_get):
        """
        Helper method for testing deleting entries from a non-existing server
        """
        server = 'foo'
        other_server = 'bar'
        entry = 'baz'
        func_add(self.conn, self.cur, other_server, entry)
        func_rm(self.conn, self.cur, server)
        self.assertIsNone(func_get(self.cur, server))
        self.assertEqual(func_get(self.cur, other_server), entry)

    def __remove_with_list(self, func_add, func_rm, func_lst):
        """
        Helper method for testing remove entry,
        when the server is not a unique key in the db
        """
        server = 'foo'
        entry = 'bar'
        other_roles = ['baz', 'qux']
        for r in [entry] + other_roles:
            func_add(self.conn, self.cur, server, r)
        func_rm(self.conn, self.cur, server, entry)
        self.assertListEqual(other_roles, func_lst(self.cur, server))

    def __remove_no_server_with_list(self, func_add, func_rm, func_lst):
        """
        Helper method for testing remove entry from a non-existing server,
        when the server is not a unique key in the db
        """
        server = 'foo'
        wrong_server = 'bar'
        entry_lst = ['baz', 'qux']
        for r in entry_lst:
            func_add(self.conn, self.cur, server, r)
        func_rm(self.conn, self.cur, wrong_server, entry_lst[0])
        self.assertListEqual(entry_lst, func_lst(self.cur, server))

    def __remove_no_entry_with_list(self, func_add, func_rm, func_lst):
        """
        Helper method for testing remove entry for a non-existing entry,
        when the server is not a unique key in the db
        """
        server = 'foo'
        wrong_role = 'bar'
        entry_lst = ['baz', 'qux']
        for r in entry_lst:
            func_add(self.conn, self.cur, server, r)
        func_rm(self.conn, self.cur, server, wrong_role)
        self.assertListEqual(entry_lst, func_lst(self.cur, server))

    def __get_list(self, func_add, func_lst):
        """
        Helper method for testing get a list of entry
        """
        entry_lst = ['foo', 'bar']
        server = 'baz'
        for r in entry_lst:
            func_add(self.conn, self.cur, server, r)
        self.assertEqual(set(entry_lst),
                         set(func_lst(self.cur, server)))

    def __get_list_empty(self, func_add, func_lst):
        """
        Helper method for testing getting a list of entry when it is empty
        """
        entry_lst = ['foo', 'bar']
        server = 'baz'
        wrong_server = 'qux'
        for r in entry_lst:
            func_add(self.conn, self.cur, server, r)
        self.assertListEqual([], func_lst(self.cur, wrong_server))


if __name__ == '__main__':
    main()
