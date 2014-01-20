
import unittest
import esauth.models

esauth.models.Group.base_dn = 'ou=groups,dc=example,dc=com'
esauth.models.User.base_dn = 'ou=users,dc=example,dc=com'


class UnitTestCase(unittest.TestCase):
    pass
