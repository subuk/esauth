import esauth.models as models
import tests.functional.base as base


class GroupEdgeTestCase(base.FunctionalBaseTestCase):
    def setUp(self):
        super(GroupEdgeTestCase, self).setUp()
        self.app.login(userid=1)

    def test_group_rename_does_not_work(self):
        group = models.Group(name='one')
        group.save()
        self.app.post('/groups/one/edit', status=302, params={
            'name': 'one2',
        })
        self.assertIsNotNone(models.Group.get('one'))
        self.assertIsNone(models.Group.get('one2'))

    def test_create_group_with_same_name(self):
        group = models.Group(name='one')
        group.save()
        ret = self.app.post('/groups/add', status=200, params={
            'name': 'one',
        })
        self.assertIn('Group one already exist', ret)
