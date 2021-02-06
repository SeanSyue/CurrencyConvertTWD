from filecmp import cmp
from pathlib import Path

p = Path('mock_tables')
files = [n for n in p.glob('*.csv')]
print(cmp(files[0], files[1]))

file_3 = Path('mock-download-root').joinpath('ExchangeRate@201912021600.csv')
print(cmp(files[0], file_3))
