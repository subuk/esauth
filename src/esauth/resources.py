import esauth
import ldapom
from pyramid.decorator import reify


class LDAPEntryAlreadyExist(Exception):
    pass


class UserAlreadyExist(LDAPEntryAlreadyExist):
    pass


class GroupAlreadyExist(LDAPEntryAlreadyExist):
    pass


class LDAPDataSourceMixin(object):

    @property
    def lc(self):
        return esauth.registry['lc']

    @property
    def settings(self):
        return esauth.registry.settings

    def get_all_users(self):
        base = self.settings.get('ldap.users_base')
        return self.lc.search(search_filter='objectClass=inetOrgPerson', base=base)

    def get_user_entry(self, uid):
        base = self.settings.get('ldap.users_base')
        entry = self.lc.get_entry("uid={0},{1}".format(uid, base))
        if not entry.exists():
            raise KeyError("User {0} not found".format(uid))
        return entry

    def get_all_groups(self):
        base = self.settings.get('ldap.groups_base')
        return self.lc.search(search_filter='objectClass=groupOfNames', base=base)

    def get_group_entry(self, name):
        base = self.settings.get('ldap.groups_base')
        entry = self.lc.get_entry("cn={0},{1}".format(name, base))
        if not entry.exists():
            raise KeyError("Group {0} not found".format(name))
        return entry

    def create_user_entry(self, userinfo):
        base = self.settings.get('ldap.users_base')
        classes = ['top', 'inetOrgPerson']

        if userinfo.get('uidNumber') and userinfo.get('gidNumber'):
            classes.append('posixAccount')
            userinfo['cn'] = u"{givenName} {sn}".format(**userinfo)

        password = userinfo.pop('userPassword', None)

        dn = 'uid={0},{1}'.format(userinfo['uid'], base)
        entry = ldapom.LDAPEntry(self.lc, dn)
        if entry.exists():
            raise UserAlreadyExist(userinfo['uid'])
        entry.objectClass = classes
        for key, value in userinfo.items():
            if not value:
                continue
            setattr(entry, key, value)
        entry.save()
        if password:
            entry.set_password(password)
        return entry

    def create_group_entry(self, groupinfo):
        base = self.settings.get('ldap.groups_base')
        dn = 'cn={0},{1}'.format(groupinfo['cn'], base)
        entry = ldapom.LDAPEntry(self.lc, dn)
        if entry.exists():
            raise GroupAlreadyExist(groupinfo['cn'])
        entry.objectClass = ['top', 'groupOfNames']
        entry.cn = groupinfo['cn']
        entry.member = ""
        entry.save()
        return entry


class UserResource(LDAPDataSourceMixin, object):

    @reify
    def __name__(self):
        return list(self.entry.uid)[0]

    def __init__(self, request, entry):
        self.request = request
        self.entry = entry

    def as_dict(self):
        return {
            'uid': list(self.entry.uid)[0],
            'uidNumber': self.entry.uidNumber,
            'gidNumber': self.entry.gidNumber,
        }


class UserListResource(LDAPDataSourceMixin, object):

    __name__ = "users"

    def __init__(self, request):
        self.request = request

    def __getitem__(self, uid):
        resource = UserResource(self.request, self.get_user_entry(uid))
        resource.__parent__ = self
        return resource

    def __iter__(self):
        for entry in self.get_all_users():
            resource = UserResource(self.request, entry)
            resource.__parent__ = self
            yield resource

    def add(self, userinfo):
        return self.create_user_entry(userinfo)


class GroupResource(LDAPDataSourceMixin, object):

    @reify
    def __name__(self):
        return list(self.entry.cn)[0]

    def __init__(self, request, entry):
        self.request = request
        self.entry = entry

    def get_members(self):
        return [self.lc.get_entry(dn) for dn in self.entry.member]

    def as_dict(self):
        return {
            'cn': list(self.entry.cn)[0],
        }


class GroupListResource(LDAPDataSourceMixin, object):

    __name__ = "groups"

    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        resource = GroupResource(self.request, self.get_group_entry(name))
        resource.__parent__ = self
        return resource

    def __iter__(self):
        for entry in self.get_all_groups():
            resource = GroupResource(self.request, entry)
            resource.__parent__ = self
            yield resource

    def add(self, groupinfo):
        return self.create_group_entry(groupinfo)


class Root(dict):

    __name__ = None
    __parent__ = None

    def __init__(self, request):
        self.request = request
        self['users'] = UserListResource(request)
        self['users'].__parent__ = self
        self['groups'] = GroupListResource(request)
        self['groups'].__parent__ = self
