def integer_sequence(limit):
    current = 1
    while current < limit:
        yield current
        current += 1
