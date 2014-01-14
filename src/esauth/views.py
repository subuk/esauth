
from pyramid.view import view_config
import esauth.resources as resources


@view_config(context=resources.UserListResource, renderer='json')
def users_list_view(context, request):
    return {
        'users': [u.as_dict() for u in context]
    }


@view_config(context=resources.GroupListResource, renderer='json')
def group_list_view(context, request):
    return {
        'groups': [u.as_dict() for u in context]
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
