
import esauth.orm as orm


class Group(orm.Base):

    all_search_filter = 'objectClass=groupOfNames'
    object_classes = {'groupOfNames'}

    name = orm.SingleValueField('cn', primary=True)
    members = orm.Field('member', default=[])

    @members.decoder
    def decode_members(self, value):
        ret = ['']
        for member_dn in value:
            if not member_dn:
                continue
            member = User.get(member_dn)
            if not member:
                continue
            ret.append(member_dn)
        return ret


class User(orm.Base):

    all_search_filter = 'objectClass=inetOrgPerson'
    object_classes = {'See pre_save'}

    username = orm.SingleValueField('uid', primary=True)
    first_name = orm.SingleValueField('givenName', default='')
    last_name = orm.SingleValueField('sn')
    description = orm.SingleValueField('description', default=None, nullable=True, null_if_blank=True)
    password = orm.Field('userPassword', nullable=True)
    uid_number = orm.Field('uidNumber', nullable=True)
    gid_number = orm.Field('gidNumber', nullable=True)
    home_directory = orm.Field('homeDirectory', nullable=True)
    login_shell = orm.Field('loginShell', nullable=True)

    @description.encoder
    def encode_description(self, value):
        if not value:
            return
        return value

    @password.encoder
    def encode_password(self, value):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return value

    @property
    def full_name(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    def pre_save(self, entry):
        entry.objectClass = ['top', 'inetOrgPerson']
        for attr_name in ('uidNumber', 'gidNumber', 'homeDirectory', 'loginShell'):
            if entry.get_attribute(attr_name):
                entry.objectClass = ['top', 'posixAccount', 'inetOrgPerson']
                break
        entry.cn = u"{0} {1}".format(self.first_name, self.last_name)
