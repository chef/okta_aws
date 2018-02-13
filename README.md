# Okta AWS tool

This tool is for accessing the AWS API for an AWS account you normally log
into via okta. Normally, when you log in to an account via okta, you are
assigned an IAM role, and don't have an actual user within AWS. This means you
don't have any API keys you can use to access the AWS API via the command
line.

This tool will prompt you for your Okta credentials, and generate temporary
API keys you can use to access the AWS API with.

## Installation

Clone this repository then run:

    python setup.py install

If you have homebrew, you can use it to install okta_aws:

    brew install https://raw.githubusercontent.com/chef/okta_aws/master/Formula/okta_aws.rb

## Setup

Make a file in your home directory called `.okta_aws.toml`:

    [general]
    username="yourusername"

    [profilename]
    embed_url="https://yourcompanyname.okta.com/home/amazon_aws/..."
    #role_arn="aws:aws:iam::1234567890:role/Okta_User"
    #role_arn="Okta_User"

The values are as follows:

* `username`: your okta username

Then there is a section for each AWS profile you wish to use. This lets you
log into multiple AWS accounts from the same okta account. The name of this
section corresponds to the name of the profile that you will use when
accessing the AWS API (e.g. what you put after `--profile` when using the AWS
cli tools).

Within each profile there are several settings:

* `embed_url` - this is App Embed Link you can find in the "General" tab when
  looking at the application inside the okta admin console.
* `role_arn`: This setting contains the role to assume when you log into
  AWS via okta. You only need to provide this if you are assigned more than
  one role in okta, and you don't want to be prompted for which role to assume
  each time. You can provide either a full ARN here, or just the name of the
  role itself.

Note: If you have been instructed to download this tool, then these settings
may have been provided to you already.

## Usage

Run `okta_aws PROFILENAME`, or run `okta_aws` without any arguments and
okta_aws will you the `AWS_PROFILE` environment variable if you have it set.

The first time you run `okta_aws`, you will be prompted for your okta username
and password. On subsequent runs, if you are still logged into okta and your
session hasn't expired, then you won't have to log in again.

Once you have entered your okta username and password, a temporary token will
be obtained for you and stored in your AWS credentials file. You can then use
the aws api as normal, passing in the profile name you gave to okta_aws.

If you have been assigned multiple possible roles when the aws account was set
up for you in okta, then you will be prompted which one of them you want to
use (e.g. Okta_PowerUser or Okta_AdminAccess). Select which one you want from
the menu if prompted. You can also configure a default role to assume in
`~/.okta_aws.toml`.

The AWS token you receive will only last for an hour. To get a new token,
re-run okta_aws.

### Automatically refreshing the token

You can run okta_aws a second time to retrieve a new token before the old one
expires. If you wish, you can run the following to automatically refresh the
token once every 55 minutes (allowing some grace period before the token
expires):

    while true; do okta_aws PROFILENAME; sleep 3300; done

okta_aws will run without prompting for anything one you have logged in and,
if necessary, configured a default profile in `~/.okta_aws.toml`.
