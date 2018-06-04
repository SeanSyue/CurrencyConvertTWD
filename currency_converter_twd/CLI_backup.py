import os
import argparse
from currency_converter_twd.Converter import CurrencyConverter
from currency_converter_twd.TableManager import csv_downloader, search_newest_file

# The directory which currency exchange rate table is downloaded and stored
TABLE_PATH = 'D:/WORKSPACE/PycharmProjects/CurrencyConvertTWD/exchange-rate-tables'


def update(instance_, file_):
    print("[INFO] finding for table...")
    csv_downloader(folder=TABLE_PATH)
    print("[INFO] Loading data...")
    instance_.load_data(file_)
    print("[INFO] Done")


def info(instance_):
    instance_.show_currency_descriptions()


def lookup(instance_, args_):
    if args_.currencies is not None:
        instance_.show_rates(*args_.currencies)
    else:
        instance_.show_all_rates()


def convert(instance_, args_):
    instance_.convert(args_.value, args_.from_cur, args_.from_type, args_.to_cur, args_.to_type)


def run_cli():
    # For the first run, make the TABLE_PATH directory
    if not os.path.isdir(TABLE_PATH):
        os.makedirs(TABLE_PATH)

    # initialize csv file & path variables
    table_dir = TABLE_PATH
    csv_file = csv_downloader(TABLE_PATH)

    # if not csv file was found, download a new one
    # if file has not unsuccessful downloaded, print error message, then quit program


    # initiate CurrencyConverter object
    file = os.path.join(table_dir, csv_file)
    instance = CurrencyConverter()
    instance.load_data(file)

    # ----------------------------------------------------------------------------------------------
    # The real CLI part begins
    # ----------------------------------------------------------------------------------------------

    parser = argparse.ArgumentParser(prog='Currency-Converter',
                                     description='Tool for converting units',
                                     epilog='Well, this one should displayed at the end')
    parser.add_argument(
        '-v', '--version',
        dest='version',
        action='version',
        version='%(prog)s ** version: 0.1 **'
    )

    subparsers = parser.add_subparsers(
        help='operation to be performed. update to update, lookup to lookup, convert to convert', dest='which')

    update_parser = subparsers.add_parser('update')
    update_parser.set_defaults(which='update')

    lookup_parser = subparsers.add_parser('lookup')
    lookup_parser.set_defaults(which='lookup')
    lookup_parser.add_argument('--currencies', '-c',
                               type=str,
                               action='store',
                               nargs='+',
                               help='lookup parser currencies',
                               )

    info_parser = subparsers.add_parser('info')
    info_parser.set_defaults(which='info')

    convert_parser = subparsers.add_parser('convert')
    convert_parser.set_defaults(which='convert')
    convert_parser.add_argument('value',
                                metavar='VALUE',
                                action='store',
                                type=float,
                                help='input value to convert')
    convert_parser.add_argument('from_cur',
                                metavar='FROM_CURRENCY',
                                action='store',
                                type=str,
                                help='from which currency to convert')
    convert_parser.add_argument('from_type',
                                metavar='FROM_TYPE',
                                action='store',
                                type=str,
                                choices={'cash', 'spot', 'Cash', 'Spot', 'CASH', 'SPOT'},
                                nargs='?',
                                default='cash',
                                help='from which type to convert')
    convert_parser.add_argument('to_cur',
                                metavar='TO_CURRENCY',
                                action='store',
                                type=str,
                                nargs='?',
                                default='NTD',
                                help='to which currency to convert')
    convert_parser.add_argument('to_type',
                                metavar='TO_TYPE',
                                action='store',
                                type=str,
                                choices={'cash', 'spot', 'Cash', 'Spot', 'CASH', 'SPOT'},
                                nargs='?',
                                default='cash',
                                help='to which type to convert')

    args = parser.parse_args()

    if args.which == 'update':
        update(instance, file)
    elif args.which == 'info':
        info(instance)
    elif args.which == 'lookup':
        lookup(instance, args)
    elif args.which == 'convert':
        convert(instance, args)