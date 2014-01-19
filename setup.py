import os
from setuptools import setup, find_packages

read = lambda path: open(path).read()

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
    description='Simple LDAP account management tool',
    long_description=read('README.rst'),
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
        'console_scripts': [
            'esauth-make-config = esauth.scripts:generate_prod_config',
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Development Status :: 3 - Alpha",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
    ],
)
