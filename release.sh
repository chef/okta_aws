#!/bin/bash
VERSION="$1"

if [[ -z $VERSION ]]; then
    echo "Usage: $0 VERSION"
    echo "Current version: $(grep ^__VERSION__ okta_aws | awk '{print $NF}')"
    exit 1
fi

echo "=> Bumping version in okta_aws to $VERSION"
sed -i "" "s/^__VERSION__ = .*$/__VERSION__ = '$VERSION'/" okta_aws

echo "=> Committing to git"
git add okta_aws
git commit -m "Release v$VERSION"

echo "=> Tagging release"
git tag "v$VERSION"

echo "=> Building source distribution"
rm -rf dist/
python ./setup.py sdist

echo "=> Changes about to be pushed"
git --no-pager show HEAD

echo "About to push changes to git. Press Enter to continue, or ^C to quit"
read -r

echo "=> Pushing to git"
git push --tags origin master

echo "About to upload release to pypi. Press Enter to continue, or ^C to quit"
read -r

echo "=> Uploading release to pypi"
twine upload dist/*

echo "=> Done"

echo "Don't forget to update the homebrew formula as well by running the"
echo "release.sh script in the homebrew-okta_aws repo."
