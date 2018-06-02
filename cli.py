import os
import argparse
from Converter import CurrencyConverter


def update(instance_, file_):
    print("Updating...")
    instance_.load_data(file_)
    print("Done")


def listing(instance_, args_):
    print("List!")
    if args_.currencies is not None:
        instance_.show_rates(*args_.currencies)
    else:
        instance_.show_all_rates()


def convert():
    print("Convert!")


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

    args = parser.parse_args()

    if args.which == 'update':
        update(instance, file)
    elif args.which == 'list':
        listing(instance, args)
    elif args.which == 'convert':
        convert()


# args = parser.parse_args('update'.split())
# args.func(args)

# parser.parse_args('update'.split())


if __name__ == '__main__':
    rates_table_path = 'exchange-rate-tables'
    csv_file = os.path.join(rates_table_path, 'ExchangeRate@201806011602.csv')
    cvt = CurrencyConverter()
    cvt.load_data(csv_file)

    run_cli(cvt, csv_file)
