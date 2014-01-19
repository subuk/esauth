from setuptools import setup, find_packages

requires = [
    'wtforms',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_webassets',
    'pyramid_beaker',
    'waitress',
    'ldapom',
]

dev_requires = [
    'nose',
    'mock',
    'coverage',
    'pyramid_debugtoolbar',
]

setup(
    name='esauth',
    version='0.1',
    author='Matvey Kruglov',
    author_email='kubus@openpz.org',
    url='http://bitbucket.org/subuk/esauth',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    test_suite="tests",
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'paste.app_factory': [
            'main = esauth.main:paste_wsgi_app',
        ],
    },
)
