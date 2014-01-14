
import esauth


class LDAPDataSourceMixin(object):

    @property
    def lc(self):
        return esauth.registry['lc']

    @property
    def settings(self):
        return esauth.registry.settings

    def get_all_users(self):
        base = self.settings.get('ldap.users_base')
        return self.lc.search(search_filter='objectClass=account', base=base)

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


class UserResource(LDAPDataSourceMixin, object):

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
    def __init__(self, request):
        self.request = request

    def __getitem__(self, uid):
        return UserResource(self.request, self.get_user_entry(uid))

    def __iter__(self):
        for entry in self.get_all_users():
            yield UserResource(self.request, entry)


class GroupResource(LDAPDataSourceMixin, object):

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
    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        return GroupResource(self.request, self.get_group_entry(name))

    def __iter__(self):
        for entry in self.get_all_groups():
            yield GroupResource(self.request, entry)


class Root(dict):
    def __init__(self, request):
        self.request = request
        self['users'] = UserListResource(request)
        self['groups'] = GroupListResource(request)
