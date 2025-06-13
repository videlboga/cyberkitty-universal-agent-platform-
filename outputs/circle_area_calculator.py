import math

def calculate_circle_area(radius):
    """Расчёт площади круга по формуле A = π * r²"""
    area = math.pi * radius ** 2
    return area

def main():
    print("🔵 Калькулятор площади круга")
    print("Формула: A = π * r²")
    
    try:
        radius = float(input("Введите радиус круга: "))
        if radius <= 0:
            print("❌ Радиус должен быть положительным числом")
            return
        
        area = calculate_circle_area(radius)
        print(f"📊 Площадь круга с радиусом {radius} = {area:.2f}")
        print(f"📐 π ≈ {math.pi:.6f}")
        
    except ValueError:
        print("❌ Пожалуйста, введите корректное число")

if __name__ == "__main__":
    main()
