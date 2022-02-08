"""Tests for IP determination"""

import warnings

import ddt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

import openedx.core.djangoapps.util.ip as ip


@ddt.ddt
class TestClientIP(TestCase):
    """Tests for get_client_ip"""

    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()

    # Note that {'REMOTE_ADDR': '127.0.0.2'} is provided by default in the test
    @ddt.unpack
    @ddt.data(
        # By default, do something useful
        (None, None, {}, '127.0.0.2', True),
        # Show that default is actually the XFF, though
        (None, None, {'HTTP_X_FORWARDED_FOR': '4.3.2.1, 5.6.7.8'}, '5.6.7.8', False),
        # Explicitly using REMOTE_ADDR
        ('REMOTE_ADDR', -1, {}, '127.0.0.2', False),
        ('REMOTE_ADDR', 0, {}, '127.0.0.2', False),
        # Fall back to REMOTE_ADDR when field or index is invalid
        ('HTTP_X_FORWARDED_FOR', -1, {}, '127.0.0.2', True),
        ('HTTP_X_FORWARDED_FOR', 33, {'HTTP_X_FORWARDED_FOR': '4.3.2.1'}, '127.0.0.2', True),
        # Can use arbitrary header or other field
        ('BLAH', -1, {'HTTP_X_FORWARDED_FOR': '4.3.2.1', 'BLAH': '5.6.7.8'}, '5.6.7.8', False),
    )
    def test_request_with_latin1_characters(
            self, cnf_field, cnf_index, request_meta, expected_answer, expected_warning
    ):
        # Settings overrides, but allow specifying None to use default value
        overrides = {
            'CLIENT_IP_REQUEST_META_FIELD': cnf_field,
            'CLIENT_IP_REQUEST_META_INDEX': cnf_index,
        }
        overrides = {k: v for k, v in overrides.items() if v is not None}

        request = self.request_factory.get('/somewhere')
        request.META.update({'REMOTE_ADDR': '127.0.0.2'})
        request.META.update(request_meta)

        with override_settings(**overrides):
            # Check if a warning was filed, indicating a fallback
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')

                actual_answer = ip.get_client_ip(request)

        assert actual_answer == expected_answer
        assert len(w) == {True: 1, False: 0}[expected_warning]
