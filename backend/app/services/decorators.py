from flask import jsonify
from flask_jwt_extended import get_jwt


def has_roles(allowed_roles):
    """
    Декоратор, который проверяет, что аргументы функции находятся в списке разрешенных значений.
    :param allowed_roles: Список разрешенных значений.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            user_roles = get_jwt()['role']
            # Проверяем все позиционные аргументы
            result = False
            for role in allowed_roles:
                if role in user_roles:
                    result = True
                    break

            if  not result:
                return jsonify({"message": "Доступ запрещен!"}), 403

            # Если все аргументы в порядке, вызываем исходную функцию
            return func(*args, **kwargs)

        # Генерация уникального имени endpoint
        wrapper.__name__ = f"{func.__name__}_{id(func)}"
        return wrapper

    return decorator