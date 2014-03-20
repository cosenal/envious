from copy import copy
import os
import unittest

__author__ = 'Matteo Danieli'

ENV_FILE = """
ENVIRONMENT=development
MONGODB_URL=http://localhost:27017/mydb
REDIS_URL=http://localhost:6379/0
"""

GARBAGE = """
bfsbm,sDbjlkckDSF
sFDklSDjkcdcddslad
SDHhjkDSjkCdlsads
"""


class EnviousTest(unittest.TestCase):

    def setUp(self):
        self.env = copy(os.environ)
        super(EnviousTest, self).setUp()

    def tearDown(self):
        try:
            os.remove('.env')
        except OSError:
            pass
        os.environ.clear()
        for k in self.env:
            os.environ[k] = self.env[k]
        super(EnviousTest, self).tearDown()

    def _write_to_env_file(self, content):
        with open('.env', 'w') as f:
            f.write(content)

    def _set_variable(self, key, value):
        os.environ[key] = value

    def _assert_variable(self, key, value):
        assert os.environ[key] == value

    def _execute_script(self):
        import sample_script
        sample_script = reload(sample_script)
        return sample_script.return_environment_variables()

    def test_envFileNotFound_functionExecutes(self):
        self._execute_script()

    def test_envFileContainsGarbage_functionExecutes(self):
        self._write_to_env_file(GARBAGE)
        self._execute_script()

    def test_envVariablesAlreadyDefined_envVariablesNotOverridden(self):
        self._set_variable('ENVIRONMENT', 'production')
        self._write_to_env_file(ENV_FILE)
        self._execute_script()
        self._assert_variable('ENVIRONMENT', 'production')

    def test_envFileContainsEnvVariables_envVariablesSet(self):
        self._write_to_env_file(ENV_FILE)
        self._execute_script()
        self._assert_variable('ENVIRONMENT', 'development')
        self._assert_variable('MONGODB_URL', 'http://localhost:27017/mydb')
        self._assert_variable('REDIS_URL', 'http://localhost:6379/0')

    def test_envFileContainsEnvVariablesAndGarbage_envVariablesSet(self):
        self._write_to_env_file(ENV_FILE + GARBAGE)
        self._execute_script()
        self._assert_variable('ENVIRONMENT', 'development')
        self._assert_variable('MONGODB_URL', 'http://localhost:27017/mydb')
        self._assert_variable('REDIS_URL', 'http://localhost:6379/0')
