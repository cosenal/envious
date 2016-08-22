from copy import copy
import os
import unittest
from imp import reload

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
            os.remove('.env2')
        except OSError:
            pass
        os.environ.clear()
        for k in self.env:
            os.environ[k] = self.env[k]
        super(EnviousTest, self).tearDown()

    def _write_to_env_file(self, content, filename='.env'):
        with open(filename, 'w') as f:
            f.write(content)

    def _set_variable(self, key, value):
        os.environ[key] = value

    def _assert_variable(self, key, value):
        assert os.environ[key] == value

    def _execute_script(self):
        from . import sample_script
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

    def test_differentEnvFileSpecified_otherEnvironmentVariablesSet(self):
        self._set_variable('ENV_FILE', '.env2')
        self._write_to_env_file('NEW_VAR=new_value', filename='.env2')
        self._execute_script()
        self._assert_variable('NEW_VAR', 'new_value')

    def test_envFileContainsMultipleEqualSigns_envVariablesSet(self):
        self._write_to_env_file('NEW_VAR=variable=containing=multiple=equal=signs')
        self._execute_script()
        self._assert_variable('NEW_VAR', 'variable=containing=multiple=equal=signs')

    def test_envFileContainsSingleQuoteEnclosedVariables_envVariablesSet(self):
        self._write_to_env_file("NEW_VAR='quote_enclosed_variable'")
        self._execute_script()
        self._assert_variable('NEW_VAR', 'quote_enclosed_variable')

    def test_envFileContainsDoubleQuotesEnclosedVariables_envVariablesSet(self):
        self._write_to_env_file('NEW_VAR="double_quote_enclosed_variable"')
        self._execute_script()
        self._assert_variable('NEW_VAR', 'double_quote_enclosed_variable')

    def test_envFileContainsMultipleLines_newlineCharacterReadCorrectly(self):
        self._write_to_env_file("NEW_LINE_VAR=\"this is line 1\\nand this is line 2\"")
        self._execute_script()
        assert len(os.environ['NEW_LINE_VAR'].splitlines()) == 2

    def test_envFileContainsCommentedLines_linesIgnored(self):
        self._set_variable('NEW_VAR', 'old_value')
        self._write_to_env_file("# NEW_VAR=new_value")
        self._execute_script()
        self._assert_variable('NEW_VAR', 'old_value')
        assert '# NEW_VAR' not in os.environ
