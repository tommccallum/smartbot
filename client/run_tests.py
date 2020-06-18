#!/usr/bin/python3
import unittest
import tests.all_tests
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"src"))

testSuite = tests.all_tests.create_test_suite()
text_runner = unittest.TextTestRunner().run(testSuite)
