# CurrencyConvertTWD
Look up currency exchange rates and calculate currency exchange values.
Currency rates based on [Bank of Taiwan](http://rate.bot.com.tw/xrt?Lang=en-US).

## Installation
1. clone this repo: `git clone https://github.com/SeanSyue/CurrencyConvertTWD`
2. install this program: `pip install .`

## Example
Examples can be found in [Example_commands.ipynb](https://github.com/SeanSyue/CurrencyConvertTWD/blob/master/Example_commands.ipynb).

## New feature
A standalone retrieval for last timestamp of the latest table

# TODO
- [X] Retrieve the timestamp of the lastest table 
- [ ] Retrieve the timestamp of the lastest table for each operation
- [ ] Clean up previous tables after updating
- [ ] Unit & intergrated testing
- [ ] Logging
- [ ] CLI with [`fire`](https://github.com/google/python-fire)
- [ ] Improved documentation
- [ ] CI support