from unittest import TestCase, main

from core.checks import *
from tests.mock_objects import *


class TestChecks(TestCase):
    """
    Unittests for checks.py
    """

    def setUp(self):
        """
        Setup before each test case
        """
        self.ctx_admin = MockContext(
            MockMessage(
                author=MockMemberAllRoles(),
                channel=MockTextChannel()
            )
        )
        self.ctx_no = MockContext(
            MockMessage(
                author=MockMemberNoRoles(),
                channel=MockTextChannel()
            )
        )
        self.ctx_bad_word = MockContext(
            MockMessage(
                content='asdasLoLiasdasd',
                channel=MockNsfwChannel()
            )
        )
        self.ctx_nsfw = MockContext(
            MockMessage(
                channel=MockNsfwChannel()
            )
        )
        self.ctx_private = MockContext(
            MockMessage(
                channel=MockPrivateChannel()
            )
        )
        self.ctx_owner = MockContext(
            MockMessage(
                author=MockMemberOwner(),
                channel=MockTextChannel()
            )
        )

    def test_is_nsfw_true(self):
        self.assertTrue(is_nsfw(self.ctx_nsfw))

    def test_is_nsfw_false(self):
        self.assertRaises(NsfwError, is_nsfw, self.ctx_admin)

    def test_is_nsfw_private(self):
        self.assertTrue(is_nsfw(self.ctx_private))

    def test_no_badword_true(self):
        self.assertTrue(no_badword(self.ctx_no))

    def test_no_badword_false(self):
        try:
            no_badword(self.ctx_bad_word)
            self.fail()
        except BadWordError as e:
            self.assertEqual('asdasLoLiasdasd', str(e))

    def test_has_manage_role(self):
        self.assertTrue(has_manage_role(self.ctx_admin))

    def test_has_manage_role_false(self):
        self.assertRaises(ManageRoleError, has_manage_role, self.ctx_no)

    def test_is_admin(self):
        self.assertTrue(is_admin(self.ctx_admin))

    def test_is_admin_false(self):
        self.assertRaises(AdminError, is_admin, self.ctx_no)

    def test_has_manage_message(self):
        self.assertTrue(has_manage_message(self.ctx_admin))

    def test_has_manage_message_false(self):
        self.assertRaises(ManageMessageError, has_manage_message, self.ctx_no)

    def test_is_owner(self):
        self.assertTrue(is_owner(self.ctx_owner))

    def test_is_owner_false(self):
        self.assertRaises(OwnerError, is_owner, self.ctx_admin)


if __name__ == '__main__':
    main()
