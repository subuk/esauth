
import os
import time
import shutil
import logging
import subprocess as sp

CONFIG_DIR_PATH = os.path.join(os.path.dirname(__file__), 'test_server_conf/')
SLAPD_ERR_LOG = '/tmp/esauth-test-slapd.log'
logger = logging.getLogger(__name__)

LDAP_INIT_DATA = """
dn: dc=test,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
dc: test
o: Test

dn: cn=admin,dc=test,dc=com
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
description: LDAP administrator
userPassword:: e1NTSEF9SU1nWldWb1REZnV0RS9uZi9wWnh2K1dvUVlRS256V08=
"""


class TestServerError(Exception):
    pass


class TestLDAPServer(object):

    def start(self):
        if not os.path.isdir("/tmp/esauth-test-slapd-data"):
            os.makedirs('/tmp/esauth-test-slapd-data')

        cmd = ['slapd', '-h', 'ldap://localhost:3389', '-f', 'slapd.conf', '-d3']
        self.proc = sp.Popen(cmd, cwd=CONFIG_DIR_PATH, stdout=open(SLAPD_ERR_LOG, 'w'), stderr=sp.STDOUT)
        time.sleep(0.5)
        if self.proc.poll() is not None:
            raise TestServerError("Cannot start test LDAP server")
        logger.info('Test LDAP server started')

    def stop(self):
        self.proc.terminate()
        self.proc.wait()
        logger.info('Test LDAP server stopped')
        if os.path.isdir('/tmp/esauth-test-slapd-data'):
            shutil.rmtree('/tmp/esauth-test-slapd-data')

    def add(self, data):
        cmd = ['ldapadd', '-w', 'admin', '-D', "cn=admin,dc=test,dc=com", '-H', 'ldap://localhost:3389']
        proc = sp.Popen(cmd, stdout=open('/dev/null'), stdin=sp.PIPE)
        proc.communicate(data)
        if proc.wait() != 0:
            self.stop()
            raise Exception("Bad return value")

    def delete(self, query):
        cmd = ['ldapdelete', '-r', '-H', 'ldap://localhost:3389', '-D', 'cn=admin,dc=test,dc=com', '-w', 'admin', query]
        proc = sp.Popen(cmd, stdout=open('/dev/null'), stdin=sp.PIPE)
        if proc.wait() != 0:
            self.stop()
            raise Exception("Bad return value")

    def load_default_data(self):
        self.add(LDAP_INIT_DATA)


server = TestLDAPServer()


def setUpModule():
    server.start()
    server.load_default_data()


def tearDownModule():
    server.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server.start()
    server.stop()
