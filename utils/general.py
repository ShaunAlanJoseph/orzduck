from time import time
import random


def get_time():
    return int(time())


def generate_string(len: int):
    symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return "".join(random.choices(symbols, k=len))