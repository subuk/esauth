import types
import mock
import ldapom
import esauth.orm as orm
import tests.unit.base as base


class TestField(object):
    def __init__(self, name='', primary=False):
        self.primary = primary
        self.name = name


class BaseMetaTestCase(base.UnitTestCase):

    test_field_cls = TestField

    def call_unit(self, attrs):
        return type('Model', (orm.Base,), attrs)

    def test_no_primary_field(self):
        with self.assertRaises(orm.InvalidDefinition):
            self.call_unit({})

    @mock.patch('esauth.orm.Field', TestField)
    def test_two_primary_field(self):
        with self.assertRaises(orm.InvalidDefinition):
            self.call_unit({
                'one': TestField(primary=True),
                'two': TestField(primary=True),
            })

    @mock.patch('esauth.orm.Field', TestField)
    def test_fields_attr_set(self):
        """
            Test cls._fields set.
        """
        attrs = {
            'one': TestField(primary=True),
            'two': TestField(),
        }
        ret = self.call_unit(attrs)
        self.assertTrue(hasattr(ret, '_fields'))

    @mock.patch('esauth.orm.Field', TestField)
    def test_primary_field_attr_set(self):
        attrs = {
            'one': TestField(primary=True),
            'two': TestField(),
        }
        ret = self.call_unit(attrs)
        self.assertEqual(ret._primary_field, 'one')

    @mock.patch('esauth.orm.Field', TestField)
    def test_no_other_fields(self):
        """
            Test cls._fields contains only fields.
        """

        attrs = {
            'one': TestField(primary=True),
            'two': TestField(),
            'three': 10,
            'five': mock.Mock(),
        }
        ret = self.call_unit(attrs)
        self.assertDictEqual(ret._fields, {'one': attrs['one'], 'two': attrs['two']})


class BaseTestCase(base.UnitTestCase):

    def setUp(self):
        self.unit = type('Model', (orm.Base,), {
            'one': orm.Field('raw_one', primary=True),
            'two': orm.Field('raw_two'),
            'base_dn': 'dc=test',
        })

    @mock.patch('ldapom.LDAPEntry', spec=ldapom.LDAPEntry)
    def test__init__unknown_args(self, LDAPEntry):
        with self.assertRaises(TypeError) as ctx:
            self.unit(one=1, two=2, three=3)
        self.assertEqual(ctx.exception.message, 'Invalid kwargs passed: three')

    @mock.patch('ldapom.LDAPEntry', spec=ldapom.LDAPEntry)
    def test__init__no_args(self, LDAPEntry):
        self.unit()

    @mock.patch('ldapom.LDAPEntry', spec=ldapom.LDAPEntry)
    def test__init__ok(self, LDAPEntry):
        obj = self.unit(one=1, two=2)
        self.assertEqual(obj.one, 1)
        self.assertEqual(obj.two, 2)

    @mock.patch('esauth.orm.Base.from_entry')
    def test_all(self, from_entry):
        self.unit.base_dn = 'dc=test'
        self.unit.all_search_filter = 'class=x'
        self.unit._connection = mock.Mock(spec=ldapom.LDAPConnection)

        e1 = mock.Mock(spec=ldapom.LDAPEntry)
        e2 = mock.Mock(spec=ldapom.LDAPEntry)
        self.unit._connection.search.return_value = [e1, e2]

        ret = self.unit.all()
        self.assertIsInstance(ret, types.GeneratorType)
        ret = list(ret)

        self.unit._connection.search.assert_called_with(search_filter='class=x', base='dc=test')
        self.assertEqual(len(ret), 2)

    @mock.patch('esauth.orm.Base.from_entry')
    def test_get_entry_exists(self, from_entry):
        self.unit.id_attribute = 'pk'
        self.unit.base_dn = 'dc=test'
        self.unit._connection = mock.Mock(spec=ldapom.LDAPConnection)

        expected_entry = mock.Mock()
        expected_entry.exists.return_value = True
        self.unit._connection.get_entry.return_value = expected_entry

        ret = self.unit.get('yyy')

        self.unit._connection.get_entry.assert_called_with('raw_one=yyy,dc=test')
        expected_entry.exists.assert_called_with()
        from_entry.assert_called_with(expected_entry)
        self.assertEqual(ret, from_entry(expected_entry))

    def test_get_entry_does_not_exist(self):
        self.unit.id_attribute = 'pk'
        self.unit.base_dn = 'dc=test'
        self.unit._connection = mock.Mock(spec=ldapom.LDAPConnection)

        expected_entry = mock.Mock()
        expected_entry.exists.return_value = False
        self.unit._connection.get_entry.return_value = expected_entry

        ret = self.unit.get('yyy')
        self.assertIsNone(ret)


    # def setUp(self):
    #     self.unit = type('Base', (orm.Base,), {})


    # def test_save(self):
    #     self.unit.attribute_map = {
    #         'oattr': 'ldapattr'
    #     }
    #     entry = mock.Mock()
    #     obj = self.unit(entry)
    #     obj.oattr = 333
    #     obj.save()
    #     self.assertEqual(entry.ldapattr, 333)
    #     entry.save.assert_called_with()

    # def test_no_save_if_no_changes(self):
    #     self.unit.attribute_map = {
    #         'oattr': 'ldapattr'
    #     }
    #     obj = self.unit()
    #     obj.save()

    # def test_update(self):
    #     self.unit.attribute_map = {
    #         'oa1': 'ldap1',
    #         'oa2': 'ldap2',
    #         'oa': 'oa',
    #     }
    #     obj = self.unit()
    #     obj.update({
    #         'oa': 'THREE',
    #         'oa1': 'ONE',
    #         'oa2': 'TWO',
    #     })
    #     self.assertEqual(obj.oa, 'THREE')
    #     self.assertEqual(obj.oa1, 'ONE')
    #     self.assertEqual(obj.oa2, 'TWO')


# class FieldTestCase(base.UnitTestCase):

#     def get_unit(self, obj_name, **field_kw):
#         cls = type('TestClass', (object, ), {
#             obj_name: orm.Field(**field_kw),
#         })
#         return cls()

#     def test__set__(self):
#         obj = self.get_unit('attr', name='raw')
#         obj.attr = 10
#         self.assertEqual(self.entry.raw, 10)

#     def test__get__(self):
#         obj = self.get_unit('attr', name='raw')
#         self.entry.raw = 30
#         self.assertEqual(obj.attr, 30)

#     def test_default_value(self):
#         obj = self.get_unit('attr', name='raw', default=100)
#         self.assertEqual(obj.attr, 100)

#     def test_set_primary_if_none(self):
#         obj = self.get_unit('attr', name='raw', primary=True)
#         obj.attr = 200

#     def test_set_primary_if_already_set(self):
#         obj = self.get_unit('attr', name='raw', primary=True)
#         self.entry.raw = 300
#         with self.assertRaises(ValueError):
#             obj.attr = 200
