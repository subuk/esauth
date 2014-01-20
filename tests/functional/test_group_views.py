import esauth.models as models
import tests.functional.base as base


class GroupViewsTestCase(base.FunctionalBaseTestCase):

    def setUp(self):
        super(GroupViewsTestCase, self).setUp()
        self.app.login(userid=1)

    def test_group_list_view(self):
        group = models.Group(name='one')
        group.save()
        group = models.Group(name='two')
        group.save()
        self.app.get('/groups')

    def test_group_create_get_form(self):
        self.app.get('/groups/add', status=200)

    def test_group_create(self):
        u1 = models.User(username='user1', first_name='hello', last_name='hello')
        u1.save()
        u2 = models.User(username='user2', first_name='hello2', last_name='hello2')
        u2.save()

        self.app.post('/groups/add', status=302, params={
            'name': 'grp12',
            'members': [u1.get_dn()]
        })
        group = models.Group.get('grp12')
        self.assertIsNotNone(group)
        self.assertEqual(group.name, 'grp12')
        self.assertEqual(group.members, ['', u1.get_dn()])

    def test_group_edit_get(self):
        group = models.Group(name='one')
        group.save()
        self.app.get('/groups/one/edit', status=200)

    def test_group_edit_post(self):
        u1 = models.User(username='user1', first_name='hello', last_name='hello')
        u1.save()
        u2 = models.User(username='user2', first_name='hello2', last_name='hello2')
        u2.save()
        group = models.Group(name='one', members=[u1.get_dn()])
        group.save()
        self.app.post('/groups/one/edit', status=302, params={
            'members': [u2.get_dn()]
        })
        group.refresh()
        self.assertEqual(group.members, ['', u2.get_dn()])

    def test_group_remove_get(self):
        group = models.Group(name='one')
        group.save()
        self.app.get('/groups/one/remove', status=200)
        self.assertIsNotNone(models.Group.get('one'))

    def test_group_remove_post(self):
        group = models.Group(name='one')
        group.save()
        self.app.post('/groups/one/remove', status=302)
        self.assertIsNone(models.Group.get('one'))

    def test_group_remove_user(self):
        u1 = models.User(username='user1', first_name='hello', last_name='hello')
        u1.save()
        group = models.Group(name='one', members=[u1.get_dn()])
        group.save()
        self.app.post('/users/user1/remove', status=302)
        group.refresh()
        self.assertEqual(group.members, [''])
