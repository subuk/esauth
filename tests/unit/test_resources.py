
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

    @mock.patch('esauth.resources.LDAPDataSourceMixin.create_group_entry')
    def test_add(self, create_group_entry):
        self.unit.add({'cn': 'tgroup'})
        create_group_entry.assert_called_with({'cn': 'tgroup'})


class GroupResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.entry = mock.Mock(spec=ldapom.LDAPEntry)
        self.unit = resources.GroupResource(self.request, self.entry)

    def test_magic_name(self):
        self.entry.cn = set(['oneone'])
        self.assertEqual(self.unit.__name__, 'oneone')

    def test_name(self):
        self.entry.cn = set(['oneone'])
        self.assertEqual(self.unit.name, 'oneone')

    @mock.patch('esauth.registry')
    def test_members_getter(self, registry):
        u_entry = mock.MagicMock()
        u_entry.uid = set(['ss'])
        registry['lc'].get_entry.return_value = u_entry
        self.entry.member = ['uid=123,dc=x', 'uid=321,dc=x']

        ret = self.unit.members
        self.assertEqual(len(ret), 2)

    @mock.patch('esauth.registry')
    def test_members_getter_ignore_blank(self, registry):
        u_entry = mock.MagicMock()
        u_entry.uid = set(['ss'])
        registry['lc'].get_entry.return_value = u_entry
        self.entry.member = ['uid=123,dc=x', 'uid=321,dc=x', '']

        ret = self.unit.members
        self.assertEqual(len(ret), 2)

    def test_unicode(self):
        self.entry.cn = ['Name']
        ret = unicode(self.unit)
        self.assertEqual(ret, u'Name')

    def test_remove(self):
        self.unit.remove()
        self.entry.delete.assert_called_with()


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

    @mock.patch('esauth.resources.LDAPDataSourceMixin.create_user_entry')
    def test_add(self, create_user_entry):
        self.unit.add('oneone')
        create_user_entry.assert_called_with('oneone')


class UserResourceTestCase(base.UnitTestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.entry = mock.Mock(spec=ldapom.LDAPEntry)
        self.entry.uid = set(['testuser'])
        self.entry.uidNumber = 10000
        self.entry.gidNumber = 10000
        self.entry.sn = ['Surnnname']
        self.entry.givenName = ['Givenname']
        self.unit = resources.UserResource(self.request, self.entry)

    def test_name(self):
        self.entry.uid = set(['oneone'])
        self.assertEqual(self.unit.__name__, 'oneone')

    def test_unicode(self):
        self.entry.uid = set(['uid'])
        self.entry.givenName = set(['F'])
        self.entry.sn = set(['L'])
        self.assertEqual(unicode(self.unit), u'F L (uid)')

    def test_set_username(self):
        self.unit.username = 'hello'
        self.assertEqual(self.entry.uid, 'hello')

    def test_set_first_name(self):
        self.unit.first_name = ['first']
        self.assertEqual(self.entry.givenName, ['first'])
        self.assertEqual(self.entry.cn, 'first Surnnname')

    def test_set_last_name(self):
        self.unit.last_name = ['last']
        self.assertEqual(self.entry.sn, ['last'])
        self.assertEqual(self.entry.cn, 'Givenname last')

    def test_set_uid_number(self):
        self.unit.uid_number = 100
        self.assertEqual(self.entry.uidNumber, 100)

    def test_set_gid_number(self):
        self.unit.gid_number = 100
        self.assertEqual(self.entry.gidNumber, 100)

    @mock.patch('esauth.resources.LDAPDataSourceMixin.get_all_groups')
    def test_remove(self, get_all_groups):
        self.entry.dn = 'cn=entry'
        grp1 = mock.Mock()
        grp1.member = ['cn=entry', 'lv=xxx']
        grp2 = mock.Mock()
        grp2.member = ['lv=xxx']
        get_all_groups.return_value = [grp1, grp2]

        self.unit.remove()

        self.assertEqual(grp1.member, ['lv=xxx'])
        self.entry.delete.assert_called_with()
        grp1.save.assert_called_with()

    @mock.patch('esauth.resources.LDAPDataSourceMixin.get_all_groups')
    def test_remove_last_member(self, get_all_groups):
        self.entry.dn = 'cn=entry'
        grp1 = mock.Mock()
        grp1.member = ['cn=entry']
        grp2 = mock.Mock()
        grp2.member = ['lv=xxx']
        get_all_groups.return_value = [grp1, grp2]

        self.unit.remove()

        self.assertEqual(grp1.member, '')
        self.entry.delete.assert_called_with()
        grp1.save.assert_called_with()


class LDAPDataSourceMixinTestCase(base.UnitTestCase):
    def setUp(self):
        self.unit = resources.LDAPDataSourceMixin()

    @mock.patch('esauth.registry', spec=Registry)
    def test_get_all_users(self, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        registry['lc'].search.return_value = "TWOTWO"

        ret = self.unit.get_all_users()
        self.assertEqual(ret, "TWOTWO")
        registry['lc'].search.assert_called_with(search_filter='objectClass=inetOrgPerson', base='dc=oneone')

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

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_user_entry_already_exist(self, LDAPEntry, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock()
        entry.exists.return_value = True
        LDAPEntry.return_value = entry

        with self.assertRaises(resources.UserAlreadyExist):
            self.unit.create_user_entry({
                'uid': 'luser',
                'givenName': 'first_name',
                'sn': 'last_name',
            })

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_user_entry_ok_no_posix_class(self, LDAPEntry, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock()
        entry.exists.return_value = False
        LDAPEntry.return_value = entry
        ret = self.unit.create_user_entry({
            'uid': 'luser',
            'userPassword': '123',
            'givenName': 'first_name',
            'sn': 'last_name',
        })
        self.assertEqual(entry.uid, 'luser')
        self.assertListEqual(entry.objectClass, ['top', 'inetOrgPerson'])
        self.assertEqual(ret, entry)

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_user_entry_set_password(self, LDAPEntry, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock()
        entry.exists.return_value = False
        LDAPEntry.return_value = entry
        self.unit.create_user_entry({
            'uid': 'luser',
            'userPassword': '123',
            'givenName': 'first_name',
            'sn': 'last_name',
        })
        entry.set_password.assert_called_with('123')

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_user_entry_ok_posix_class(self, LDAPEntry, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock()
        entry.exists.return_value = False
        LDAPEntry.return_value = entry
        ret = self.unit.create_user_entry({
            'uid': 'luser',
            'userPassword': '123',
            'uidNumber': 111,
            'gidNumber': 111,
            'givenName': 'gname',
            'sn': 'sn'
        })
        self.assertEqual(entry.uid, 'luser')
        self.assertListEqual(entry.objectClass, ['top', 'inetOrgPerson', 'posixAccount'])
        self.assertEqual(ret, entry)

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_user_entry_blank_key_ignored(self, LDAPEntry, registry):
        registry.settings = {'ldap.users_base': 'dc=oneone'}
        entry = mock.Mock()
        entry.exists.return_value = False
        LDAPEntry.return_value = entry

        self.unit.create_user_entry({
            'uid': 'luser',
            'userPassword': '123',
            'blanKey': '',
            'givenName': 'first_name',
            'sn': 'last_name',
        })
        self.assertTrue(entry.blanKey)

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_group_entry(self, LDAPEntry, registry):
        entry = mock.Mock()
        entry.exists.return_value = False
        LDAPEntry.return_value = entry
        registry.settings = {'ldap.groups_base': 'dc=base'}
        ret = self.unit.create_group_entry({'cn': 'tgroup'})
        LDAPEntry.assert_called_with(registry['lc'], 'cn=tgroup,dc=base')
        self.assertEqual(entry.member, "")
        self.assertEqual(entry.cn, "tgroup")
        entry.save.assert_called_with()
        self.assertEqual(ret, entry)

    @mock.patch('esauth.registry')
    @mock.patch('ldapom.LDAPEntry')
    def test_create_group_entry_already_exist(self, LDAPEntry, registry):
        entry = mock.Mock()
        entry.exists.return_value = True
        LDAPEntry.return_value = entry
        with self.assertRaises(resources.GroupAlreadyExist):
            self.unit.create_group_entry({'cn': 'tgroup'})


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
