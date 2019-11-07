# Okta AWS tool

[![Build Status](https://travis-ci.org/chef/okta_aws.svg?branch=master)](https://travis-ci.org/chef/okta_aws)

This tool is for accessing the AWS API for AWS accounts you normally log
into via okta. Normally, when you log in to an account via okta, you are
assigned an IAM role, and don't have an actual user within AWS. This means you
don't have any API keys you can use to access the AWS API via the command
line.

This tool will prompt you for your Okta credentials, and generate temporary
API keys you can use to access the AWS API with.

## Installation

Okta_aws requires Python 3 to run.

### macOS

If you have [Homebrew](https://brew.sh), you can use it to install `okta_aws`:

    brew tap chef/okta_aws
    brew install okta_aws

To do the same thing in one step, you can run:

    brew install chef/okta_aws/okta_aws

### Linux (Ubuntu)

Due to a [bug](https://github.com/aws/aws-cli/issues/3820) in the
version of the AWS CLI found in Ubuntu packages, you will need to use
the AWS CLI installed via `pip` instead (`okta_aws` currently
interacts with the AWS API via the CLI).

Once you have installed the newer AWS CLI, you can install `okta_aws`
using `pip`:

    sudo apt-get remove awscli
    sudo apt-get install python3 python3-pip
    sudo python3 -m pip install --upgrade awscli
    sudo python3 -m pip install --upgrade okta_aws


### Pip

Alternatively, you can install via `pip`:

    pip install okta_aws

### Source

To install from source, clone this repository and run:

    python setup.py install

## Setup

Make a file in your home directory called `.okta_aws.toml`:

    [general]
    username="yourusername"
    okta_server="yourcompany.okta.com"

The values are as follows:

* `username`: your okta username.
* `okta_server`: the okta domain your company uses. It is usually something
  like `yourcompanyname.okta.com`.

There are some optional settings too:

* `short_profile_names` - okta_aws will fetch a list of AWS accounts you have
  been assigned directly from okta, and will use the name in okta as the
  profile name referred to by the AWS tools. However, the name of the
  application in okta is often verbose. With this option turned on (it
  defaults to true), the profile names will be shortened into something easier
  to type. For example 'MyCompany Engineering (all devs) AWS' will become
  `mycompany-engineering`. The exact rules are:
  * Any trailing 'AWS' suffix, if present, is removed
  * Anything in parentheses is stripped
  * Everything is converted to lowercaase
  * Spaces are stripped and replaced with dashes
* `cookie_file` - the location where the okta session cookie is stored. This
  defaults to `~/.okta_aws_cookie`.
* `session_duration` - How long to request that the AWS temporary credentials
  should be valid for. This defaults to `3600` (1 hour), but you can choose a
  shorter or longer value up to `43200` (12 hours).
  * Note: in order to choose a session length longer than 1 hour, you need to
    configure the role in AWS to allow longer sessions. In the IAM console,
    find the role and exit the `Maximum CLI/API session duration` setting.
* `role_arn` - the ARN or name of the role to assume. This only needs to be
  set if you have more than one role and are prompted to select which role to
  assume when you run okta_aws.

Each of these settings can be set per-profile. To do this, create a new
section in the configuration file with the name of the profile, and put your
per-profile settings here. For example, in order to use a longer session
length for the `mycompany-dev` profile, add this to your `~/.okta_aws.toml`
file:

```
[mycompany-dev]
session_duration = 43200
```

Or, if you are prompted when logging into the `mycompany-staging` profile
which role you want to use, then you can configure a default role as follows:

```
[mycompany-staging]
role_arn = "Okta_PowerUser"
# Alternatively you can specify the full ARN
# role_arn = "arn:aws:iam::1234567890:role/Okta_PowerUser"
```

### Profile aliases

Sometimes, the profile name obtained from okta doesn't match the profile name
you want to use in your AWS credentials file (for example, you might have a
specific profile name hardcoded in scripts). In these cases, you can configure
a profile name to be an _alias_ of another. To do this, add an `[aliases]`
section to your `.okta_aws.toml` file. For example, if `okta_aws --list` shows
an available profile of `companyname-engineering` but you have
`engineering` configured as a profile name in your scripts, you can do:

```
[aliases]
engineering = "companyname-engineering"
```

Then, you just set `AWS_PROFILE` to `engineering`, or pass `engineering` as an
argument to okta_aws, and it will log in with the `companyname-engineering`
profile, while storing the credentials in an `engineering` profile in your
`~/.aws/credentials` file.

If you want to configure profile specific settings for a profile that has an
alias, you can configure them under either the profile name itself, or the
alias. If you configure the settings under the 'real' name of the profile,
then those settings will also be used if you refer to the profile by its
alias. If you configure them under the alias, then they will only take effect
if you refer to the profile by its alias.

### GovCloud

If the profile name includes 'govcloud', then okta_aws will use the appropriate
region for fetching govcloud credentials (us-gov-east-1).

## Usage

Run `okta_aws PROFILENAME`, or run `okta_aws` without any arguments and
okta_aws will use the `AWS_PROFILE` environment variable if you have it set.

To fetch credentials for all profiles you have access to, run `okta_aws --all`.

To list the available profiles, run `okta_aws --list`.

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
expires. If you wish, you can run one of the following to automatically refresh
the token once every 55 minutes (allowing some grace period before the token
expires):

    while true; do okta_aws PROFILENAME; sleep 3300; done
    while true; do okta_aws --all; sleep 3300; done

okta_aws will run without prompting for anything one you have logged in and,
if necessary, configured a default profile in `~/.okta_aws.toml`.

Users of zsh may find this `oh-my-zsh` plugin useful for shell-integrated
auto-refresh:  [okta-aws plugin for zsh](https://gist.github.com/irvingpop/8e4e3bc63497be3432e695a52ef885f0)

## Similar projects

* [okta-aws-cli-assume-role](https://github.com/oktadeveloper/okta-aws-cli-assume-role) - Okta's own tool
* [oktaauth](https://github.com/ThoughtWorksInc/oktaauth) - Python library for working with okta
* [segmentio/aws-okta](https://github.com/segmentio/aws-okta) - uses assumerole
  to connect to multiple aws accounts while signing into a primary aws account
  in okta.
* [aws-vault](https://github.com/99designs/aws-vault) - tool for securely storing aws credentials
* [okta_aws_login](https://github.com/nimbusscale/okta_aws_login)
* [okta-awscli](https://github.com/jmhale/okta-awscli)
