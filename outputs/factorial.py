def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

if __name__ == '__main__':
    number = int(input('Введите число: '))
    print(f'Факториал числа {number} равен {factorial(number)}')