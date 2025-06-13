import math

def calculate_circle_area(radius):
    """Расчёт площади круга по формуле A = π * r²"""
    return math.pi * radius ** 2

def calculate_cat_area(length, width):
    """Приблизительный расчёт площади кота (как прямоугольника)"""
    return length * width

# Пример использования
if __name__ == "__main__":
    # Площадь круга
    radius = 5
    circle_area = calculate_circle_area(radius)
    print(f"Площадь круга с радиусом {radius} = {circle_area:.2f}")
    
    # Площадь кота (шуточный расчёт)
    cat_length = 0.5  # метры
    cat_width = 0.3   # метры
    cat_area = calculate_cat_area(cat_length, cat_width)
    print(f"Площадь кота {cat_length}x{cat_width}м = {cat_area:.2f} м²")
