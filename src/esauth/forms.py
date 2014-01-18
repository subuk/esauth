
import wtforms as forms
import wtforms.validators as validators

ValidationError = forms.ValidationError


class UserForm(forms.Form):
    login = forms.StringField('Login', [validators.Length(min=2, max=16)])
    first_name = forms.StringField('First name', [validators.Required(), validators.Length(max=255)])
    last_name = forms.StringField('Last name', [validators.Required(), validators.Length(max=255)])
    description = forms.TextAreaField('Description')
    password = forms.PasswordField('Password')
    password2 = forms.PasswordField('Password confirmation', [validators.EqualTo('password')])

    def ldap_dict(self):
        return {
            'uid': self.data['login'],
            'givenName': self.data['first_name'],
            'sn': self.data['last_name'],
            'description': self.data['description'],
            'userPassword': self.data['password'],
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
