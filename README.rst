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

    virtualenv ~/esauth
    . ~/esauth/bin/activate
    python setup.py develop
    pip install esauth[dev]
    python setup.py test
    pserve development.ini

QA
--

Question:
    Tests fails with error 'Cannot start test LDAP server'

Answer:
    ESAuth try to run slapd instance with config from tests/functional/test_server/slapd.conf.
    Check that nothing does not block access to this file (selinux or apparmor, usually)
    Also, check test server log at /tmp/esauth-test-slapd.log.
