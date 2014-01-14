
import mock
import ldapom
import pyramid.testing as testing
import esauth.resources as resources
import tests.unit.base as base
from pyramid.registry import Registry


class GroupListResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.unit = resources.GroupListResource(self.request)

    @mock.patch('esauth.resources.LDAPDataSourceMixin.get_group_entry')
    @mock.patch('esauth.resources.GroupResource')
    def test_getitem(self, GroupResource, get_group_entry):
        get_group_entry.return_value = 'DUMMY_ENTRY'
        ret = self.unit['oneoneone']
        self.assertIsNotNone(ret)
        GroupResource.assert_called_with(self.request, 'DUMMY_ENTRY')

    @mock.patch('esauth.resources.LDAPDataSourceMixin.get_all_groups')
    @mock.patch('esauth.resources.GroupResource')
    def test_iter(self, GroupResource, get_all_groups):
        get_all_groups.return_value = ['DUMMY_ENTRY_1', 'DUMMY_ENTRY_2']
        rets = []
        for x in self.unit:
            rets.append(x)
        self.assertEqual(len(rets), 2)
        GroupResource.assert_called_with(self.request, 'DUMMY_ENTRY_2')


class GroupResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.entry = mock.Mock(spec=ldapom.LDAPEntry)
        self.unit = resources.GroupResource(self.request, self.entry)

    def test_as_dict(self):
        self.entry.cn = ['CN']
        ret = self.unit.as_dict()
        self.assertIsInstance(ret, dict)
        self.assertEqual(ret['cn'], 'CN')

    @mock.patch('esauth.resources.LDAPDataSourceMixin.lc')
    def test_get_members(self, lc):
        lc.get_entry.side_effect = [1, 2]
        self.entry.member = ['memberOne', 'memberTwo']
        ret = self.unit.get_members()
        self.assertEqual(len(ret), 2)
        self.assertListEqual(ret, [1, 2])


class UserListResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.unit = resources.UserListResource(self.request)

    @mock.patch('esauth.resources.UserResource')
    @mock.patch('esauth.resources.LDAPDataSourceMixin.get_user_entry')
    def test_getitem(self, get_user_entry, UserResource):
        get_user_entry.return_value = 'DUMMY_ENTRY'
        ret = self.unit['oneoneone']
        self.assertIsNotNone(ret)
        UserResource.assert_called_with(self.request, 'DUMMY_ENTRY')

    @mock.patch('esauth.resources.UserResource')
    @mock.patch('esauth.resources.LDAPDataSourceMixin.get_all_users')
    def test_iter(self, get_all_users, UserResource):
        get_all_users.return_value = ['DUMMY_ENTRY_1', 'DUMMY_ENTRY_2']
        rets = []
        for x in self.unit:
            rets.append(x)
        self.assertEqual(len(rets), 2)
        UserResource.assert_called_with(self.request, 'DUMMY_ENTRY_2')


class UserResourceTestCase(base.UnitTestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.entry = mock.Mock(spec=ldapom.LDAPEntry)
        self.entry.uid = ['testuser']
        self.entry.uidNumber = 10000
        self.entry.gidNumber = 10000
        self.unit = resources.UserResource(self.request, self.entry)

    def test_as_dict(self):
        ret = self.unit.as_dict()
        self.assertIsInstance(ret, dict)
        self.assertEqual(ret['uid'], 'testuser')
        self.assertEqual(ret['uidNumber'], 10000)
        self.assertEqual(ret['gidNumber'], 10000)


class LDAPDataSourceMixinTestCase(base.UnitTestCase):
    def setUp(self):
        self.unit = resources.LDAPDataSourceMixin()

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_all_users(self, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        registry['lc'].search.return_value = "TWOTWO"

        ret = self.unit.get_all_users()
        self.assertEqual(ret, "TWOTWO")
        registry['lc'].search.assert_called_with(search_filter='objectClass=account', base='dc=oneone')

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_all_groups(self, registry):
        registry.settings = {'ldap.groups_base': 'dc=oneone'}
        registry['lc'].search.return_value = "TWOTWO"

        ret = self.unit.get_all_groups()
        self.assertEqual(ret, "TWOTWO")
        registry['lc'].search.assert_called_with(search_filter='objectClass=groupOfNames', base='dc=oneone')

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_user_entry(self, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock(spec=ldapom.LDAPEntry)
        entry.exists.return_value = True
        registry['lc'].get_entry.return_value = entry

        ret = self.unit.get_user_entry("luser")
        registry['lc'].get_entry.assert_called_with("uid=luser,dc=oneone")
        self.assertEqual(ret, entry)

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_user_entry_failure(self, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock(spec=ldapom.LDAPEntry)
        entry.exists.return_value = False
        registry['lc'].get_entry.return_value = entry

        with self.assertRaises(KeyError):
            self.unit.get_user_entry("luser")

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_group_entry(self, registry):
        registry.settings = {'ldap.groups_base': 'dc=oneone'}
        entry = mock.Mock(spec=ldapom.LDAPEntry)
        entry.exists.return_value = True
        registry['lc'].get_entry.return_value = entry

        ret = self.unit.get_group_entry('lgroup')
        registry['lc'].get_entry.assert_called_with("cn=lgroup,dc=oneone")
        self.assertEqual(ret, entry)

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_group_entry_failure(self, registry):
        registry.settings = {'ldap.groups_base': 'dc=oneone'}
        entry = mock.Mock(spec=ldapom.LDAPEntry)
        entry.exists.return_value = False
        registry['lc'].get_entry.return_value = entry

        with self.assertRaises(KeyError):
            self.unit.get_group_entry('lgroup')


class RootFactoryTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.unit = resources.Root(self.request)

    def test_users_in(self):
        self.assertIn('users', self.unit)
        self.assertIsInstance(self.unit['users'], resources.UserListResource)

    def test_groups_in(self):
        self.assertIn('groups', self.unit)
        self.assertIsInstance(self.unit['groups'], resources.GroupListResource)
