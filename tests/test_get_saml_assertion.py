#!/usr/bin/env python3
# pylint: disable=invalid-name,missing-docstring
from unittest.mock import patch


def test_get_saml_assertion(oa, shared_datadir):
    with patch("requests.post") as patched_post:
        patched_post.return_value.status_code = 200
        with open("%s/saml_assertion_page.html" % shared_datadir) as fh:
            patched_post.return_value.text = fh.read()

        sa = oa.get_saml_assertion("session_id", "app_url")

        assert sa == "VGVzdGluZyAxLi4uMi4uLjMuLi4K"
