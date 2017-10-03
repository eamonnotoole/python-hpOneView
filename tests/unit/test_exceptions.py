# -*- coding: utf-8 -*-
###
# (C) Copyright (2012-2017) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###
import traceback
import unittest
import logging
import mock
import pickle
import tempfile
import os

from hpOneView.exceptions import handle_exceptions
from hpOneView.exceptions import HPOneViewException
from hpOneView.exceptions import HPOneViewInvalidResource
from hpOneView.exceptions import HPOneViewUnknownType
from hpOneView.exceptions import HPOneViewTaskError
from hpOneView.exceptions import HPOneViewResourceNotFound
from hpOneView.exceptions import HPOneViewValueError


class ExceptionsTest(unittest.TestCase):
    def test_exception_constructor_with_string(self):
        exception = HPOneViewException("A message string")

        self.assertEqual(exception.msg, "A message string")
        self.assertEqual(exception.oneview_response, None)
        self.assertEqual(exception.args[0], "A message string")
        self.assertEqual(len(exception.args), 1)

    def test_exception_constructor_with_valid_dict(self):
        exception = HPOneViewException({'message': "A message string"})

        self.assertEqual(exception.msg, "A message string")
        self.assertEqual(exception.oneview_response, {'message': "A message string"})
        self.assertEqual(exception.args[0], "A message string")
        self.assertEqual(exception.args[1], {'message': 'A message string'})

    def test_exception_constructor_with_invalid_dict(self):
        exception = HPOneViewException({'msg': "A message string"})

        self.assertEqual(exception.msg, None)
        self.assertEqual(exception.oneview_response, {'msg': "A message string"})
        self.assertEqual(exception.args[0], None)
        self.assertEqual(exception.args[1], {'msg': "A message string"})

    def test_exception_constructor_with_invalid_type(self):
        exception = HPOneViewException(['List, item 1', "List, item 2: A message string"])

        self.assertEqual(exception.msg, None)
        self.assertEqual(exception.oneview_response, ['List, item 1', "List, item 2: A message string"])
        self.assertEqual(exception.args[0], None)
        self.assertEqual(exception.args[1], ['List, item 1', "List, item 2: A message string"])

    def test_invalid_resource_exception_inheritance(self):
        exception = HPOneViewInvalidResource({'message': "A message string"})

        self.assertIsInstance(exception, HPOneViewException)
        self.assertEqual(exception.msg, "A message string")
        self.assertEqual(exception.oneview_response, {'message': "A message string"})
        self.assertEqual(exception.args[0], "A message string")
        self.assertEqual(exception.args[1], {'message': 'A message string'})

    def test_unknown_type_exception_inheritance_with_string(self):
        exception = HPOneViewUnknownType("A message string")

        self.assertIsInstance(exception, HPOneViewException)
        self.assertEqual(exception.msg, "A message string")
        self.assertEqual(exception.oneview_response, None)
        self.assertEqual(exception.args[0], "A message string")
        self.assertEqual(len(exception.args), 1)

    def test_exception_constructor_with_unicode(self):
        exception = HPOneViewException(u"A message string")

        self.assertEqual(exception.msg, "A message string")
        self.assertEqual(exception.oneview_response, None)
        self.assertEqual(exception.args[0], "A message string")
        self.assertEqual(len(exception.args), 1)

    def test_task_error_constructor_with_string(self):
        exception = HPOneViewTaskError("A message string", 100)

        self.assertIsInstance(exception, HPOneViewException)
        self.assertEqual(exception.msg, "A message string")
        self.assertEqual(exception.oneview_response, None)
        self.assertEqual(exception.args[0], "A message string")
        self.assertEqual(len(exception.args), 1)
        self.assertEqual(exception.error_code, 100)

    def test_oneview_resource_not_found_inheritance(self):
        exception = HPOneViewResourceNotFound("The resource was not found!")

        self.assertIsInstance(exception, HPOneViewException)
        self.assertEqual(exception.msg, "The resource was not found!")
        self.assertEqual(exception.oneview_response, None)
        self.assertEqual(exception.args[0], "The resource was not found!")

    def test_oneview_value_error_inheritance(self):
        exception = HPOneViewValueError("The given data is empty!")

        self.assertIsInstance(exception, HPOneViewException)
        self.assertEqual(exception.msg, "The given data is empty!")
        self.assertEqual(exception.oneview_response, None)
        self.assertEqual(exception.args[0], "The given data is empty!")

    def test_pickle_HPOneViewException_dict(self):
        message = {"msg": "test message"}
        exception = HPOneViewException(message)
        tempf = tempfile.NamedTemporaryFile(delete=False)
        with tempf as f:
            pickle.dump(exception, f)

        with open(tempf.name, 'rb') as f:
            exception = pickle.load(f)

        os.remove(tempf.name)
        self.assertEqual('Exception', exception.__class__.__name__)

    def test_pickle_HPOneViewException_message(self):
        message = "test message"
        exception = HPOneViewException(message)
        tempf = tempfile.NamedTemporaryFile(delete=False)
        with tempf as f:
            pickle.dump(exception, f)

        with open(tempf.name, 'rb') as f:
            exception = pickle.load(f)

        os.remove(tempf.name)
        self.assertEqual('Exception', exception.__class__.__name__)

    @mock.patch.object(traceback, 'print_exception')
    @mock.patch.object(logging, 'error')
    def test_should_log_message(self, mock_logging_error, mock_traceback):
        message = "test message"
        exception = HPOneViewException(message)
        traceback_ex = None
        handle_exceptions(exception.__class__, exception, traceback_ex, mock_logging_error)

        log_message = "Uncaught Exception: HPOneViewException with message: test message"
        mock_logging_error.error.assert_called_once_with(log_message)

    @mock.patch.object(traceback, 'print_exception')
    @mock.patch.object(logging, 'error')
    def test_should_print_exception(self, mock_logging_error, mock_traceback):
        message = "test message"
        exception = HPOneViewException(message)
        traceback_ex = None
        handle_exceptions(exception.__class__, exception, traceback_ex, mock_logging_error)

        mock_traceback.assert_called_once_with(exception.__class__, exception, traceback_ex)

    @mock.patch.object(traceback, 'print_exception')
    @mock.patch.object(logging, 'error')
    def test_should_log_oneview_reponse(self, mock_logging_error, mock_traceback):
        message = {"msg": "test message"}
        exception = HPOneViewException(message)
        traceback_ex = None
        handle_exceptions(exception.__class__, exception, traceback_ex, mock_logging_error)

        log_message = "Uncaught Exception: HPOneViewException with message: \n{'msg': 'test message'}"
        mock_logging_error.error.assert_called_once_with(log_message)

    @mock.patch.object(traceback, 'print_exception')
    @mock.patch.object(logging, 'error')
    def test_should_log_python_exception(self, mock_logging_error, mock_traceback):
        message = "test message"
        exception = Exception(message)
        traceback_ex = None
        handle_exceptions(exception.__class__, exception, traceback_ex, mock_logging_error)

        log_message = "Uncaught Exception: Exception with message: test message"
        mock_logging_error.error.assert_called_once_with(log_message)
