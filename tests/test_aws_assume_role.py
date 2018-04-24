# pylint: disable=invalid-name,missing-docstring
from unittest.mock import patch


def test_aws_assume_role(oa, shared_datadir):
    with patch("subprocess.check_output") as patched_check_output:
        # Open in binary mode here to match faked check_output result as being
        # in bytes as opposed to a string
        with open("%s/aws_sts_output.txt" % shared_datadir, 'rb') as fh:
            patched_check_output.return_value = fh.read()

        with open("%s/saml_assertion.txt" % shared_datadir) as fh:
            assertion = fh.read()

        credentials = oa.aws_assume_role(
            'arn:aws:iam::012345678901:saml-provider/OKTA',
            'arn:aws:iam::012345678901:role/Okta_AdministratorAccess',
            assertion,
            3600)

        assert credentials['AccessKeyId'] == 'ASIAABCDEFG123456789'
        assert credentials['SecretAccessKey'] == \
            'hOUlRBNYBVlR05jXRBXbntDc/F56FkPsj+Gd/mzP'
        assert credentials['SessionToken'] == \
            'uMvpvBlJ2kL3JRsJiktoC3FJq3aVCmyKOcX+mtrJCc5UIkFsozZD7aGxISsAE' \
            'LQelXCEMVRhef37BG8dsI8cd2Khz+xIcWdwCxwOfFqQEWDFltsI3Sfbz0cdT9' \
            'mtDG6DvmT3vTFB5DdeuRJzTvZFXCi7msKCGWmOpSpWc9PrZIOVV5ad84mgsa3' \
            'N0ccvCEtJ/7rdzZL/y9cQfZLmb0+VbuVTL76Siyw9zt7sMIjDSOtGBOXf1wcg' \
            'O2m7NU37wRK3Ux4nvttTtrKeZ7f3DuDzsH61OrLcg98sz0XDW3Brl31dhrqdV' \
            'ORIOv9SEpaRewDSX/wl74DVElH9VQ0fOHdsD6MNFnKl+NEAiYd4vZMjk1U8/e' \
            '4GAWZIF/EHaQxgHU3NBsWvRYsTQUPombgR81BXm9Quh9aj'
        assert credentials['Expiration'] == '2018-04-24T00:00:00Z'
