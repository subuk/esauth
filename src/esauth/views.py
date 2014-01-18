from pyramid.view import view_config, view_defaults
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
        'users': [u.entry for u in context]
    }


@view_defaults(context=resources.UserListResource, renderer='user_form.jinja2', name='add')
class UserCreateFormView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {}

    @view_config(request_method='GET')
    def get(self):
        return {
            'main_user_form': forms.UserForm(),
            'posix_user_form': forms.PosixUserAccountForm(),
        }

    @view_config(request_method='POST')
    def post(self):
        main_user_form = forms.UserForm(self.request.POST)
        posix_user_form = forms.PosixUserAccountForm(self.request.POST)
        self.response.update({
            'main_user_form': main_user_form,
            'posix_user_form': posix_user_form,
            'posix_account': self.request.POST.get('posix_account')
        })

        if not main_user_form.validate():
            return self.response

        if 'posix_account' in self.request.POST and not posix_user_form.validate():
            return self.response

        try:
            self.context[main_user_form.data['login']]
        except KeyError:
            pass
        else:
            main_user_form.login.errors.append(u"User {login} already exist".format(**main_user_form.data))
            return self.response

        userinfo = {}
        userinfo.update(main_user_form.ldap_dict())
        userinfo.update(posix_user_form.ldap_dict())

        self.context.add(userinfo)
        return HTTPFound(model_path(self.context[userinfo['uid']]))


@view_config(context=resources.GroupListResource, renderer='group_list.jinja2')
def group_list_view(context, request):
    return {
        'groups': [u for u in context]
    }


@view_config(context=resources.UserResource, renderer='json')
def user_view(context, request):
    return {'user': context.as_dict()}


@view_config(context=resources.GroupResource, renderer='json')
def group_view(context, request):
    return {'group': context.as_dict()}


@view_config(context=resources.GroupResource, name='members', renderer='json')
def group_members_view(context, request):
    render = lambda entry: user_view(resources.UserResource(request, entry), request)
    return {'members': [render(entry) for entry in context.get_members()]}
