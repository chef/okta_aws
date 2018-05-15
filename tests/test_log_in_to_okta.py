# pylint: disable=invalid-name,missing-docstring
import json
import pytest

from okta_aws import exceptions

from unittest.mock import patch


def test_log_in_to_okta_success(oa, shared_datadir):
    oa.config = oa.load_config("%s/okta_aws.toml" % shared_datadir)
    with patch("requests.post") as patched_post:
        patched_post.return_value.status_code = 200
        with open("%s/okta_auth_success.json" % shared_datadir) as fh:
            text = fh.read()
        patched_post.return_value.text = text
        patched_post.return_value.json.return_value = json.loads(text)

        token = oa.log_in_to_okta('hunter2')

        assert token == "1234567890ABCDEFGHIJKLMNO"


def test_log_in_to_okta_incorrect_password(oa, shared_datadir):
    oa.config = oa.load_config("%s/okta_aws.toml" % shared_datadir)
    with patch("requests.post") as patched_post:
        patched_post.return_value.status_code = 401

        with pytest.raises(exceptions.LoginError, match="Incorrect password"):
            oa.log_in_to_okta('hunter2')


def test_log_in_to_okta_password_expired(oa, shared_datadir):
    oa.config = oa.load_config("%s/okta_aws.toml" % shared_datadir)
    with patch("requests.post") as patched_post:
        patched_post.return_value.status_code = 200
        with open("%s/okta_auth_password_expired.json" % shared_datadir) as fh:
            text = fh.read()
        patched_post.return_value.text = text
        patched_post.return_value.json.return_value = json.loads(text)

        with pytest.raises(exceptions.LoginError, match="Password Expired"):
            oa.log_in_to_okta('hunter2')
