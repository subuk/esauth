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
            self.context[form.data['login']]
        except KeyError:
            pass
        else:
            form.login.errors.append(u"User {login} already exist".format(**form.data))
            return self.response

        self.context.add(form.ldap_dict())
        return HTTPFound(model_path(self.context[form.data['login']]))


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
        self.context.remove()
        return HTTPFound(model_path(self.context.__parent__))


@view_config(context=resources.GroupListResource, renderer='group_list.jinja2')
def group_list_view(context, request):
    return {
        'groups': context,
    }


@view_config(context=resources.UserResource, renderer='json')
def user_view(context, request):
    return {'user': context.as_dict()}


@view_config(context=resources.GroupResource, name='members', renderer='json')
def group_members_view(context, request):
    render = lambda entry: user_view(resources.UserResource(request, entry), request)
    return {'members': [render(entry) for entry in context.get_members()]}
