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

## Setup

Make a file in your home directory called `.okta_aws.toml`:

    [general]
    username="yourusername"
    okta_server="yourcompany.okta.com"
    apptype="amazon_aws"

    [profilename]
    appid="..."
    prinicpal_arn="arn:aws:iam::1234567890:saml-provider/OKTA"
    role_arn="aws:aws:iam::1234567890:role/Okta_User"

The values are as follows:

* `username`: your okta username
* `okta_server`: The domain name you use to log into okta. It's normally
  `yourcompanyname.okta.com`.
* `apptype`: This should normally be set to `amazon_aws`

Then there is a section for each AWS profile you wish to use. This lets you
log into multiple AWS accounts from the same okta account. The name of this
section corresponds to the name of the profile that you will use when
accessing the AWS API (e.g. what you put after `--profile` when using the AWS
cli tools).

Within each profile there are several settings:

* `appid` - this is the app ID used by okta. Finding this out isn't
  straightforward, but you can get it by going into the application settings
  in the admin interface in okta, and looking for the 'Identity Provider
  metadata' link in the 'Sign On' section. The URL will look something like:
  `https://chef.okta.com/app/SOMERANDOMID/sso/saml/metadata`. The random ID in
  this URL is your appid.
* `principal_arn`: This is the ARN of the saml integration you set up in AWS.
  It can also be found from the 'Sign on' page of the application settings
  in okta.  Look for the 'Identify provider ARN' setting.
* `role_arn`: This is the ARN of the role you are assigned when you log into
  AWS via okta. It can be found in the IAM console when you log in, by going
  to the roles section and finding the role that you are logged in as (shown
  at the top right of the screen on the AWS console).

Note: If you have been instructed to download this tool, then these settings
may have been provided to you already.
