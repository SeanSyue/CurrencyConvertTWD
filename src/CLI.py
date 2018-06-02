import os
import argparse
# import sys
from src.Converter import CurrencyConverter
from src.TableManager import download_csv, search_newest_file

# sys.path.insert(0, 'src')
# TABLE_PATH = '../exchange-rate-tables'
TABLE_PATH = 'D:/WORKSPACE/PycharmProjects/CurrencyConvertTWD/exchange-rate-tables'
# sys.path.insert(0, 'TABLE_PATH')


def update(instance_, file_):
    print("[INFO] finding for table...")
    download_csv(folder=TABLE_PATH)
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
    if not os.path.isdir(TABLE_PATH):
        os.makedirs(TABLE_PATH)
    for _, _, files in os.walk(TABLE_PATH):
        if not files:
            download_csv(TABLE_PATH)

    # specify currency exchange rate table filepath
    rates_table_path = None
    try:
        rates_table_path = TABLE_PATH
        csv_file = search_newest_file(rates_table_path)
    except FileNotFoundError:
        print("[ERROR] Can not find table path{}".format(rates_table_path))
        raise
    file = os.path.join(rates_table_path, csv_file)

    # initiate CurrencyConverter object
    instance = CurrencyConverter()
    instance.load_data(file)

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

# args = parser.parse_args('update'.split())
# args.func(args)

# parser.parse_args('update'.split())


# if __name__ == '__main__':
# # specify currency exchange rate table filepath
# rates_table_path = None
# try:
#     rates_table_path = '../exchange-rate-tables'
#     csv_file = search_newest_file(rates_table_path)
# except FileNotFoundError:
#     print("[ERROR] Can not find table path{}".format(rates_table_path))
#     raise
# table_filepath = os.path.join(rates_table_path, csv_file)
#
# # initiate CurrencyConverter object
# cvt = CurrencyConverter()
# cvt.load_data(table_filepath)

# # run main function
# run_cli(cvt, table_filepath)
