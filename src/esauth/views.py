from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid import security
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import model_path
import esauth.resources as resources
import esauth.forms as forms
import esauth.models as models

LOGIN_URL = '/login'


@view_config(context=resources.Root, renderer='base_with_menu.jinja2')
def dashboard_view(context, request):  # pragma: no cover
    return {}


@view_config(context=resources.UserListResource, renderer='user/list.jinja2')
def users_list_view(context, request):
    return {
        'users': context,
    }


@view_defaults(context=resources.UserListResource, renderer='user/form.jinja2', name='add')
class UserCreateFormView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}
        self.model = models.User()

    def get_form_kwargs(self):
        return {
            'formdata': self.request.POST or None,
            'obj': self.model,
        }

    def get_form(self):
        form = forms.UserForm(**self.get_form_kwargs())
        self.response.update({
            'form': form,
        })
        return form

    @view_config(request_method='GET')
    def get(self):
        return {
            'form': self.get_form(),
        }

    @view_config(request_method='POST')
    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response

        try:
            self.context[form.data['username']]
        except KeyError:
            pass
        else:
            form.username.errors.append(u"User {username} already exist".format(**form.data))
            return self.response

        form.populate_obj(self.model)
        self.model.save()
        self.request.session.flash({
            'type': 'success',
            'msg': 'User {username} successfully created!'.format(**form.data)
        })
        return HTTPFound(model_path(self.context))


@view_defaults(context=resources.UserResource, renderer='user/form.jinja2', name='edit')
class UserEditFormView(UserCreateFormView):

    def __init__(self, context, request):
        super(UserEditFormView, self).__init__(context, request)
        self.model = context.model

    def get_form(self):
        form = super(UserEditFormView, self).get_form()
        del form.username
        return form

    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response
        form.populate_obj(self.model)
        self.model.save()
        self.request.session.flash({
            'type': 'success',
            'msg': 'User {0} successfully updated!'.format(self.context.model.username)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_defaults(context=resources.GroupListResource, renderer='group/form.jinja2', name='add')
class GroupAddView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}
        self.model = models.Group()

    def get_form_kwargs(self):
        return {
            'formdata': self.request.POST,
            'obj': self.model,
        }

    def get_form(self):
        form = forms.GroupForm(**self.get_form_kwargs())

        form.members.choices = []
        for user in models.User.all():
            form.members.choices.append((user.get_dn(), user.username))

        self.response.update({
            'form': form,
        })
        return form

    @view_config(request_method='GET')
    def get(self):
        return {
            'form': self.get_form(),
        }

    @view_config(request_method='POST')
    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response

        try:
            self.context[form.data['name']]
        except KeyError:
            pass
        else:
            form.name.errors.append(u"Group {name} already exist".format(**form.data))
            return self.response

        form.populate_obj(self.model)
        self.model.save()
        self.request.session.flash({
            'type': 'success',
            'msg': 'Group {0} successfully created!'.format(form.data['name'])
        })
        return HTTPFound(model_path(self.context[form.data['name']], 'edit'))


@view_defaults(context=resources.GroupResource, renderer='group/form.jinja2', name='edit')
class GroupEditView(GroupAddView):

    def __init__(self, context, request):
        super(GroupEditView, self).__init__(context, request)
        self.model = context.model

    def get_form(self):
        form = super(GroupEditView, self).get_form()
        del form.name
        return form

    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response

        # members = []
        # for uid in form.data['members']:
        #     member = self.context.get_user_entry(uid)
        #     members.append(member.dn)
        # if not members:
        #     members = ['']

        form.populate_obj(self.model)
        self.model.save()

        self.request.session.flash({
            'type': 'success',
            'msg': 'Group {0} successfully updated!'.format(self.model.name)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_defaults(context=resources.GroupResource, renderer='group/remove.jinja2', name='remove')
class GroupRemoveView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}
        self.model = context.model

    @view_config(request_method='GET')
    def get(self):
        return self.response

    @view_config(request_method='POST')
    def post(self):
        name = self.model.name
        self.model.remove()
        self.request.session.flash({
            'type': 'success',
            'msg': 'Group {0} successfully removed!'.format(name)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_defaults(context=resources.UserResource, renderer='user/remove.jinja2', name='remove')
class UserRemoveView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.model = context.model
        self.response = {}

    @view_config(request_method='GET')
    def get(self):
        return self.response

    @view_config(request_method='POST')
    def post(self):
        username = self.model.username
        self.model.remove()
        self.request.session.flash({
            'type': 'success',
            'msg': 'User {0} successfully removed!'.format(username)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_config(context=resources.GroupListResource, renderer='group/list.jinja2')
def group_list_view(context, request):
    return {
        'groups': context,
    }


@forbidden_view_config(renderer='403.jinja2')
def forbidden_view(response, request):  # pragma: no cover
    if not getattr(request, 'user', None):
        return HTTPFound("{0}?next={1}".format(LOGIN_URL, request.path))
    request.response.status = 403
    return {}


@view_config(context=resources.Root, name='logout')
def logout(request):  # pragma: no cover
    security.forget(request)
    return HTTPFound('/')


@view_defaults(context=resources.Root, renderer='auth/login.jinja2', permission=security.NO_PERMISSION_REQUIRED, name='login')
class LoginView(object):

    form_class = forms.LoginForm

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    def get_form_kwargs(self):
        return {
            'formdata': self.request.POST or None,
        }

    def get_form(self):
        form = self.form_class(**self.get_form_kwargs())
        self.response.update({
            'form': form,
        })
        return form

    @view_config(request_method='GET')
    def get(self):
        return {
            'form': self.get_form()
        }

    @view_config(request_method='POST')
    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response
        security.remember(self.request, 'admin_user')
        redirect_url = self.request.params.get('next') or '/'
        return HTTPFound(redirect_url)
