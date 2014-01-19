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
