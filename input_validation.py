import re

def validate_input(num):
    if not isinstance(num, int):
        raise ValueError('Пожалуйста, введите целое число')
    if num < 0:
        raise ValueError('Пожалуйста, введите неотрицательное число')
    return num