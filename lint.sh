#!/bin/bash
# Quick script to lint okta_aws
# Serves mostly as a reminder of which tools are used.

# Installation of tools on a mac:
#   brew install flake8
#   pip3 install pylint

flake8
pylint okta_aws
