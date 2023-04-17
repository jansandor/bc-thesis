NOTSET = '-'
MAN = 'M'
WOMAN = 'W'

# order in tuple is important because of accounts_filters.py sex_value filter
SEX_CHOICES = (
    (NOTSET, 'nechci uvést'),
    (MAN, 'muž'),
    (WOMAN, 'žena')
)
