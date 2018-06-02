import os
import argparse
from Converter import CurrencyConverter
from TableManager import download_csv, search_newest_file


def update(instance_, file_):
    print("[INFO] Checking for table...")
    download_csv()
    print("[INFO] Loading data...")
    instance_.load_data(file_)
    print("[INFO] Done")


def listing(instance_, args_):
    print("List!")
    if args_.currencies is not None:
        instance_.show_rates(*args_.currencies)
    else:
        instance_.show_all_rates()


def convert(instance_, args_):
    instance_.convert(args_.value, args_.from_cur, args_.from_type, args_.to_cur, args_.to_type)


def run_cli(instance, file):
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
        help='operation to be performed. update to update, list to list, convert to convert')

    update_parser = subparsers.add_parser('update')
    update_parser.set_defaults(which='update')

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(which='list')
    list_parser.add_argument('--currencies', '-c',
                             type=str,
                             action='store',
                             nargs='+',
                             help='list parser currencies'
                             )

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
    elif args.which == 'list':
        listing(instance, args)
    elif args.which == 'convert':
        convert(instance, args)


# args = parser.parse_args('update'.split())
# args.func(args)

# parser.parse_args('update'.split())


if __name__ == '__main__':
    # specify currency exchange rate table filepath
    rates_table_path = None
    try:
        rates_table_path = '../exchange-rate-tables'
        csv_file = search_newest_file(rates_table_path)
    except FileNotFoundError:
        print("[ERROR] Can not find table path{}".format(rates_table_path))
        raise
    table_filepath = os.path.join(rates_table_path, csv_file)

    # initiate CurrencyConverter object
    cvt = CurrencyConverter()
    cvt.load_data(table_filepath)

    # run main function
    run_cli(cvt, table_filepath)
