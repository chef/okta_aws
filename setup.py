import os
import re
from setuptools import setup


def find_version():
    with open(os.path.join(os.path.dirname(__file__),
                           'okta_aws/okta_aws.py')) as fh:
        content = fh.read()
        m = re.search(r"^__VERSION__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if m:
            return m.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name='okta_aws',
    version=find_version(),
    description='Use the AWS API via an account using Okta',
    author='Mark Harrison',
    author_email='mharrison@chef.io',
    license='Apache-2.0',
    packages=['okta_aws'],
    entry_points={"console_scripts": ['okta_aws=okta_aws.__main__:main']},
    url='https://github.com/chef/okta_aws',
    python_requires='>=3',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest_datadir'],
    install_requires=['requests>=2.21.0', 'toml>=0.10.0', 'boto3>=1.9.93']
)
