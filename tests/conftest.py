import pytest

from okta_aws import okta_aws


@pytest.fixture
def oa():
    return okta_aws.OktaAWS([])
