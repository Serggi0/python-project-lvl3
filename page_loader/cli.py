import argparse


def create_parser_arg():
    parser_arg = argparse.ArgumentParser(description='download the web-site')
    parser_arg.add_argument('directory')
    parser_arg.add_argument('site')
    parser_arg.add_argument('-o', '--output',
                            help='download the page from the web and put it in the specified existing directory (by default, in the program launch directory)',
                            default='/var/tmp'
                            )
    parser_arg.print_help()
    return parser_arg
