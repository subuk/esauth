
import wtforms as forms
import wtforms.validators as validators

ValidationError = forms.ValidationError


class RequiredTogether(validators.Required):
    def __init__(self, namespace, *args, **kwargs):
        self.namespace = namespace
        super(RequiredTogether, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        group = []
        for field_obj in form._fields.values():
            for v in field_obj.validators:
                if isinstance(v, RequiredTogether) and v.namespace == self.namespace:
                    group.append(field_obj)

        validation_needed = False
        for field_obj in group:
            if field_obj.raw_data[0]:
                validation_needed = True
                break

        if validation_needed:
            if not field.raw_data[0]:
                super(RequiredTogether, self).__call__(form, field)
            if field.errors:
                raise validators.ValidationError()
        else:
            field.errors[:] = []
            raise validators.StopValidation()


class UserForm(forms.Form):
    username = forms.StringField('Login', [validators.Length(min=2, max=16)])
    first_name = forms.StringField('First name', [validators.Required(), validators.Length(max=255)])
    last_name = forms.StringField('Last name', [validators.Required(), validators.Length(max=255)])
    description = forms.TextAreaField('Description')
    password = forms.PasswordField('Password')
    password2 = forms.PasswordField('Password confirmation', [validators.EqualTo('password')])

    uid_number = forms.IntegerField('UID Number', [RequiredTogether('posix_account'), validators.NumberRange(min=10000, max=65535)])
    gid_number = forms.IntegerField('GID Number', [RequiredTogether('posix_account'), validators.NumberRange(min=10000, max=65535)])
    home_directory = forms.StringField('Home directory', [RequiredTogether('posix_account'), validators.Length(min=3, max=255)])
    login_shell = forms.StringField('Login shell', [RequiredTogether('posix_account'), validators.Optional(), validators.Length(min=3, max=255)])

    def ldap_dict(self):
        return {
            'uid': self.data['username'],
            'givenName': self.data['first_name'],
            'sn': self.data['last_name'],
            'description': self.data['description'],
            'userPassword': self.data['password'],
            'uidNumber': self.data['uid_number'],
            'gidNumber': self.data['gid_number'],
            'homeDirectory': self.data['home_directory'],
            'loginShell': self.data['login_shell'],
        }


class PosixUserAccountForm(forms.Form):
    uid_number = forms.IntegerField('UID Number', [validators.NumberRange(min=10000, max=65535)])
    gid_number = forms.IntegerField('GID Number', [validators.NumberRange(min=10000, max=65535)])
    home_directory = forms.StringField('Home directory', [validators.Length(min=3, max=255)])
    login_shell = forms.StringField('Login shell', [validators.Optional(), validators.Length(min=3, max=255)])

    def ldap_dict(self):
        return {
            'uidNumber': self.data['uid_number'],
            'gidNumber': self.data['gid_number'],
            'homeDirectory': self.data['home_directory'],
            'loginShell': self.data['login_shell'],
        }


class GroupForm(forms.Form):
    name = forms.StringField("Name", [validators.Required()])
    members = forms.SelectMultipleField('Members')

    def ldap_dict(self):
        return {
            'cn': self.data['name'],
        }
