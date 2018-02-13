# Okta AWS tool

This tool is for accessing the AWS API for an AWS account you normally log
into via okta. Normally, when you log in to an account via okta, you are
assigned an IAM role, and don't have an actual user within AWS. This means you
don't have any API keys you can use to access the AWS API via the command
line.

This tool will prompt you for your Okta credentials, and generate temporary
API keys you can use to access the AWS API with. It will also continue to
renew those credentials before they expire (the temporary credentials normally
only last for an hour) while it is running.

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
