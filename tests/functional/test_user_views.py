import esauth.models as models
import esauth.resources as resources
import tests.functional.base as base


class UserViewsTestCase(base.FunctionalBaseTestCase):

    def setUp(self):
        super(UserViewsTestCase, self).setUp()
        self.app.login(userid=1)

    def test_user_list_view(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        user = models.User(username='hello2', first_name='hello', last_name='hello')
        user.save()
        ret = self.app.get('/users', status=200)
        self.assertIsInstance(ret.view_context, resources.UserListResource)

    def test_user_create_get_form(self):
        self.app.get('/users/add', status=200)

    def test_user_create_no_posix(self):
        self.app.post('/users/add', status=302, params={
            'username': 'test111',
            'first_name': 'test111',
            'last_name': 'test111',
        })
        user = models.User.get('test111')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test111')
        self.assertEqual(user.first_name, 'test111')
        self.assertEqual(user.last_name, 'test111')

    def test_user_create_no_posix_form_invalid(self):
        ret = self.app.post('/users/add', status=200, params={
            'username': 'test111',
            'first_name': 'test111',
        })
        user = models.User.get('test111')
        self.assertIsNone(user)
        self.assertIn('This field is required', ret)

    def test_user_create_posix(self):
        self.app.post('/users/add', status=302, params={
            'username': u'test111',
            'first_name': u'test111',
            'last_name': u'test111',
            'uid_number': u'10000',
            'gid_number': u'10000',
            'home_directory': u'/home/xx',
            'login_shell': u'/bin/bash',
        })
        user = models.User.get('test111')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test111')
        self.assertEqual(user.first_name, 'test111')
        self.assertEqual(user.last_name, 'test111')
        self.assertEqual(user.uid_number, 10000)
        self.assertEqual(user.gid_number, 10000)
        self.assertEqual(user.home_directory, '/home/xx')
        self.assertEqual(user.login_shell, '/bin/bash')

    def test_user_create_posix_form_invalid(self):
        ret = self.app.post('/users/add', status=200, params={
            'username': 'test111',
            'first_name': 'test111',
            'last_name': 'test111',
            'uid_number': '10000',
            'gid_number': '',
            'home_directory': '/home/xx',
            'login_shell': '/bin/bash',
        })
        user = models.User.get('test111')
        self.assertIsNone(user)
        self.assertIn('This field is required', ret)

    def test_user_edit_get_form(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        ret = self.app.get('/users/hello/edit', status=200)
        self.assertIsInstance(ret.view_context, resources.UserResource)

    def test_user_edit_save(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        self.app.post('/users/hello/edit', status=302, params={
            'username': 'hello',
            'first_name': 'test111',
            'last_name': 'test22',
        })
        user.refresh()
        self.assertEqual(user.username, 'hello')
        self.assertEqual(user.first_name, 'test111')
        self.assertEqual(user.last_name, 'test22')

    def test_user_remove_get(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        self.app.get('/users/hello/remove', status=200)
        self.assertTrue(user.exists())

    def test_user_remove_post(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        self.app.post('/users/hello/remove', status=302)
        self.assertFalse(user.exists())
