# Making a new release

## Prerequisites

* Create an account on <https://pypi.org/> and make sure you have access to the
  okta_aws package. Ask an existing maintainer for access if you don't have
  it.
* Make sure you have push access to the `chef/okta_aws` and
 `chef/homebrew-okta_aws` repositories.
* Install dependencies: python3, pipenv, twine (`brew install python3 pipenv;
  pip3 install twine`)

## Making the release

* Edit okta_aws and bump the version number at the top (in the `__VERSION__`
  variable)
* Run `pipenv update` to update dependencies in Pipfile.lock
* Commit changes to git
* Tag the commit `git tag v$(./okta_aws --version)`
* Push the changes `git push --tags origin master`
* Remove any existing builds `rm -rf dist`
* Run `python ./setup.py sdist` to build a source package
* Run `twine upload dist/*` to upload the package to pypi.
* Update the homebrew formula:
  * Run `pipenv shell` in the okta_aws directory
  * Run `pip install homebrew-pypi-poet`
  * Run `pip install okta_aws`
  * Run `poet -f okta_aws`
  * Clone <https://github.com/chef/homebrew-okta_aws>
  * Copy the relevant lines from generated formula over the existing one in
    `homebrew-okta_aws/Formula/okta_aws.rb`.
    * Only copy the url, sha256 and resource sections, keep the original
      description, test, homepage and head lines.
  * Commit and push the changes to homebrew-okta-aws
