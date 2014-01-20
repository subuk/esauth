
import mock
import ldapom
import pyramid.testing as testing
import esauth.models as models
import esauth.resources as resources
import tests.unit.base as base
from pyramid.registry import Registry


class GroupListResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.unit = resources.GroupListResource(self.request)

    @mock.patch('esauth.models.Group')
    @mock.patch('esauth.resources.GroupResource')
    def test_getitem(self, GroupResource, Group):
        Group.get.return_value = 'DUMMY_ENTRY'
        ret = self.unit['oneoneone']
        self.assertIsNotNone(ret)
        GroupResource.assert_called_with(self.request, 'DUMMY_ENTRY')

    @mock.patch('esauth.models.Group')
    @mock.patch('esauth.resources.GroupResource')
    def test_iter(self, GroupResource, Group):
        Group.all.return_value = ['DUMMY_ENTRY_1', 'DUMMY_ENTRY_2']
        rets = []
        for x in self.unit:
            rets.append(x)
        self.assertEqual(len(rets), 2)
        GroupResource.assert_called_with(self.request, 'DUMMY_ENTRY_2')


class GroupResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.model = mock.Mock(spec=models.Group)
        self.unit = resources.GroupResource(self.request, self.model)

    def test__name__(self):
        self.model.name = 'oneone'
        self.assertEqual(self.unit.__name__, 'oneone')

    def test_unicode(self):
        self.model.name = 'Name'
        ret = unicode(self.unit)
        self.assertEqual(ret, u'Name')


class UserListResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.unit = resources.UserListResource(self.request)

    @mock.patch('esauth.models.User')
    def test_getitem(self, User):
        User.get.return_value = 'USER'
        ret = self.unit['oneoneone']
        self.assertIsInstance(ret, resources.UserResource)
        self.assertEqual(ret.__parent__, self.unit)

    @mock.patch('esauth.models.User')
    def test_iter(self, User):
        User.all.return_value = ['DUMMY_ENTRY_1', 'DUMMY_ENTRY_2']
        rets = []
        for x in self.unit:
            rets.append(x)
        self.assertEqual(len(rets), 2)
        self.assertEqual(rets[0].__parent__, self.unit)
        self.assertEqual(rets[1].__parent__, self.unit)
        self.assertIsInstance(rets[0], resources.UserResource)
        self.assertIsInstance(rets[1], resources.UserResource)


class UserResourceTestCase(base.UnitTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.user = mock.Mock(spec=models.User)
        self.user.username = 'testuser'
        self.user.uid_number = 10000
        self.user.gid_number = 10000
        self.user.last_name = 'Surnnname'
        self.user.first_name = 'Givenname'
        self.user.full_name = 'Givenname Surnnname'
        self.unit = resources.UserResource(self.request, self.user)

    def test_name(self):
        self.assertEqual(self.unit.__name__, 'testuser')

    def test_unicode(self):
        self.assertEqual(unicode(self.unit), u'Givenname Surnnname (testuser)')


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
