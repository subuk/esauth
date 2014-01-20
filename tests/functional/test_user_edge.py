import esauth.models as models
import tests.functional.base as base


class UserEdgeTestCase(base.FunctionalBaseTestCase):
    def setUp(self):
        super(UserEdgeTestCase, self).setUp()
        self.app.login(userid=1)

    def test_user_rename_does_not_work(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        self.app.post('/users/hello/edit', status=302, params={
            'username': 'hello2',
            'first_name': 'hello',
            'last_name': 'hello',
        })
        self.assertIsNotNone(models.User.get('hello'))
        self.assertIsNone(models.User.get('hello2'))

    def test_create_user_with_same_username(self):
        user = models.User(username='hello', first_name='hello', last_name='hello')
        user.save()
        ret = self.app.post('/users/add', status=200, params={
            'username': 'hello',
            'first_name': 'hello',
            'last_name': 'hello',
        })
        self.assertIn('User hello already exist', ret)
