import esauth
import ldapom
from pyramid.decorator import reify
from pyramid.security import Allow, Authenticated


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

        userinfo['cn'] = u"{givenName} {sn}".format(**userinfo)

        if userinfo.get('uidNumber') and userinfo.get('gidNumber'):
            classes.append('posixAccount')

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

    def __init__(self, request, entry):
        self.request = request
        self.entry = entry

    @reify
    def __name__(self):
        return self.username

    def __unicode__(self):
        return u"{0} ({1})".format(self.full_name, self.username)

    @property
    def username(self):
        return list(self.entry.uid)[0]

    @username.setter
    def username(self, value):
        self.entry.uid = value

    @property
    def first_name(self):
        return list(self.entry.givenName)[0]

    @first_name.setter
    def first_name(self, value):
        self.entry.givenName = value
        self.entry.cn = self.full_name

    @property
    def last_name(self):
        return list(self.entry.sn)[0]

    @last_name.setter
    def last_name(self, value):
        self.entry.sn = value
        self.entry.cn = self.full_name

    @property
    def full_name(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    @property
    def uid_number(self):
        return self.entry.uidNumber

    @uid_number.setter
    def uid_number(self, value):
        if not value:
            return
        self.entry.uidNumber = int(value)

    @property
    def gid_number(self):
        return self.entry.gidNumber

    @gid_number.setter
    def gid_number(self, value):
        if not value:
            return
        self.entry.gidNumber = int(value)

    @property
    def home_directory(self):
        return self.entry.homeDirectory

    @home_directory.setter
    def home_directory(self, value):
        if not value:
            return
        self.entry.homeDirectory = value

    @property
    def login_shell(self):
        return self.entry.loginShell

    @login_shell.setter
    def login_shell(self, value):
        if not value:
            return
        self.entry.loginShell = value

    @reify
    def is_posix_account(self):
        return self.entry.is_posixAccount

    def save(self):
        self.entry.save()

    def remove(self):
        for group in self.get_all_groups():
            if self.entry.dn in group.member:
                group.fetch()
                group.member.remove(self.entry.dn)
                if not group.member:
                    group.member = ""
                group.save()
        self.entry.delete()


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

    def __init__(self, request, entry):
        self.request = request
        self.entry = entry

    @reify
    def __name__(self):
        return list(self.entry.cn)[0]

    @reify
    def name(self):
        return self.__name__

    @reify
    def members(self):
        ret = []
        for dn in self.entry.member:
            if not dn:
                continue
            entry = self.lc.get_entry(dn)
            ret.append(list(entry.uid)[0])
        return ret

    def remove(self):
        self.entry.delete()

    def __unicode__(self):
        return ','.join(self.entry.cn)


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
