"""
    Boatswain command line interface
"""
from __future__ import absolute_import

import argparse
import sys
import logging
import yaml
from .boatswain import Boatswain
from .bcolors import bcolors


def argparser():
    """
        Define the argument parsers for Boatswain

        We use subparsers, currently the implemented subparsers are:
        - build: building docker images
    """
    desc = 'Builds docker images based on a docker-compose style yaml file'
    parser = argparse.ArgumentParser(description=desc)

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    subparsers.required = True

    #
    # Common options
    #
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '-v', '--verbose', help="Verbose output",
        action='store_true'
    )
    common.add_argument(
        '--dryrun', help="Do a dry run don't actually build",
        action='store_true'
    )
    common.add_argument(
        '--debug', help="Debug boatswain itself",
        action='store_true'
    )
    common.add_argument(
        '-b', '--boatswain_file', help='Override the default boatswain file',
        default='boatswain.yml'
    )

    #
    # Build parser
    #
    buildparser = subparsers.add_parser(
        'build', help='builds the images specified in the boatswain.yml file',
        parents=[common]
    )
    buildparser.add_argument(
        '-f', '--force',
        help="Force building images even if they already exists",
        action='store_true'
    )
    buildparser.add_argument(
        'imagename', help="Name of the image to build",
        nargs='?'
    )

    #
    # Clean parser
    #
    cleanparser = subparsers.add_parser(
        'clean', help='Clean the images specified in the boatswain.yml file',
        parents=[common]
    )
    cleanparser.add_argument(
        'imagename', help="Name of the image to clean",
        nargs='?'
    )

    return parser


def exit_with_message(message, number):
    """
        Exit nicely with a pretty colored message
    """
    if message:
        if number < 0:
            print(bcolors.fail(message))
        elif number > 0:
            print(bcolors.warning(message))
        else:
            print(bcolors.green(message))
    sys.exit(number)


def main():
    """
        Run the boatswain command using the given arguments
    """
    parser = argparser()
    print(bcolors.header("Welcome to Boatswain"))

    if len(sys.argv) < 1:
        parser.print_help()
        exit_with_message("", 1)

    arguments = parser.parse_args()

    if arguments.debug:
        logging.basicConfig(level=logging.DEBUG)

    command = arguments.command
    try:
        with open(arguments.boatswain_file) as yamlfile:
            bsfile = yaml.load(yamlfile)
    except IOError as error:
        exit_with_message(error.filename + ": " + error.strerror, -error.errno)

    bosun = Boatswain(bsfile)

    if command == 'build':
        if arguments.imagename:
            bosun.build_up_to(arguments.imagename, dryrun=arguments.dryrun,
                              verbose=arguments.verbose, force=arguments.force)
        else:
            bosun.build(dryrun=arguments.dryrun, verbose=arguments.verbose,
                        force=arguments.force)
    elif command == 'clean':
        if arguments.imagename:
            bosun.clean_up_to(arguments.imagename, dryrun=arguments.dryrun)
        else:
            bosun.clean(dryrun=arguments.dryrun)
