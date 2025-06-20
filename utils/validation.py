import re

def validate_data(data):
    if not isinstance(data, dict):
        return False
    if 'message' not in data or not isinstance(data['message'], str):
        return False
    if 'chat_id' not in data or not isinstance(data['chat_id'], int):
        return False
    return True

# Пример использования
data = {'message': 'Hello, World!', 'chat_id': 12345}
print(validate_data(data))