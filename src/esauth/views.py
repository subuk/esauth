from pyramid.view import view_config
import esauth.resources as resources


@view_config(context=resources.Root, renderer='base_with_menu.jinja2')
def dashboard_view(context, request):
    return {}


@view_config(context=resources.UserListResource, renderer='user_list.jinja2')
def users_list_view(context, request):
    return {
        'users': [u.entry for u in context]
    }


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
