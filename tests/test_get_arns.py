#!/usr/bin/env python3
# pylint: disable=invalid-name,missing-docstring


def test_get_arns(oa, shared_datadir):
    with open("%s/saml_assertion.txt" % shared_datadir) as fh:
        assertion = fh.read()
    arns = oa.get_arns(assertion)

    # Principal
    assert arns[0] == 'arn:aws:iam::012345678901:saml-provider/OKTA'
    # Role
    assert arns[1] == 'arn:aws:iam::012345678901:role/Okta_AdministratorAccess'
