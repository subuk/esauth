import ldapom
from pyramid.config import Configurator
from pyramid.settings import asbool
from pyramid.paster import bootstrap, setup_logging
import esauth.resources
import esauth.assets


def configure_webassets_jinja2_integration(config):
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    assets_env = config.get_webassets_env()
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.assets_environment = assets_env


def configure_webassets(config):
    settings = config.get_settings()
    settings.setdefault('webassets.base_dir', 'src/esauth/static')
    settings.setdefault('webassets.base_url', '/static')
    config.include('pyramid_webassets')
    config.add_webasset('all_js', esauth.assets.all_js)
    config.add_webasset('all_css', esauth.assets.all_css)


def configure_template_engine(config):
    from pyramid.traversal import model_path

    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("esauth:templates")
    env = config.get_jinja2_environment()
    env.globals['model_url'] = model_path


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
    configure_template_engine(config)
    configure_webassets(config)
    configure_webassets_jinja2_integration(config)
    config.set_root_factory(esauth.resources.Root)
    return config.make_wsgi_app()


def paste_wsgi_app(global_config, **settings):
    return make_app(settings)


def scripting_boostrap(config_uri):
    setup_logging(config_uri)
    return bootstrap(config_uri)
