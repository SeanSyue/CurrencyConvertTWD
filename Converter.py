import pandas
import numpy as np
import sys

# sys.tracebacklimit=0  # Suppress traceback
sys.stderr = object  # Suppress error message


class _CurrencyTable:
    def __init__(self, file_):
        self._base = 'NTD'
        self._cash = 'cash'
        self._spot = 'spot'
        self._cash_buy = 'Cash.Buy'
        self._cash_sell = 'Cash.Sell'
        self._spot_buy = 'Spot.Buy'
        self._spot_sell = 'Spot.Sell'
        self._ex_col_names = [self._cash_buy, self._cash_sell, self._spot_buy, self._spot_sell]

        self._info_dict = {'USD': '0', 'HKD': '1', 'GBP': '2', 'AUD': '3', 'CAD': '4', 'SGD': '5', 'CHF': '6',
                           'JPY': '7',
                           'ZAR': '8', 'SEK': '9', 'NZD': '10', 'THB': '11', 'PHP': '12', 'IDR': '13', 'EUR': '14',
                           'KRW': '15', 'VND': '16', 'MYR': '17', 'CNY': '18'}

        self._df = pandas.read_csv(file_, index_col=False,
                                   usecols=['Currency', 'Cash', 'Spot', 'Cash.1', 'Spot.1']) \
            .replace({'0': np.nan, 0: np.nan}) \
            .rename(index=str, columns={"Cash": self._cash_buy, "Spot": self._spot_buy,
                                        "Cash.1": self._cash_sell, "Spot.1": self._spot_sell}) \
            .set_index(['Currency'])
        self._df['Description'] = self._df.index.map(self._info_dict)

        self._cur_list = [cur_name for cur_name in self._df.index.values] + [self._base]
        self._ex_types = {self._cash, self._spot}

    def get_cash_buy(self, cur):
        return self._df.loc[cur, self._cash_buy]

    def get_cash_sell(self, cur):
        return self._df.loc[cur, self._cash_sell]

    def get_spot_buy(self, cur):
        return self._df.loc[cur, self._spot_buy]

    def get_spot_sell(self, cur):
        return self._df.loc[cur, self._spot_sell]

    def show_rates(self, *cur):
        print(self._df.reindex(cur).loc[:, self._ex_col_names])

    def list_currencies(self):
        print(self._df.loc[:, ['Description']])
        print("base: {}".format(self._base))

    def show_currency_table(self):
        print(self._df)


class _SimpleConverter(_CurrencyTable):
    def __init__(self, file_):
        _CurrencyTable.__init__(self, file_)

    def _to_base_cash(self, cur, value):
        try:
            rate = self.get_cash_buy(cur)
            if np.isnan(rate) or rate is None:
                raise TypeError
            else:
                return value * rate
        except TypeError:
            print("[ERROR] {} to {} conversion by cash is not available yet!".format(cur, self._base))
            raise

    def _from_base_cash(self, cur, value):
        try:
            rate = self.get_cash_sell(cur)
            if np.isnan(rate) or rate is None:
                raise TypeError
            else:
                return value / rate
        except TypeError:
            print("[ERROR] {} to {} conversion by cash is not available yet!".format(self._base, cur))
            raise

    def _to_base_spot(self, cur, value):
        try:
            rate = self.get_spot_buy(cur)
            if np.isnan(rate) or rate is None:
                raise TypeError
            else:
                return value * rate
        except TypeError:
            print("[ERROR] {} to {} conversion by spot is not available yet!".format(cur, self._base))
            raise

    def _from_base_spot(self, cur, value):
        try:
            rate = self.get_spot_sell(cur)
            if np.isnan(rate) or rate is None:
                raise TypeError
            else:
                return value / rate
        except TypeError:
            print("[ERROR] {} to {} conversion by spot is not available yet!".format(self._base, cur))
            raise


class CurrencyConverter(_SimpleConverter):
    def __init__(self, file_):
        _SimpleConverter.__init__(self, file_)

    def _to_base(self, value, from_cur, from_type):
        if from_type == self._cash:
            return self._to_base_cash(from_cur, value)
        elif from_type == self._spot:
            return self._to_base_spot(from_cur, value)

    def _from_base(self, value, to_cur, to_type):
        if to_type == self._cash:
            return self._from_base_cash(to_cur, value)
        elif to_type == self._spot:
            return self._from_base_spot(to_cur, value)

    def convert(self, value, from_cur, from_type, to_cur, to_type):
        if from_type not in self._ex_types or to_type not in self._ex_types:
            print("[ERROR] Irregular exchange type!")
        elif from_cur not in self._cur_list or to_cur not in self._cur_list:
            print("[ERROR] Unsupported currency!")
        elif from_cur == to_cur and from_type == to_type:
            print("[INFO] Identical currency no need for exchange")
        elif from_cur == to_cur == 'NTD':
            print("[NTD-T0-NTD] ARE YOU KIDDING ME?")

        elif from_cur == self._base:
            print(self._from_base(value, to_cur, to_type))
        elif to_cur == self._base:
            print(self._to_base(value, from_cur, from_type))
        else:
            mid_result = self._to_base(value, from_cur, from_type)
            print(self._from_base(mid_result, to_cur, to_type))


if __name__ == '__main__':
    file = 'ExchangeRate@201805301602.csv'
    cvt = CurrencyConverter(file)
    # print(cvt.get_cash_buy('HKD'))
    # cvt.list_currencies()
    # cvt.convert(1, 'USD', 'spot', 'VND', 'spot')
    # cvt.show_currency_table()
    # print(cvt.get_spot_sell('USD'))
    cvt.show_rates('VND')
