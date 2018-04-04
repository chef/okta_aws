import os
import re
from setuptools import setup


def find_version():
    with open(os.path.join(os.path.dirname(__file__), 'okta_aws')) as fh:
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
    scripts=['okta_aws'],
    url='https://github.com/chef/okta_aws',
    python_requires='>=3',
    install_requires=['requests>=2.18.4', 'toml>=0.9.4']
)
