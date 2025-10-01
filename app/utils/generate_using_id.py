import random
import string


def using_id(length=10):
    symbols = string.ascii_uppercase + string.digits
    return "".join(random.choice(symbols) for _ in range(length)) #noqa
