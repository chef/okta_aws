# Making a new release

## Prerequisites

* Create an account on <https://pypi.org/> and make sure you have access to the
  okta_aws package. Ask an existing maintainer for access if you don't have
  it.
* Make sure you have push access to the `chef/okta_aws` and
 `chef/homebrew-okta_aws` repositories.
* Install dependencies: python3, twine (`brew install python3;
  pip3 install twine`)

## Making the release

Run `./release.sh NEW_VERSION_NUMBER`. This will:

* Edit okta_aws and bump the version number at the top (in the `__VERSION__`
  variable)
* Commit changes to git
* Tag the commit `git tag v$(./okta_aws --version)`
* Push the changes `git push --tags origin master`
* Remove any existing builds `rm -rf dist`
* Run `python ./setup.py sdist` to build a source package
* Run `twine upload dist/*` to upload the package to pypi.

To update the homebrew formula, clone
<https://github.com/chef/homebrew-okta_aws> and run the `release.sh` script in
that repository. This will:

* Install okta_aws and homebrew-pypi-poet to a virtualenv
* Generate a formula with `poet -f okta_aws`
* Patch the generated formula to add local customizations
* Commit and push the changes to homebrew-okta-aws
