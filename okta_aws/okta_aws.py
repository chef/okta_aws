#
# Copyright 2017 Chef Software
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import base64
import getpass
import json
import html
import logging
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import requests
import toml

__VERSION__ = '0.5.0'


class OktaAWS(object):
    def __init__(self, argv=None):
        """Initialize the program

        argv - command line arguments (or None to use sys.argv)
        """
        self.args = self.parse_args(argv)
        self.profile = self.args.profile

    def parse_args(self, argv):
        """Parses command line arguments using argparse

        argv - command line arguments (or None to use sys.argv)
        """
        parser = argparse.ArgumentParser(
            description='Generates temporary AWS credentials for an AWS'
            ' account you access through okta.')
        parser.add_argument('profile', nargs='?',
                            default=os.getenv("AWS_PROFILE") or "default",
                            help='The AWS profile you want credentials for')
        parser.add_argument('--config', '-c', default='~/.okta_aws.toml',
                            help='Path to the configuration file')
        parser.add_argument('--no-cookies', '-n', action='store_true',
                            help="Don't use or save okta session cookie")
        parser.add_argument('--debug', '-d', action='store_true',
                            help='Show debug output')
        parser.add_argument('--quiet', '-q', action='store_true',
                            help='Only show error messages')
        parser.add_argument('--list', '-l', action='store_true',
                            help="Don't assume a role, list assigned "
                            "applications in okta")
        parser.add_argument('--all', '-a', action='store_true',
                            help='Assume a role in all assigned accounts')
        parser.add_argument('--version', '-v', action='version',
                            version=__VERSION__,
                            help='Show version of okta_aws and exit')
        parser.add_argument('--setup', '-s', action='store_true',
                            help="Set up a config file for okta_aws")
        return parser.parse_args(argv)

    def setup_logging(self):
        """Sets up logging based on whether debugging is enabled or not"""
        if self.args.debug:
            logging.basicConfig(
                format='%(asctime)s %(levelname)s %(message)s',
                level=logging.DEBUG)
        elif self.args.quiet:
            logging.basicConfig(format='%(message)s', level=logging.ERROR)
        else:
            logging.basicConfig(format='%(message)s', level=logging.INFO)

    def preflight_checks(self):
        """Performs some checks to ensure that the program can be run
        successfully. If these checks fail, an explanation is given as well as
        a hint for how the user can fix the problem.
        """
        errors = []
        # AWS cli
        if shutil.which("aws") is None:
            errors.append("The AWS CLI (the 'aws' command) cannot be found. "
                          "see http://docs.aws.amazon.com/cli/latest/"
                          "userguide/installing.html for information on "
                          "installing it.")
        if errors:
            print("Preflight check failed")
            print("======================")
            for e in errors:
                print("* %s" % e)
            sys.exit(1)

    def interactive_setup(self, config_file):
        """Performs first-time setup for users who haven't set up a config
        file yet, by asking some simple questions.
        """
        try:
            toml_config = toml.load(os.path.expanduser(config_file))
        except FileNotFoundError:
            toml_config = {}
        toml_config.setdefault('general', {})

        default_username = toml_config['general'].get(
            'username', getpass.getuser())
        default_server = toml_config['general'].get(
            'okta_server', 'example.okta.com')

        print("Okta AWS initial setup")
        print("======================")
        print()
        username = input("Enter your okta username [%s]: " % default_username)
        if username == "":
            username = default_username

        okta_server = input("Enter your okta domain [%s]: " % default_server)
        if okta_server == "":
            okta_server = default_server

        print()
        print("Creating/updating %s" % config_file)
        toml_config['general']['username'] = username
        toml_config['general']['okta_server'] = okta_server
        with open(os.path.expanduser(config_file), "w") as fh:
            toml.dump(toml_config, fh)

        print("Setup complete. You can now log in with okta_aws PROFILENAME.")
        print("Hint: you can use 'okta_aws --list' to see which profiles "
              "you can use.")

    def load_config(self, config_file):
        """Loads the config file and returns a dictionary containing its
        contents.

        config_file - path to the configuration file to load
        """
        try:
            config = toml.load(os.path.expanduser(config_file))
        except FileNotFoundError:
            self.interactive_setup(config_file)
            sys.exit(0)

        config.setdefault('general', {})
        config.setdefault('aliases', {})

        required_config_options = [
            'username',
            'okta_server'
        ]

        missing_options = [k for k in required_config_options
                           if k not in config['general']]
        if missing_options:
            logging.error("Missing required configuration settings: %s",
                          ', '.join(missing_options))
            sys.exit(1)

        # Default configuration values
        config['general'].setdefault('cookie_file', '~/.okta_aws_cookie')
        config['general'].setdefault('short_profile_names', True)
        config['general'].setdefault('session_duration', 3600)

        config['general']['cookie_file'] = os.path.expanduser(
            config['general']['cookie_file'])

        return config

    def get_config(self, key, default=None):
        """Obtain a profile specific configuration value, falling back to the
        general config or a default value"""
        try:
            return self.config[self.profile][key]
        except KeyError:
            try:
                real_profile = self.config['aliases'][self.profile]
                return self.config[real_profile][key]
            except KeyError:
                return self.config['general'].get(key, default)

    def choose_from_menu(self, choices, prompt="Select an option: "):
        """Present an interactive menu of choices for the user to pick from.

        Returns the index into the list of the selected item.

        choices - a list of options to choose from
        prompt  - the prompt to show to the user
        """
        for idx, value in enumerate(choices):
            print("%2d) %s" % (idx + 1, value))
        response = 0
        while response < 1 or response > len(choices):
            try:
                response = int(input(prompt))
            except ValueError:
                # If we enter something invalid, just go through the
                # loop again.
                pass
        return response - 1

    def select_role(self, arns):
        """Returns the role to use from a list of principal/role arn pairs,
        based on either a configuration option, user selecting from a menu,
        or simply returning the only arn pair in the list if there is only
        one.

        arns - a list of arn pairs (each pair should be a princpal/role arn)
        """
        selected = None
        if len(arns) > 1:
            role_arn = self.get_config('role_arn')
            if role_arn is not None:
                # First check to see if we configured a default role
                logging.debug("Looking for configured role: %s", role_arn)
                for arn in arns:
                    # Use endswith here so we can provide just a role name
                    # instead of the full ARN.
                    if arn[1].endswith(role_arn):
                        selected = arn
            if selected is None:
                # We either didn't configure a default role or the configured
                # default role didn't match any available roles. Ask the user
                # to pick one.
                print("Available roles")
                response = self.choose_from_menu(
                    [arn[1].split('/')[-1] for arn in arns],
                    "Select role to log in with: ")
                selected = arns[response]
        else:
            selected = arns[0]
        return selected

    def get_arns(self, saml_assertion):
        """Extracts the available principal/role ARNS for a user given a
        base64 encoded SAML assertion returned by okta.

        saml_assertion - the saml asssertion given by okta, base64 encoded.
        """
        parsed = ET.fromstring(base64.b64decode(saml_assertion))
        # Horrible xpath expression to dig into the ARNs
        elems = parsed.findall(
            ".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute["
            "@Name='https://aws.amazon.com/SAML/Attributes/Role']//*")
        # text contains Principal ARN, Role ARN separated by a comma
        arns = [e.text.split(",", 1) for e in elems]
        selected = self.select_role(arns)
        # Returns principal_arn, role_arn
        logging.debug("Principal ARN: %s", selected[0])
        logging.debug("Role ARN: %s", selected[1])
        return selected

    def aws_assume_role(self, principal_arn, role_arn, assertion, duration):
        """Gets temporary credentials from aws. Returns a dictionary
        containing the temporary credentials.

        principal_arn - the principal_arn (obtained from saml assertion)
        role_arn  - the arn of the role to assume (obtained from saml
                    assertion)
        assertion - the saml assertion itself (base64 encoded)
        duration  - how long to request the credentials be valid for in
                    seconds. This can't be longer than AWS allows (3600 by
                    default, may be configured to be as long as 43200)
        """

        # Override AWS_PROFILE so aws sts doesn't complain if we have it set
        # to a new profile that doesn't yet exist
        newenv = os.environ.copy()
        if 'AWS_PROFILE' in newenv:
            del newenv['AWS_PROFILE']
        if 'AWS_DEFAULT_PROFILE' in newenv:
            del newenv['AWS_DEFAULT_PROFILE']

        try:
            output = subprocess.check_output([
                "aws", "sts", "assume-role-with-saml",
                "--role-arn", role_arn,
                "--principal-arn", principal_arn,
                "--saml-assertion", assertion,
                "--duration-seconds", str(duration)],
                                             env=newenv)
        except OSError as e:
            if e.errno == 2:
                logging.error(
                    "The AWS CLI cannot be found, see: http://docs.aws"
                    ".amazon.com/cli/latest/userguide/installing.html")
                logging.error("If you are on a mac with homebrew, run "
                              "`brew install awscli`")
                sys.exit(1)
            raise
        except subprocess.CalledProcessError as e:
            print("Error getting temporary credentials. Exiting...")
            sys.exit(1)

        aws_creds = json.loads(output.decode('utf-8'))
        return aws_creds['Credentials']

    def set_aws_config(self, profile, key, value):
        """Sets a single AWS configuration option. Used to store the temporary
        credentials in ~/.aws/credentials.

        profile - the profile to set the configuration option under
        key     - the option to change
        value   - the value to change it to
        """
        # Override AWS_PROFILE so aws sts doesn't complain if we have it set
        # to a new profile that doesn't yet exist
        newenv = os.environ.copy()
        if 'AWS_PROFILE' in newenv:
            del newenv['AWS_PROFILE']
        if 'AWS_DEFAULT_PROFILE' in newenv:
            del newenv['AWS_DEFAULT_PROFILE']

        subprocess.call(["aws", "configure", "set",
                         "--profile", profile, key, value],
                        env=newenv)

    def store_aws_creds_in_profile(self, profile, aws_creds):
        """Stores the temporary AWS credentials in ~/.aws/credentials.

        profile - the profile to store the credentials under
        aws_creds - a dictionary containing the credentials returned from AWS
        """
        self.set_aws_config(profile, "aws_access_key_id",
                            aws_creds['AccessKeyId'])
        self.set_aws_config(profile, "aws_secret_access_key",
                            aws_creds['SecretAccessKey'])
        self.set_aws_config(profile, "aws_session_token",
                            aws_creds['SessionToken'])

    def is_logged_in(self, session_id):
        """Checks to see if a given okta session ID is still valid. Will return
        false if the session has expired and we are no longer logged in to
        okta.

        session_id - the session token that we are verifying
        """
        logging.debug("Verifying if we are already logged in")
        r = requests.get("https://%s/api/v1/sessions/me" %
                         self.get_config('okta_server'),
                         cookies={"sid": session_id})
        logged_in = r.status_code == 200
        logging.debug("Logged in: %s", logged_in)
        return logged_in

    def log_in_to_okta(self, password):
        """Logs in to okta using the authn API, returning a single use session
        token that can be exchanged for a long lived session ID.

        password - the user's okta password
        """
        r = requests.post(
            "https://%s/api/v1/authn" % self.get_config('okta_server'),
            json={
                "username": self.get_config('username'),
                "password": password
            })
        if r.status_code != 200:
            logging.debug(r.text)
            return None
        return r.json()['sessionToken']

    def get_session_id(self, session_token):
        """Returns a (long lived) session ID given a (single use) session
        token.

        session_token - the single use token returned when logging in to okta
        """
        r = requests.post(
            "https://%s/api/v1/sessions" % self.get_config('okta_server'),
            json={"sessionToken": session_token})
        if r.status_code != 200:
            logging.debug(r.text)
            return None
        return r.json()['id']

    def get_assigned_applications(self, session_id):
        """Queries okta to get a list of AWS applications that have been
        assigned to the user. Returns a dictionary mapping the profile names
        to log in URLs for each assigned application.

        session_id - the okta session ID needed to make api calls
        """
        # TODO - proper pagination on this
        logging.debug("Getting assigned application links from okta")
        r = requests.get("https://%s/api/v1/users/me/appLinks?limit=1000" %
                         self.get_config('okta_server'),
                         cookies={"sid": session_id})
        if r.status_code != 200:
            logging.error("Error getting assigned application list")
            logging.debug(r.text)
            return None
        applinks = {i['label']: i['linkUrl'] for i in r.json()
                    if i['appName'] == 'amazon_aws'}
        return applinks

    def shorten_appnames(self, applinks):
        """Converts long application names such as
        'Company Engineering AWS (dev use)' to something suitable for use in
        an aws profile such as 'company-engineering'.

        applinks - a dictionary mapping application names to application links.
        """
        logging.debug("Shortening application names")
        newapplinks = {}
        for k, v in applinks.items():
            newk = re.sub(" *AWS$", "", k)  # Remove AWS suffix
            newk = re.sub(r" *\(.*\)", "", newk)  # Remove anything in parens
            newk = newk.lower()
            newk = re.sub(" +", "-", newk)
            newapplinks[newk] = v
            logging.debug("%s => %s", k, newk)
        return newapplinks

    def get_saml_assertion(self, session_id, app_url):
        """Sends a request to the application link, and extracts a SAML
        assertion from the response.

        session_id - okta session ID needed to make api calls
        app_url    - The URL used to log in to the okta application
        """
        r = requests.post(app_url, cookies={"sid": session_id})

        if r.status_code != 200:
            logging.error("Error getting saml assertion. HTML response %s",
                          r.status_code)
            return None

        match = re.search(r'<input name="SAMLResponse".*value="([^"]*)"',
                          r.text)
        if not match:
            return None
        return html.unescape(match.group(1))

    def friendly_interval(self, seconds):
        """Converts a number of seconds into something a little friendlier,
        such as '10 minutes' or '1 hour'.

        seconds - an integer number of seconds to convert
        """
        if seconds == 3600:
            return "1 hour"
        elif seconds >= 3600:
            return "%.2g hours" % (seconds / 3600.0)
        elif seconds == 60:
            return "1 minute"
        return "%.2g minutes" % (seconds / 60.0)

    def fetch_credentials(self, applinks, session_id):
        """Performs the various steps needed to actually get a set of
        temporary credentials and store them. Doesn't return anything, but
        temporary credentials should be stored in ~/.aws/credentials by the
        time this method has finished.

        applinks   - a mapping of profile names to application links
        session_id - okta session ID needed to make API calls
        """
        # Resolve any profile alias and store it in real_profile
        real_profile = self.config['aliases'].get(self.profile, self.profile)

        if real_profile not in applinks:
            alias_msg = ""
            if real_profile != self.profile:
                alias_msg = " (an alias that resolved to %s)" % real_profile
            print("ERROR: %s%s isn't a valid profile name" % (
                self.profile, alias_msg))
            print("Valid profiles:", ', '.join(list(applinks.keys())))
            sys.exit(1)

        saml_assertion = self.get_saml_assertion(
            session_id, applinks[real_profile])
        if saml_assertion is None:
            logging.error("Problem getting SAML assertion")
            sys.exit(1)

        principal_arn, role_arn = self.get_arns(saml_assertion)

        logging.info("Assuming AWS role %s...", role_arn.split("/")[-1])
        session_duration = self.get_config('session_duration')
        aws_creds = self.aws_assume_role(principal_arn, role_arn,
                                         saml_assertion, session_duration)
        self.store_aws_creds_in_profile(self.profile, aws_creds)
        logging.info("Temporary credentials stored in profile %s",
                     self.profile)
        logging.info("Credentials expire in %s",
                     self.friendly_interval(session_duration))

    def run(self):
        """Main entry point for the application after parsing command line
        arguments."""
        self.setup_logging()

        self.preflight_checks()

        if self.args.setup:
            self.interactive_setup(self.args.config)
            sys.exit(0)

        self.config = self.load_config(self.args.config)

        if not self.args.no_cookies:
            if os.path.exists(self.get_config('cookie_file')):
                logging.debug("Loading session ID from %s",
                              self.get_config('cookie_file'))
                with open(self.get_config('cookie_file')) as fh:
                    session_id = fh.read().rstrip("\n")
                    # Support old cookie file format
                    if session_id.startswith('#LWP-Cookies-2.0'):
                        logging.debug("Converting old cookie file format")
                        m = re.search(r'sid="([^"]*)"', session_id)
                        if m:
                            logging.debug("Found session ID in old cookies")
                            session_id = m.group(1)
                        else:
                            logging.debug("Didn't find session ID in cookies")
                            session_id = None
                if session_id is not None \
                        and not self.is_logged_in(session_id):
                    session_id = None
            else:
                session_id = None

        if session_id is None:
            print("Okta Username:", self.get_config('username'))
            password = ""
            while password == "":
                password = getpass.getpass("Okta Password: ")
            sys.stdout.flush()

            onetimetoken = self.log_in_to_okta(password)
            if onetimetoken is None:
                logging.error("Error logging into okta.")
                sys.exit(1)

            session_id = self.get_session_id(onetimetoken)
            if not self.args.no_cookies:
                logging.debug("Saving session cookie to %s",
                              self.get_config('cookie_file'))
                with open(self.get_config('cookie_file'), 'w') as fh:
                    fh.write(session_id)

        applinks = self.get_assigned_applications(session_id)
        if self.get_config('short_profile_names'):
            applinks = self.shorten_appnames(applinks)

        if self.args.all:
            for profile in applinks.keys():
                print("Fetching credentials for:", profile)
                self.profile = profile
                self.fetch_credentials(applinks, session_id)
            sys.exit(0)

        if self.args.list:
            print("Available profiles:")
            reverse_aliases = {}
            for k, v in self.config['aliases'].items():
                reverse_aliases.setdefault(v, []).append(k)
            for profile in applinks.keys():
                if profile in reverse_aliases:
                    print("%s (Aliases: %s)" % (profile, ', '.join(
                        reverse_aliases[profile])))
                else:
                    print(profile)

            sys.exit(0)

        self.fetch_credentials(applinks, session_id)
