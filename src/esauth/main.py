
import ldapom
from pyramid.config import Configurator
from pyramid.settings import asbool
from pyramid.paster import bootstrap, setup_logging
import esauth.resources


def configure_ldap_connection(config):
    settings = config.get_settings()
    config.registry['lc'] = ldapom.LDAPConnection(
        uri=settings.get('ldap.uri'),
        base=settings.get('ldap.login'),
        bind_dn=settings.get('ldap.bind_dn'),
        bind_password=settings.get('ldap.bind_password')
    )


def configure_common_debug_options(config):
    settings = config.get_settings()
    settings['reload_templates'] = 'true'
    settings['debug_notfound'] = 'true'
    config.include('pyramid_debugtoolbar')


def configure_views(config):
    config.scan('esauth.views')


def make_app(settings):
    config = Configurator(registry=esauth.registry)
    config.setup_registry(settings=settings)
    if asbool(settings['debug']):
        configure_common_debug_options(config)
    configure_ldap_connection(config)
    configure_views(config)
    config.set_root_factory(esauth.resources.Root)
    return config.make_wsgi_app()


def paste_wsgi_app(global_config, **settings):
    return make_app(settings)


def scripting_boostrap(config_uri):
    setup_logging(config_uri)
    return bootstrap(config_uri)
