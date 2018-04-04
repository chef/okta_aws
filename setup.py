from setuptools import setup

setup(
    name='okta_aws',
    version='0.2.0',
    description='Use the AWS API via an account using Okta',
    author='Mark Harrison',
    author_email='mharrison@chef.io',
    license='Apache-2.0',
    scripts=['okta_aws'],
    url='https://github.com/chef/okta_aws',
    python_requires='>=3',
    install_requires=['requests>=2.18.4', 'toml>=0.9.4']
)
