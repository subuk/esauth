from pyramid.decorator import reify
from pyramid.security import Allow, Authenticated
from esauth import models


class UserResource(object):

    def __init__(self, request, user):
        self.request = request
        self.model = user

    @reify
    def __name__(self):
        return self.model.username

    def __unicode__(self):
        return u"{0} ({1})".format(self.model.full_name, self.model.username)


class UserListResource(object):

    __name__ = "users"

    def __init__(self, request):
        self.request = request

    def __getitem__(self, username):
        user = models.User.get(username)
        if not user:
            raise KeyError(username)

        resource = UserResource(self.request, user)
        resource.__parent__ = self
        return resource

    def __iter__(self):
        for user in models.User.all():
            resource = UserResource(self.request, user)
            resource.__parent__ = self
            yield resource


class GroupResource(object):

    def __init__(self, request, group):
        self.request = request
        self.model = group

    @reify
    def __name__(self):
        return self.model.name

    def __unicode__(self):
        return unicode(self.model.name)


class GroupListResource(object):

    __name__ = "groups"

    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        group = models.Group.get(name)
        if not group:
            raise KeyError(group)

        resource = GroupResource(self.request, group)
        resource.__parent__ = self
        return resource

    def __iter__(self):
        for entry in models.Group.all():
            resource = GroupResource(self.request, entry)
            resource.__parent__ = self
            yield resource


class Root(dict):

    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Authenticated, 'edit'),
        (Allow, Authenticated, 'view'),
    ]

    def __init__(self, request):
        self.request = request
        self['users'] = UserListResource(request)
        self['users'].__parent__ = self
        self['groups'] = GroupListResource(request)
        self['groups'].__parent__ = self
