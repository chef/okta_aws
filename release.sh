#!/bin/bash
VERSION="$1"

VERSION_FILE="okta_aws/okta_aws.py"

if [[ -z $VERSION ]]; then
    echo "Usage: $0 VERSION"
    echo "Current version: $(grep ^__VERSION__ $VERSION_FILE | awk '{print $NF}')"
    exit 1
fi

# Make sure required commands are installed first
for i in twine python git; do
    if ! command -v twine >/dev/null; then
        echo "You need to have $i installed. Please install it and try"
        echo "running this again. See RELEASE.md for more information"
        exit 1
    fi
done

echo "=> Bumping version in okta_aws to $VERSION"
sed -i "" "s/^__VERSION__ = .*$/__VERSION__ = '$VERSION'/" "$VERSION_FILE"

echo "=> Committing to git"
git add "$VERSION_FILE"
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
