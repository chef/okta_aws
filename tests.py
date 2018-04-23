#!/usr/bin/env python3
# pylint: disable=invalid-name,missing-docstring
import unittest
from unittest.mock import Mock, patch

from okta_aws import okta_aws


class TestFriendlyInterval(unittest.TestCase):
    """Test the friendly_interval method"""

    def setUp(self):
        args = []
        self.oa = okta_aws.OktaAWS(args)

    def test_hour(self):
        self.assertEqual(self.oa.friendly_interval(3600), '1 hour')
        self.assertEqual(self.oa.friendly_interval(7200), '2 hours')

    def test_minute(self):
        self.assertEqual(self.oa.friendly_interval(600), '10 minutes')
        self.assertEqual(self.oa.friendly_interval(60), '1 minute')

    def test_fractions(self):
        self.assertEqual(self.oa.friendly_interval(5400), '1.5 hours')
        self.assertEqual(self.oa.friendly_interval(30), '0.5 minutes')


class TestGetSamlAssertion(unittest.TestCase):
    """Test the get_saml_assertion method"""

    def setUp(self):
        args = []
        self.oa = okta_aws.OktaAWS(args)

    def test_get_saml_assertion(self):
        with patch("requests.post") as patched_post:
            patched_post.return_value.status_code = 200
            with open("test_fixtures/saml_assertion_page.html") as fh:
                patched_post.return_value.text = fh.read()

            sa = self.oa.get_saml_assertion("session_id", "app_url")

            self.assertEqual(sa, "VGVzdGluZyAxLi4uMi4uLjMuLi4K")


if __name__ == '__main__':
    unittest.main()
