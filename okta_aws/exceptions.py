class Error(Exception):
    "Base exception class for okta_aws"
    pass


class LoginError(Error):
    "Error logging in to okta"
    def __init__(self, message):
        self.message = message


class AssumeRoleError(Error):
    "Error running aws assume-role-with-saml"
    def __init__(self, message):
        self.message = message
