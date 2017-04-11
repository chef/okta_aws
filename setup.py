from setuptools import setup

setup(
    name='okta_aws',
    version='0.1.0',
    description='Use the AWS API via an account using Okta',
    author='Mark Harrison',
    scripts=['okta_aws'],
    url='https://github.com/chef/okta_aws',
    install_requires=['oktaauth>=0.2', 'toml>=0.9.2']
)
