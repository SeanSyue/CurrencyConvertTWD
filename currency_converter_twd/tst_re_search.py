import re


text = 'attachment; filename="ExchangeRate@201912181525.csv"'
# text = 'fake_content'
pattern = r'"(.*?)"'

table_name = re.search(pattern, text)
print(table_name)
print(type(table_name))
# table_name = re.search(pattern, text).group(1)
