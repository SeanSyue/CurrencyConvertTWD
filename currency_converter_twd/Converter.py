"""
Some statements should be consistent with CLI.py.
Check for them by searching 'This one should be consistent with the command CLI.py'
"""
import pandas
import numpy as np


class _CurrencyTable:
    """
    Basic currency table loader.
    Including functions for inspecting available currencies, currency rates and exchange type
    Should use "self.load_data" method first after initialization before using other commands!
    """

    def __init__(self):
        # Name of csv file loaded
        self.filename = None

        # Some meta constants
        self._BASE = 'NTD'
        self._CASH = 'cash'
        self._SPOT = 'spot'
        self._CASH_BUY = 'Cash.Buy'
        self._CASH_SELL = 'Cash.Sell'
        self._SPOT_BUY = 'Spot.Buy'
        self._SPOT_SELL = 'Spot.Sell'

        # Column names of exchange rates
        self._ex_col_names = [self._CASH_BUY, self._CASH_SELL, self._SPOT_BUY, self._SPOT_SELL]
        # Available exchange types
        self._ex_types = {self._CASH, self._SPOT}

        # Descriptions of each currency
        self._INFO_DICT = {'USD': 'US Dollar', 'HKD': 'Hong Kong Dollar', 'GBP': 'British Pound',
                           'AUD': 'Australian Dollar', 'CAD': 'Canadian Dollar', 'SGD': 'Singapore Dollar',
                           'CHF': 'Swiss Franc', 'JPY': 'Japanese Yen', 'ZAR': 'South African Rand',
                           'SEK': 'Swedish Krona', 'NZD': 'New Zealand Dollar', 'THB': 'Thai Baht',
                           'PHP': 'Philippine Peso', 'IDR': 'Indonesian Rupiah', 'EUR': 'Euro',
                           'KRW': 'Korean Won', 'VND': 'Vietnam Dong', 'MYR': 'Malaysian Ringgit', 'CNY': 'China Yuan'}

        # Available currencies for exchange
        self._cur_list = list(self._INFO_DICT.keys())+[self._BASE]

        self._df = None

    def load_data(self, file_):
        """ Used to initialize/update data-frame """

        # Load csv file as data-frame
        self._df = pandas.read_csv(file_, index_col=False,
                                   usecols=['Currency', 'Cash', 'Spot', 'Cash.1', 'Spot.1']) \
            .replace({'0': np.nan, 0: np.nan}) \
            .rename(index=str, columns={"Cash": self._CASH_BUY, "Spot": self._SPOT_BUY,
                                        "Cash.1": self._CASH_SELL, "Spot.1": self._SPOT_SELL}) \
            .set_index(['Currency'])
        self._df['Description'] = self._df.index.map(self._INFO_DICT)

        self.filename = file_

    def get_cash_buy(self, cur):
        """ Get one single currency rate """
        if cur not in self._cur_list:
            # This one should be consistent with the command CLI.py
            print("[WARNING] Invalid currency detected\n"
                  "Use 'cvtwd info' or 'cvtwd lookup' to check for available currencies")
        return self._df.loc[cur, self._CASH_BUY]

    def get_cash_sell(self, cur):
        """ Get one single currency rate """
        if cur not in self._cur_list:
            # This one should be consistent with the command CLI.py
            print("[WARNING] Invalid currency detected\n"
                  "Use 'cvtwd info' or 'cvtwd lookup' to check for available currencies")
        return self._df.loc[cur, self._CASH_SELL]

    def get_spot_buy(self, cur):
        """ Get one single currency rate """
        if cur not in self._cur_list:
            # This one should be consistent with the command CLI.py
            print("[WARNING] Invalid currency detected\n"
                  "Use 'cvtwd info' or 'cvtwd lookup' to check for available currencies")
        return self._df.loc[cur, self._SPOT_BUY]

    def get_spot_sell(self, cur):
        """ Get one single currency rate """
        if cur not in self._cur_list:
            # This one should be consistent with the command CLI.py
            print("[WARNING] Invalid currency detected\n"
                  "Use 'cvtwd info' or 'cvtwd lookup' to check for available currencies")
        return self._df.loc[cur, self._SPOT_SELL]

    def show_rates(self, *cur):
        """
        Print exchange rates between given currency to/from base currency.
        Can handle multiple currency query
        """
        print(self._df.reindex(cur).loc[:, self._ex_col_names])
        if set(cur).issubset(self._cur_list) is False:
            print('[WARNING] Invalid currency detected')

    def show_currency_descriptions(self):
        """ Print available currencies """
        print(self._df.loc[:, ['Description']])
        print("base: {}".format(self._BASE))

    def show_all_rates(self):
        """ Print all exchange rates """
        print(self._df.loc[:, self._ex_col_names])

    def show_ex_types(self):
        """ Print available exchange type """
        print(self._ex_types)


class _SimpleConverter(_CurrencyTable):
    """
    Do computational works.
    Only handle foreign currency to/from base currency exchange
    """

    def __init__(self):
        _CurrencyTable.__init__(self)

    def _to_base_cash(self, cur, value):
        rate = self.get_cash_buy(cur)
        if np.isnan(rate) or rate is None:
            print("[OOPS]   {} to {} conversion by CASH is not available yet!".format(cur, self._BASE))
        else:
            return value * rate

    def _from_base_cash(self, cur, value):
        rate = self.get_cash_sell(cur)
        if np.isnan(rate) or rate is None:
            print("[OOPS]   {} to {} conversion by CASH is not available yet!".format(self._BASE, cur))
        else:
            return value / rate

    def _to_base_spot(self, cur, value):
        rate = self.get_spot_buy(cur)
        if np.isnan(rate) or rate is None:
            print("[OOPS]   {} to {} conversion by SPOT is not available yet!".format(cur, self._BASE))
        else:
            return value * rate

    def _from_base_spot(self, cur, value):
        rate = self.get_spot_sell(cur)
        if np.isnan(rate) or rate is None:
            print("[OOPS]   {} to {} conversion by SPOT is not available yet!".format(self._BASE, cur))
        else:
            return value / rate


class CurrencyConverter(_SimpleConverter):
    """ Main converter """

    def __init__(self):
        _SimpleConverter.__init__(self)

    def _to_base(self, value, from_cur, from_type):
        if from_type == self._CASH:
            return self._to_base_cash(from_cur, value)
        elif from_type == self._SPOT:
            return self._to_base_spot(from_cur, value)

    def _from_base(self, value, to_cur, to_type):
        if to_type == self._CASH:
            return self._from_base_cash(to_cur, value)
        elif to_type == self._SPOT:
            return self._from_base_spot(to_cur, value)

    def convert(self, value, from_cur, from_type, to_cur, to_type):
        """ 
        Check for input regularity, then handle top-level currency exchange query
        Checking is deployed to all the inputs, so multiple can be captured
        Conditions to verify: 
            1. are source and destination currencies are both base currencies?
            2. are input currencies identical?
            3. are input exchange types available? 
            4. are input currencies available?
            5. is input value valid?
        """
        # Initialize flags that check whether conditions have met
        is_value_valid = is_not_ntd = is_not_identical = is_type_valid = is_currency_valid = True

        # Regularize inputs' case
        from_cur = from_cur.upper()
        to_cur = to_cur.upper()
        from_type = from_type.lower()
        to_type = to_type.lower()

        # Check if input value valid
        if isinstance(value, (int, float)) is False:
            is_value_valid = False
            print("[ERROR]  Irregular value!")

        # Check if source and destination currencies are both base currencies
        if from_cur == to_cur == 'NTD':
            is_not_ntd = False
            print("[WHAT?]  NTD TO NTD IS NO NEED FOR EXCHANGE!")

        # Check if input currencies and exchange types are identical
        if from_cur == to_cur and from_type == to_type:
            is_not_identical = False
            print("[INFO]   Identical currency no need for exchange")

        # Check if input exchange types available
        if not (from_type in self._ex_types) and (to_type in self._ex_types):
            is_type_valid = False
            print("[ERROR]  Irregular exchange type!\n"
                  "         Supported exchange type are {{{0}, {1}}}.format(self._CASH, self._SPOT)")

        # Check if input currencies available
        if from_cur not in self._cur_list or to_cur not in self._cur_list:
            is_currency_valid = False
            # This one should be consistent with the command CLI.py
            print("[ERROR]  Unsupported currency!\n"
                  "Use 'cvtwd info' or 'cvtwd lookup' to check for available currencies")

        # If all the conditions have met, then do the exchange job
        if all([is_not_ntd, is_not_identical, is_type_valid, is_currency_valid, is_value_valid]) is True:
            if from_cur == self._BASE:
                result = self._from_base(value, to_cur, to_type)
            elif to_cur == self._BASE:
                result = self._to_base(value, from_cur, from_type)
            else:
                mid_result = self._to_base(value, from_cur, from_type)
                result = self._from_base(mid_result, to_cur, to_type)

            # Print exchange result
            if result is not None:
                print_format = {"value": value,
                                "from_cur": from_cur,
                                "from_type": from_type,
                                "result": result,
                                "to_cur": to_cur,
                                "to_type": to_type}
                print("[RESULT] {f[value]} {f[from_cur]}({f[from_type]}) = *{f[result]}* {f[to_cur]}({f[to_type]})"
                      .format(f=print_format))


if __name__ == '__main__':
    """ TEST COMMANDS """
    file = '../exchange-rate-tables/ExchangeRate@201806011602.csv'
    cvt = CurrencyConverter()
    cvt.load_data(file)

    print(cvt.get_cash_buy('HKD'))
    print(cvt.get_spot_sell('USD'))
    cvt.show_rates('VND', 'EUR')
    cvt.show_rates('fef', 'JPY')
    cvt.convert(1, 'NTD', 'a', 'NTD', 'spot')
    cvt.convert(2, 'EUR', 'cash', 'fe', 'se')
    cvt.convert(323, 'NTD', 'cash', 'VND', 'spot')
    cvt.convert(323, 'ZAR', 'cash', 'VND', 'spot')
    cvt.convert(333, 'USD', 'cash', 'JPY', 'spot')
    cvt.convert(333, 'USD', 'cash', 'NTD', 'spot')
    cvt.show_all_rates()
    cvt.show_currency_descriptions()
