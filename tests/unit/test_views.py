import mock
import pyramid.testing as testing
import pyramid.httpexceptions as r
import esauth.views as views
import tests.unit.base as base


class UserCreateFormViewTestCase(base.UnitTestCase):

    def create_unit(self, context, request):
        return views.UserCreateFormView(context, request)

    def test_get(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)

        ret = unit.get()
        self.assertIn('main_user_form', ret)
        self.assertIn('posix_user_form', ret)
        self.assertIsInstance(ret['main_user_form'], views.forms.UserForm)
        self.assertIsInstance(ret['posix_user_form'], views.forms.PosixUserAccountForm)

    @mock.patch('esauth.forms.UserForm')
    @mock.patch('esauth.forms.PosixUserAccountForm')
    def test_post_main_form_invalid(self, PosixUserAccountForm, UserForm):
        context = mock.MagicMock(spec=testing.DummyResource)
        request = testing.DummyRequest(params={
            'one': 'two',
        })
        UserForm().validate.return_value = False
        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertIn('main_user_form', ret)
        self.assertEqual(ret['main_user_form'], UserForm())

    @mock.patch('esauth.forms.UserForm')
    @mock.patch('esauth.forms.PosixUserAccountForm')
    def test_post_posix_account_form_invalid(self, PosixUserAccountForm, UserForm):
        context = mock.MagicMock(spec=testing.DummyResource)
        request = testing.DummyRequest(params={
            'posix_account': 'yes',
        })
        UserForm().validate.return_value = True
        PosixUserAccountForm().validate.return_value = False
        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertIn('posix_account', ret)
        self.assertEqual(ret['posix_account'], 'yes')
        self.assertEqual(ret['posix_user_form'], PosixUserAccountForm())

    @mock.patch('esauth.forms.UserForm')
    @mock.patch('esauth.forms.PosixUserAccountForm')
    def test_post_user_already_exist(self, PosixUserAccountForm, UserForm):
        context = mock.MagicMock(spec=testing.DummyResource)
        request = testing.DummyRequest(params={
            'login': 'user',
        })
        UserForm().data = {'login': 'user'}

        unit = self.create_unit(context, request)
        unit.post()
        UserForm().login.errors.append.assert_called_with("User user already exist")

    @mock.patch('esauth.forms.UserForm')
    @mock.patch('esauth.forms.PosixUserAccountForm')
    def test_post_ok(self, PosixUserAccountForm, UserForm):
        context = mock.MagicMock(spec=testing.DummyResource)
        request = testing.DummyRequest(params={
            'login': 'user',
        })
        context.__getitem__.side_effect = [KeyError('user'), testing.DummyResource()]
        context.add = mock.Mock()
        context.add.return_value = 'OK'
        UserForm().data = {'login': 'user'}
        UserForm().ldap_dict.return_value = {'uid': 'user'}

        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertIsInstance(ret, r.HTTPFound)


class GroupAddViewTestCase(base.UnitTestCase):

    def create_unit(self, context, request):
        return views.GroupAddView(context, request)

    def test_get(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)
        ret = unit.get()
        self.assertIn('form', ret)
        self.assertIsInstance(ret['form'], views.forms.GroupForm)

    @mock.patch('esauth.forms.GroupForm')
    def test_post_invalid(self, GroupForm):
        context = testing.DummyResource()
        request = testing.DummyRequest(params={
            'one': 'test',
        })
        unit = self.create_unit(context, request)
        GroupForm().validate.return_value = False
        ret = unit.post()
        self.assertIn('form', ret)

    @mock.patch('esauth.forms.GroupForm')
    def test_post_group_already_exist(self, GroupForm):
        context = testing.DummyResource()
        request = testing.DummyRequest(params={
            'name': 'test',
        })
        unit = self.create_unit(context, request)
        GroupForm().data = {'name': 'test'}
        context['test'] = testing.DummyResource('OK')
        ret = unit.post()
        self.assertIn('form', ret)

    @mock.patch('esauth.forms.GroupForm')
    def test_post_ok(self, GroupForm):
        context = testing.DummyResource()
        request = testing.DummyRequest(params={
            'name': 'test',
        })
        GroupForm().data = {'name': 'test'}
        context.add = lambda x: context.__setitem__('test', testing.DummyResource('OK'))

        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertIsInstance(ret, r.HTTPFound)
