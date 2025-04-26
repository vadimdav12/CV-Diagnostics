import re

def simple_preprocess(answers):
    # 1. Разбиваем
    chunks = re.split(r'RESULT \d+', answers)[1:]

    cleaned = []
    seen = set()
    for c in chunks:
        # 2. Очистка лишнего
        c = re.sub(r'©.*?v \d\.\d', '', c)
        c = re.sub(r'RAL ?\d{3,4}', '', c)
        c = ' '.join(c.split())  # убираем множественные пробелы
        # 3. Обрезка
        if len(c) > 800:
            c = c[:800] + '…'
        # 4. Дедупликация по хешу начала
        h = hash(c[:300])
        if h not in seen:
            seen.add(h)
            cleaned.append(c)

    return '\n\n'.join(cleaned)

# === Теперь сам код работы ===

# 1. Читаем answers.txt
with open('answer', 'r', encoding='utf-8') as f:
    answers = f.read()

# 2. Обрабатываем
processed_answers = simple_preprocess(answers)

# 3. Выводим результат (например, печать или запись в файл)
print(processed_answers)

# (опция) Можешь сохранить обратно в новый файл
with open('processed_answers.txt', 'w', encoding='utf-8') as f:
    f.write(processed_answers)
