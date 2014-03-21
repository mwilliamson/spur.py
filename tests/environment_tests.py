__author__ = 'nmckinney'

import unittest
from spur.local import LocalShell

class EnvironmentalVariableTests(unittest.TestCase):

    def test_GetEnvironmentalVariablesLocal(self):
        shell = LocalShell()
        home = shell.env['HOME']
        self.assertIsNotNone(home)