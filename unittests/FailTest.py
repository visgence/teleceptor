#!/usr/bin/env python
__author__ = 'Victor Szczepanski'
import unittest

#local
from abstractTest import AbstractTeleceptorTest


class FailTest(AbstractTeleceptorTest):

    def test00_fail(self):
        self.assertTrue(False)

if __name__ == "__main__":

    unittest.main()
