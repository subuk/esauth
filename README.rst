ESAuth
======

Simple LDAP account management tool.

Installation
------------

::

    virtualenv ~/esauth
    . ~/esauth/bin/activate
    pip install esauth
    esauth-make-config -o esauth.cfg
    pserve esauth.cfg

Use ldap_bind_dn password for login.


Development
-----------

::

    virtualenv ~/envs/esauth
    . ~/envs/esauth/bin/activate
    python setup.py develop
    python setup.py test
    pserve development.ini

QA
--

Question:
    Tests fails with error 'Cannot start test LDAP server'

Answer:
    ESAuth try to run slapd instance with config file tests/functional/test_server/slapd.conf.
    Check that nothing does not block access to this file (selinux or apparmor, usually).
    Also, check test server log: /tmp/esauth-test-slapd.log.


Changelog
---------

v0.2

    * Use jQuery.choosen for all form fields
    * Models layer

v0.1

    * Initial package version.
    * CRUD for users and groups.
