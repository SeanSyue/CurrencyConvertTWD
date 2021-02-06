import configparser
from pathlib import Path
from shutil import copy

config = configparser.ConfigParser()
config.read('config.ini')

# The directory which currency exchange rate table is downloaded and stored
_FOLDER = config['TABLE']['folder']


p_folder = Path(__file__).parent.joinpath(_FOLDER)
p_folder.mkdir(exist_ok=True)

_TEST_CSV_OLD_1 = 'mock_tables/ExchangeRate@201912021600.csv'
_TEST_CSV_OLD_2 = 'mock_tables/ExchangeRate@201912201451.csv'
_TEST_CSV_NEW = 'mock_tables/ExchangeRate@201912201528.csv'


# copy(_TEST_CSV_OLD_1, str(p_folder.joinpath(Path(_TEST_CSV_OLD_1).name)))


def __make_existed_tables(*tables):
    for test_csv in tables:
        src = str(Path(test_csv).resolve())
        des = str(p_folder.joinpath(Path(test_csv).name))
        print(f"{src = }")
        print(f"{des = }")
        copy(src, des)
        

tables_for_testing = (_TEST_CSV_OLD_1, _TEST_CSV_OLD_2)
# __make_existed_tables()
__make_existed_tables(*tables_for_testing)
