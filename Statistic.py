import sys, re
from pathlib import Path
import json
from scipy.spatial.distance import jensenshannon
import numpy as np

from collections import Counter


def get_bigrams(text):
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)]
    return Counter(bigrams).most_common()


def keep_russian_letters(text):
    text = text.lower()
    cleaned = ''.join(c for c in text if ('а' <= c <= 'я') or (c == " "))
    return re.sub(r'\s+', ' ', cleaned).strip()


def create_json(file_path):
    """Создает новый пустой JSON-файл."""
    data = {"total_symbols": 0,
            "stats": {}
            }
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Файл {file_path} создан.")


def load_json(path, log_mode=False) -> dict:
    """
    Загружает данные из JSON-файла.
    Если файл не существует, пуст или поврежден, создает новый файл или завершает программу.
    """

    if path.exists():
        if path.stat().st_size == 0:
            if log_mode:
                print("Файл пуст. Создаем новый JSON.")
            create_json(path)

        try:
            with path.open("r", encoding="utf-8") as file:
                if log_mode:
                    print("Файл успешно загружен.")
                return json.load(file)

        except json.JSONDecodeError:
            while True:
                answer = input("Файл поврежден. Хотите пересоздать statistic.json? [Y/N]: ").strip().lower()
                if answer in ('y', 'yes'):
                    create_json(path)
                    return {}
                elif answer in ('n', 'no'):
                    print("Программа завершена.")
                    sys.exit(1)
                else:
                    print("Некорректный ввод. Введите 'Y' или 'N'.")
    else:
        if log_mode:
            print("Файл statistic.json не существовал. Создан новый JSON.")
        create_json(path)
        return {}


def load_text(path) -> str:
    """
    Загружает текст из файла, оставляя только русские буквы и пробелы.
    Если файл пуст, возвращает пустую строку.
    """
    try:
        with path.open("r", encoding="utf-8") as file:
            content = file.read()
            if not content:  # Если файл пуст
                print("Файл пуст.")
                return ""
            return keep_russian_letters(content)
    except FileNotFoundError:
        print(f"Файл {path} не найден и будет создан. Программа завершена.")
        path.touch()
        sys.exit(1)
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}. Программа завершена.")
        sys.exit(1)


def update_json(path, data):
    """Сохраняет данные в JSON-файл."""
    try:
        with open(path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Данные успешно сохранены в файл {path}.")
    except Exception as e:
        print(f"Ошибка при записи в {path}: {e}")


def symbol_stats(text, data=None):
    if data is None:
        data = {"total_symbols": 0, "stats": {}}

    text = keep_russian_letters(text)

    for letter in text:
        data["total_symbols"] += 1
        if letter not in data["stats"]:
            data["stats"][letter] = {}
            data["stats"][letter]["count"] = 1
        else:
            data["stats"][letter]["count"] += 1

    for letter in data["stats"]:
        data["stats"][letter]["percent"] = round((data["stats"][letter]["count"] / data['total_symbols']) * 100, 3)

    sorted_stats = dict(sorted(data['stats'].items(), key=lambda item: item[1]['count'], reverse=True))
    data['stats'] = sorted_stats
    return data


# def extract_distribution(data) -> list:
#     """
#     Извлекает список частот символов из структуры распределения.
#     """
#     stats = data["stats"]
#     # Сортируем символы по алфавиту для согласованности
#     sorted_symbols = sorted(stats.keys())
#     distribution = [stats[symbol]["count"] for symbol in sorted_symbols]
#     return distribution


def compare_distributions_JS(reference_data, candidate_data) -> float:
    """
    Сравнивает два распределения с помощью расстояния Йенсена-Шеннона.
    """
    sort_reference_data, sort_candidate_data = align_distributions(reference_data, candidate_data)

    reference_counts = [sort_reference_data['stats'][letter]['count'] for letter in sort_reference_data['stats'].keys()]
    candidate_counts = [sort_candidate_data['stats'][letter]['count'] for letter in sort_candidate_data['stats'].keys()]

    reference_dist = np.array(reference_counts)
    candidate_dist = np.array(candidate_counts)

    # Преобразуем абсолютные частоты в вероятности
    reference_probs = reference_dist / np.sum(reference_dist)
    candidate_probs = candidate_dist / np.sum(candidate_dist)

    print(candidate_probs)

    return jensenshannon(reference_probs, candidate_probs)


def align_distributions(reference, candidate) -> tuple[dict, dict]:
    """
    Выравнивает два распределения, добавляя отсутствующие символы с нулевой частотой.
    """
    reference_symbols = set(reference['stats'].keys())
    candidate_symbols = set(candidate['stats'].keys())

    # Добавляем отсутствующие символы в кандидата
    for symbol in reference_symbols - candidate_symbols:
        candidate['stats'][symbol] = {"count": 0, "percent": 0}

    # Сортируем символы по алфавиту
    sorted_reference_stats = dict(sorted(reference['stats'].items(), key=lambda item: item[0]))
    sorted_candidate_stats = dict(sorted(candidate['stats'].items(), key=lambda item: item[0]))
    reference['stats'] = sorted_reference_stats
    candidate['stats'] = sorted_candidate_stats
    return reference, candidate


def collect_statistic():
    """Вычисляет ряд распределения символов."""
    stat_path = Path("statistic.json")
    text_path = Path("text.txt")
    data = load_json(stat_path)
    text = load_text(text_path)

    print("Происходит сбор статистики...")
    symbol_stats(text, data)
    update_json(stat_path, data)


if __name__ == "__main__":
    text = " Привет,  как у тея дела - малыш   "
    print(keep_russian_letters(text))
