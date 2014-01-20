
import unittest
import webtest
import pyramid.events as events
import pyramid.scripting as scripting
import pyramid.testing as testing
from pyramid.config import Configurator
import esauth
import esauth.main
import esauth.models
from tests.functional import server


class PyramidTestApp(webtest.TestApp):

    """

        Extends webtest.TestApp to allow checking additional variables.

        app_request:
            Request, cathed from pyramid's NewRequest event.

        app_response:
            Application response object.

        view:
            View function, used for this request.

        view_context:
            Request context, catched from pyramid's ContextFound event.

        view_return:
            Values, returned from view function.

        renderer_name:
            Renderer name used with this view

        Usage example:

        ::

            class BaseFunctionalTestCase(unittest.TestCase):

                def __init__(self):
                    self.app = PyramidTestApp(myapp.main({}, **config))

                def test_root_view(self):
                    response = self.app.get('/', status=200)
                    self.assertIsInstance(self.app.view_context, myapp.resources.MyRootResource)
                    self.assertIn('langs', self.app.view_return)
    """

    session = {}

    def __init__(self, *args, **kwargs):
        super(PyramidTestApp, self).__init__(*args, **kwargs)
        config = Configurator(registry=esauth.registry)
        config.add_subscriber(self._before_app_render, events.BeforeRender)
        config.add_subscriber(self._on_new_request, events.NewRequest)
        config.add_subscriber(self._on_new_response, events.NewResponse)
        config.add_subscriber(self._on_context_found, events.ContextFound)
        config.set_session_factory(self.session_factory)
        config.commit()

    def login(self, userid):
        """
            Login as user userid.
            Assumes SessionAuthenticationPolicy in use.
        """
        self.session['auth.userid'] = userid

    def override_settings(self, **settings):
        config = Configurator(registry=self.app.registry)
        config.add_settings(**settings)
        config.commit()

    def get_root(self):
        """
            Get application root resource factory
        """
        return scripting.get_root(self.app)[0]

    def session_factory(self, request):
        """
            Application session factory. Uses pyramid.DummySession.
        """
        return testing.DummySession(self.session)

    def _on_new_request(self, event):
        test_vars = event.request.environ['paste.testing_variables']
        test_vars.update({
            'app_request': event.request,
        })

    def _on_context_found(self, event):
        test_vars = event.request.environ['paste.testing_variables']
        test_vars.update({
            'view_context': event.request.context,
        })

    def _on_new_response(self, event):
        test_vars = event.request.environ['paste.testing_variables']
        test_vars.update({
            'app_response': event.response,
            'app_exception': getattr(event.request, "exception", None)
        })

    def _before_app_render(self, env):
        test_vars = env['req'].environ['paste.testing_variables']
        test_vars.update({
            'view': env['view'],
            'view_return': env.rendering_val,
            'renderer_name': env['renderer_name'],
        })


LDAP_ROOTS = """
dn: ou=groups,dc=test,dc=com
objectClass: organizationalUnit
objectClass: top
ou: groups

dn: ou=users,dc=test,dc=com
objectClass: organizationalUnit
objectClass: top
ou: users
"""


class FunctionalBaseTestCase(unittest.TestCase):

    def setUp(self):
        server.add(LDAP_ROOTS)
        self.app = PyramidTestApp(esauth.main.make_app({
            'debug': 'true',
            'ldap.users_base': 'ou=users,dc=test,dc=com',
            'ldap.groups_base': 'ou=groups,dc=test,dc=com',
            'ldap.bind_dn': 'cn=admin,dc=test,dc=com',
            'ldap.bind_password': 'admin',
            'ldap.uri': 'ldap://localhost:3389',
        }))

    def tearDown(self):
        server.delete("ou=groups,dc=test,dc=com")
        server.delete("ou=users,dc=test,dc=com")
