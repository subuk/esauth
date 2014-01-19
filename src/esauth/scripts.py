
import sys
import string
import random
import argparse


CONFIG_TEMPLATE = """
###
# ESAuth configuration
###

[app:main]
use = egg:esauth

session.secret = {session_secret}

ldap.bind_dn = {ldap_bind_dn}
ldap.bind_password = {ldap_bind_password}
ldap.uri = {ldap_uri}

ldap.users_base = {ldap_users_base}
ldap.groups_base = {ldap_groups_base}

[server:main]
use = egg:waitress#main
host = {host}
port = {port}

###
# logging configuration
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/logging.html
###

[loggers]
keys = root, esauth

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_esauth]
level = DEBUG
qualname = esauth
handlers =

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s

"""


def get_value(prompt, default='', type=str, blank=False):
    full_prompt = "{0} [{1}]:".format(prompt, default)

    while True:
        value = raw_input(full_prompt).strip() or default
        if not value:
            print >> sys.stderr, "Bad value"
            continue
        try:
            return type(value)
            return value
        except ValueError:
            print >> sys.stderr, "Bad value"


def generate_prod_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-file', '-o', default='/dev/stdout')
    args = parser.parse_args()

    ldap_base = get_value('LDAP Base', default='dc=example,dc=com')

    params = {
        'host': get_value('ESAuth listen host', default='0.0.0.0'),
        'port': get_value('ESAuth listen port', default='6543', type=int),
        'ldap_users_base': get_value('LDAP users root', default='ou=users,%s' % ldap_base),
        'ldap_groups_base': get_value('LDAP users root', default='ou=groups,%s' % ldap_base),
        'ldap_bind_dn': get_value('LDAP bind dn', default='cn=admin,%s' % ldap_base),
        'ldap_bind_password': get_value('LDAP bind password'),
        'ldap_uri': get_value('LDAP URI', default='ldap://localhost:389'),
    }
    params['session_secret'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(30))

    with open(args.output_file, 'w') as f:
        cfg = CONFIG_TEMPLATE.format(**params)
        f.write(cfg)

    print >> sys.stderr, """
Config file written to {0}
""".format(args.output_file)
