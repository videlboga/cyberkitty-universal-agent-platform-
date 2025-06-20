def add(a, b):
    """Сложение двух чисел"""
    return a + b

def subtract(a, b):
    """Вычитание двух чисел"""
    return a - b

def multiply(a, b):
    """Умножение двух чисел"""
    return a * b

def divide(a, b):
    """Деление двух чисел с проверкой на ноль"""
    if b != 0:
        return a / b
    else:
        raise ValueError("Division by zero is not allowed")

def main():
    """Основная функция программы"""
    print("🧮 Калькулятор готов к работе!")
    print("Доступные операции: сложение, вычитание, умножение, деление")
    
    # Примеры использования
    print(f"\n📊 Примеры вычислений:")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")
    print(f"6 * 7 = {multiply(6, 7)}")
    print(f"15 / 3 = {divide(15, 3)}")
    
    # Интерактивный режим
    print(f"\n🎯 Интерактивный режим:")
    try:
        a = float(input("Введите первое число: "))
        operation = input("Введите операцию (+, -, *, /): ")
        b = float(input("Введите второе число: "))
        
        if operation == '+':
            result = add(a, b)
        elif operation == '-':
            result = subtract(a, b)
        elif operation == '*':
            result = multiply(a, b)
        elif operation == '/':
            result = divide(a, b)
        else:
            result = "Неизвестная операция"
        
        print(f"Результат: {a} {operation} {b} = {result}")
        
    except ValueError:
        print("Ошибка: введите корректные числа")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()