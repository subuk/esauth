import mock
import esauth.forms as forms
import tests.unit.base as base


class RequiredTogetherTestCase(base.UnitTestCase):

    def setUp(self):
        self.unit = forms.RequiredTogether('test')

    def test_call_ok(self):
        form = mock.Mock()
        main_field = mock.Mock()
        main_field.raw_data = ["Text"]
        main_field.errors = []

        t_field1 = mock.Mock()
        t_field1.validators = [self.unit]
        t_field1.raw_data = ["One"]

        t_field2 = mock.Mock()
        t_field2.raw_data = ["One"]
        t_field2.validators = [self.unit]

        t_field3 = mock.Mock()
        t_field3.validators = [self.unit]
        t_field3.raw_data = ["One"]

        form._fields.values.return_value = [t_field1, t_field2, t_field3]

        self.unit(form, main_field)

    def test_call_blank_field(self):
        form = mock.Mock()
        main_field = mock.Mock()
        main_field.raw_data = [""]
        main_field.errors = []

        t_field1 = mock.Mock()
        t_field1.validators = [self.unit]
        t_field1.raw_data = ["One"]

        t_field2 = mock.Mock()
        t_field2.raw_data = ["One"]
        t_field2.validators = [self.unit]

        t_field3 = mock.Mock()
        t_field3.validators = [self.unit]
        t_field3.raw_data = ["One"]

        form._fields.values.return_value = [t_field1, t_field2, t_field3]

        ret = self.unit(form, main_field)
        self.assertIsNone(ret)

    def test_call_already_with_errors(self):
        form = mock.Mock()
        main_field = mock.Mock()
        main_field.raw_data = [""]
        main_field.errors = ["oneoneone"]

        t_field1 = mock.Mock()
        t_field1.validators = [self.unit]
        t_field1.raw_data = ["One"]

        t_field2 = mock.Mock()
        t_field2.raw_data = ["One"]
        t_field2.validators = [self.unit]

        t_field3 = mock.Mock()
        t_field3.validators = [self.unit]
        t_field3.raw_data = ["One"]

        form._fields.values.return_value = [t_field1, t_field2, t_field3]

        with self.assertRaises(forms.ValidationError):
            self.unit(form, main_field)

    def test_call_all_fields_blank(self):
        form = mock.Mock()
        main_field = mock.Mock()
        main_field.raw_data = [""]
        main_field.errors = ["oneoneone"]

        t_field1 = mock.Mock()
        t_field1.validators = [self.unit]
        t_field1.raw_data = [""]

        t_field2 = mock.Mock()
        t_field2.raw_data = [""]
        t_field2.validators = [self.unit]

        t_field3 = mock.Mock()
        t_field3.validators = [self.unit]
        t_field3.raw_data = [""]

        form._fields.values.return_value = [t_field1, t_field2, t_field3]

        with self.assertRaises(forms.validators.StopValidation):
            self.unit(form, main_field)
        self.assertEqual(main_field.errors, [])
