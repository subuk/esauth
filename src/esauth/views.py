from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid import security
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import model_path
from pyramid.decorator import reify
import esauth.resources as resources
import esauth.forms as forms
import esauth.models as models

LOGIN_URL = '/login'


class BaseFormView(object):

    form_class = None
    success_url = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    def __call__(self):
        method = self.request.method.lower()
        return getattr(self, method)()

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

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        return HTTPFound(self.get_success_url())

    def form_invalid(self, form):
        return self.response

    def get(self):
        return {
            'form': self.get_form(),
        }

    def post(self):
        form = self.get_form()
        if form.validate():
            return self.form_valid(form)
        return self.form_invalid(form)


class BaseModelFormView(BaseFormView):
    model_class = None
    flash_message = None

    @reify
    def model(self):
        return getattr(self.context, 'model', None) or self.model_class()

    def add_message(self, form_data):
        self.request.session.flash({
            'type': 'success',
            'msg': self.flash_message.format(**form_data)
        })

    def form_valid(self, form):
        form.populate_obj(self.model)
        self.model.save()
        if self.flash_message:
            self.add_message(form.data)
        return super(BaseModelFormView, self).form_valid(form)

    def get_success_url(self):
        return model_path(self.context)


class CreateModelFormView(BaseModelFormView):
    pass


class EditModelFormView(BaseModelFormView):

    def get_form_kwargs(self):
        kwargs = super(EditModelFormView, self).get_form_kwargs()
        kwargs['obj'] = self.model
        return kwargs


class RemoveModelFormView(BaseModelFormView):
    form_class = None
    model_class = None

    def get_success_url(self):
        return model_path(self.context.__parent__)

    def get_form(self):
        return

    def post(self):
        self.model.remove()
        return HTTPFound(self.get_success_url())


@view_config(context=resources.UserListResource, renderer='user/form.jinja2', name='add')
class UserCreateFormView(CreateModelFormView):
    form_class = forms.UserForm
    model_class = models.User
    flash_message = 'User {username} successfully created!'


@view_config(context=resources.UserResource, renderer='user/form.jinja2', name='edit')
class UserEditFormView(EditModelFormView):
    form_class = forms.UserForm
    model_class = models.User
    flash_message = 'User successfully updated!'

    def get_form(self):
        form = super(UserEditFormView, self).get_form()
        del form.username
        return form

    def get_success_url(self):
        return model_path(self.context.__parent__)


@view_config(context=resources.GroupListResource, renderer='group/form.jinja2', name='add')
class GroupAddView(CreateModelFormView):
    form_class = forms.GroupForm
    model_class = models.Group
    flash_message = 'Group {name} successfully created!'

    def get_form(self):
        form = super(GroupAddView, self).get_form()
        form.members.choices = []
        for user in models.User.all():
            form.members.choices.append((user.get_dn(), user.username))
        return form


@view_config(context=resources.GroupResource, renderer='group/form.jinja2', name='edit')
class GroupEditView(GroupAddView):

    flash_message = 'Group successfully updated!'

    def get_form(self):
        form = super(GroupEditView, self).get_form()
        del form.name
        return form

    def get_success_url(self):
        return model_path(self.context.__parent__)


@view_config(context=resources.GroupResource, renderer='group/remove.jinja2', name='remove')
class GroupRemoveView(RemoveModelFormView):
    flash_message = 'Group successfully removed!'


@view_config(context=resources.UserResource, renderer='user/remove.jinja2', name='remove')
class UserRemoveView(RemoveModelFormView):
    flash_message = 'User successfully removed!'


@view_config(context=resources.Root, renderer='base_with_menu.jinja2')
def dashboard_view(context, request):  # pragma: no cover
    return {}


@view_config(context=resources.UserListResource, renderer='user/list.jinja2')
def users_list_view(context, request):
    return {
        'users': context,
    }


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
