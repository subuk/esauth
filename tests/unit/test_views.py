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
        self.assertIn('form', ret)
        self.assertIsInstance(ret['form'], views.forms.UserForm)

    @mock.patch('esauth.forms.UserForm')
    def test_post_form_invalid(self, UserForm):
        context = mock.MagicMock(spec=testing.DummyResource)
        request = testing.DummyRequest(params={
            'one': 'two',
        })
        UserForm().validate.return_value = False
        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertIn('form', ret)
        self.assertEqual(ret['form'], UserForm())

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
        get_all_users = mock.Mock()
        get_all_users.return_value = [mock.Mock()]
        context.get_all_users = get_all_users
        return views.GroupAddView(context, request)

    @mock.patch('esauth.forms.GroupForm')
    def test_get(self, GroupForm):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)
        ret = unit.get()
        self.assertIn('form', ret)
        self.assertEqual(ret['form'], GroupForm())

    @mock.patch('esauth.forms.GroupForm')
    def test_get_form_on_get_request(self, GroupForm):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)
        unit.get_form()
        GroupForm.assert_called_with(formdata={})

    @mock.patch('esauth.forms.GroupForm')
    def test_get_form_on_post_request(self, GroupForm):
        context = testing.DummyResource()
        request = testing.DummyRequest(params={
            'name': 'hello',
        })
        unit = self.create_unit(context, request)
        unit.get_form()
        GroupForm.assert_called_with(formdata={'name': 'hello'})

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

    def test_get_form_kwargs(self):
        context = testing.DummyResource()
        request = testing.DummyRequest(params={
            'name': 'test',
        })
        unit = self.create_unit(context, request)
        ret = unit.get_form_kwargs()
        self.assertIn('formdata', ret)
        self.assertDictEqual(ret['formdata'], {'name': 'test'})


class GroupEditViewTestCase(base.UnitTestCase):

    def create_unit(self, context, request):
        return views.GroupEditView(context, request)

    def test_get_form_kwargs(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)
        ret = unit.get_form_kwargs()
        self.assertIn('obj', ret)
        self.assertEqual(ret['obj'], context)

    @mock.patch('esauth.forms.GroupForm')
    def test_post_invalid(self, GroupForm):
        context = testing.DummyResource()
        get_all_users = mock.Mock()
        context.get_all_users = get_all_users
        request = testing.DummyRequest({
            'one': 'two',
        })

        GroupForm().validate.return_value = False
        get_all_users.return_value = [mock.Mock(), mock.Mock()]
        unit = self.create_unit(context, request)
        unit.post()
        GroupForm().validate.assert_called_with()

    @mock.patch('esauth.forms.GroupForm')
    def test_post(self, GroupForm):
        context = testing.DummyResource()
        get_all_users = mock.Mock()
        context.get_all_users = get_all_users
        context.entry = mock.Mock()
        context.get_user_entry = mock.Mock()
        data = {
            'name': 'hello',
            'members': ['one', 'two']
        }
        request = testing.DummyRequest(data)

        GroupForm().validate.return_value = True
        GroupForm().data = data
        get_all_users.return_value = [mock.Mock(), mock.Mock()]

        unit = self.create_unit(context, request)
        ret = unit.post()
        GroupForm().validate.assert_called_with()
        self.assertIsInstance(ret, r.HTTPFound)

    @mock.patch('esauth.forms.GroupForm')
    def test_post_no_members(self, GroupForm):
        context = testing.DummyResource()
        get_all_users = mock.Mock()
        context.get_all_users = get_all_users
        context.entry = mock.Mock()
        context.get_user_entry = mock.Mock()
        data = {
            'name': 'hello',
            'members': []
        }
        request = testing.DummyRequest(data)

        GroupForm().validate.return_value = True
        GroupForm().data = data
        get_all_users.return_value = []

        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertEqual(context.entry.member, [''])
        self.assertIsInstance(ret, r.HTTPFound)


class GroupDeleteViewTestCase(base.UnitTestCase):

    def create_unit(self, context, request):
        return views.GroupRemoveView(context, request)

    def test_get(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)
        ret = unit.get()
        self.assertEqual(ret, {})

    def test_post(self):
        context = testing.DummyResource()
        context.remove = mock.Mock()
        request = testing.DummyRequest(params={})
        unit = self.create_unit(context, request)
        ret = unit.post()
        context.remove.assert_called_with()
        self.assertIsInstance(ret, r.HTTPFound)


class UserRemoveViewTestCase(base.UnitTestCase):

    def create_unit(self, context, request):
        return views.UserRemoveView(context, request)

    def test_get(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        unit = self.create_unit(context, request)
        ret = unit.get()
        self.assertDictEqual(ret, {})

    def test_post(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        context.remove = mock.Mock()
        unit = self.create_unit(context, request)
        ret = unit.post()
        self.assertIsInstance(ret, r.HTTPFound)
        context.remove.assert_called_with()
