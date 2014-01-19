from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid import security
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import model_path
import esauth.resources as resources
import esauth.forms as forms


@view_config(context=resources.Root, renderer='base_with_menu.jinja2')
def dashboard_view(context, request):
    return {}


@view_config(context=resources.UserListResource, renderer='user_list.jinja2')
def users_list_view(context, request):
    return {
        'users': context,
    }


@view_defaults(context=resources.UserListResource, renderer='user_form.jinja2', name='add')
class UserCreateFormView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    def get_form_kwargs(self):
        return {
            'formdata': self.request.POST or None,
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

        self.context.add(form.ldap_dict())
        self.request.session.flash({
            'type': 'success',
            'msg': 'User {username} successfully created!'.format(**form.data)
        })
        return HTTPFound(model_path(self.context))


@view_defaults(context=resources.UserResource, renderer='user_form.jinja2', name='edit')
class UserEditFormView(UserCreateFormView):

    def get_form_kwargs(self):
        kwargs = super(UserEditFormView, self).get_form_kwargs()
        kwargs['obj'] = self.context
        return kwargs

    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response

        form.populate_obj(self.context)
        self.context.save()
        self.request.session.flash({
            'type': 'success',
            'msg': 'User {0} successfully updated!'.format(self.context.username)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_defaults(context=resources.GroupListResource, renderer='group_form.jinja2', name='add')
class GroupAddView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    def get_form_kwargs(self):
        return {
            'formdata': self.request.POST,
        }

    def get_form(self):
        form = forms.GroupForm(**self.get_form_kwargs())

        form.members.choices = []
        for user in self.context.get_all_users():
            uid = user.uid.pop()
            form.members.choices.append((uid, uid))

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

        self.context.add(form.ldap_dict())
        self.request.session.flash({
            'type': 'success',
            'msg': 'Group {0} successfully created!'.format(form.data['name'])
        })
        return HTTPFound(model_path(self.context[form.data['name']], 'edit'))


@view_defaults(context=resources.GroupResource, renderer='group_form.jinja2', name='edit')
class GroupEditView(GroupAddView):

    def get_form_kwargs(self):
        kwargs = super(GroupEditView, self).get_form_kwargs()
        kwargs['obj'] = self.context
        return kwargs

    def get_form(self):
        form = super(GroupEditView, self).get_form()
        del form.name
        return form

    def post(self):
        form = self.get_form()
        if not form.validate():
            return self.response

        members = []
        for uid in form.data['members']:
            member = self.context.get_user_entry(uid)
            members.append(member.dn)
        if not members:
            members = ['']

        self.context.entry.member = members
        self.context.entry.save()
        self.request.session.flash({
            'type': 'success',
            'msg': 'Group {0} successfully updated!'.format(self.context.name)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_defaults(context=resources.GroupResource, renderer='group_remove.jinja2', name='remove')
class GroupRemoveView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    @view_config(request_method='GET')
    def get(self):
        return self.response

    @view_config(request_method='POST')
    def post(self):
        name = self.context.name
        self.context.remove()
        self.request.session.flash({
            'type': 'success',
            'msg': 'Group {0} successfully removed!'.format(name)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_defaults(context=resources.UserResource, renderer='user_remove.jinja2', name='remove')
class UserRemoveView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    @view_config(request_method='GET')
    def get(self):
        return self.response

    @view_config(request_method='POST')
    def post(self):
        username = self.context.username
        self.context.remove()
        self.request.session.flash({
            'type': 'success',
            'msg': 'User {0} successfully removed!'.format(username)
        })
        return HTTPFound(model_path(self.context.__parent__))


@view_config(context=resources.GroupListResource, renderer='group_list.jinja2')
def group_list_view(context, request):
    return {
        'groups': context,
    }


LOGIN_URL = '/login'


@forbidden_view_config(renderer='403.jinja2')
def forbidden_view(response, request):
    if not getattr(request, 'user', None):
        return HTTPFound("{0}?next={1}".format(LOGIN_URL, request.path))
    request.response.status = 403
    return {}


@view_config(context=resources.Root, name='logout')
def logout(request):
    security.forget(request)
    return HTTPFound('/')


@view_defaults(context=resources.Root, renderer='login.jinja2', permission=security.NO_PERMISSION_REQUIRED, name='login')
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
