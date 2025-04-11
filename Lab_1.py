import string, heapq
from pathlib import Path

from Statistic import keep_russian_letters, load_json, symbol_stats, extract_distribution, align_distributions, \
    compare_distributions_JS

rus = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
       'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', ' ', 'я']
eng = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
       'w', 'x', 'y', 'z', ' ']


# Алгоритм Евклида
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


# Расширенный алгоритм Евклида
def gcdex(a, b):
    if a == 0:
        return (b, 0, 1)
    d, x1, y1 = gcdex(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return (d, x, y)


def find_best_key(reference_data, candidate_data):
    """
    Находит ключ, который дает распределение, наиболее близкое к эталонному.
    """
    reference_distribution = [reference_data['stats'][letter]["count"] for letter in reference_data['stats'].keys()]

    best_key = None
    min_distance = float('inf')

    for key, candidate_distribution in candidate_data.items():
        candidate_distribution = extract_distribution(candidate_distribution)

        # Выбираем метод сравнения (например, Йенсена-Шеннона)
        distance = compare_distributions_JS(reference_distribution, candidate_distribution)

        if distance < min_distance:
            min_distance = distance
            best_key = key

    return best_key, min_distance

# Шифр Цезаря
def encrypt_caesar(text, k, abc=None, info: bool = False):
    if abc is None:
        abc = rus
    text = keep_russian_letters(text)
    n = len(abc)

    if info:
        for s in abc:
            print(f"{abc.index(s)} {s} -> {(abc.index(s) + k) % n} {abc[(abc.index(s) + k) % n]}")

    res = ''.join(abc[(abc.index(char) + k) % n] for char in text)
    return res


# Расшифрование шифра Цезаря
def decrypt_caesar(text, k, abc=None):
    if abc is None:
        abc = rus
    return encrypt_caesar(text, -k, abc)


# Дешифрование шифра Цезаря
def hacking_caesar(text, abc=None):
    if abc is None:
        abc = rus

    n = len(abc)

    reference_stats = load_json(Path('statistic.json'))
    ciphertext_stats = symbol_stats(text)

    candidates = {}

    for i in range(5):
        for j in range(5):
            cand_symbol = list(reference_stats['stats'].items())[i][0]
            cand_symbol_ind = abc.index(cand_symbol)

            ref_symbol = list(ciphertext_stats['stats'].items())[j][0]
            ref_symbol_ind = abc.index(ref_symbol)

            k = (ref_symbol_ind - cand_symbol_ind) % n

            candidate_stats = {"total_symbols": ciphertext_stats['total_symbols'], "stats": {}}
            # Меняем ряд распределения текста по ключу
            for letter in ciphertext_stats['stats']:
                candidate_stats['stats'][abc[(abc.index(letter) - k) % n]] = ciphertext_stats['stats'][letter]

            align_distributions(reference_stats, candidate_stats)

            candidates[k] = candidate_stats
    for k, candidate in candidates.items():



def encrypt_affine(text: str, a: int, b: int, abc=None, info: bool = False):
    if abc is None:
        abc = rus
    n = len(abc)
    while gcd(a, n) != 1:
        coprimes = [i for i in range(1, n) if gcd(i, n) == 1]
        print(
            "Ошибка! Коэффициент a должен быть взаимнопрост с мощностью алфавита.\nВыберите новый коэффициент из предложенных: ")
        a = int(input(f"{coprimes}\n"))
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator).lower()
    if info:
        print(f"Шифрование y = ax + b, где a = {a}, b = {b}.")
        for s in abc:
            print(f"{abc.index(s)} {s} -> {(abc.index(s) * a + b) % n} {abc[(abc.index(s) * a + b) % n]}")
    res = ''.join(abc[(abc.index(char) * a + b) % n] for char in text)
    return res


def decrypt_affine(text: str, a: int, b: int, abc=None):
    if abc is None:
        abc = rus
    n = len(abc)
    while gcd(a, n) != 1:
        coprimes = [i for i in range(1, n) if gcd(i, n) == 1]
        print(
            "Ошибка! Коэффициент a должен быть взаимнопрост с мощностью алфавита.\nВыберите новый коэффициент из предложенных: ")
        a = int(input(f"{coprimes}\n"))
    ar = (gcdex(a, n)[1]) % n
    res = ''.join(abc[((abc.index(char) - b) * ar) % n] for char in text)
    return res


def hacking_affine(text: str, abc=None):
    if abc is None:
        abc = rus
    n = len(abc)
    x1 = abc.index(" ")  # first_ind
    if abc == rus:
        x2 = abc.index("о")
    else:
        x2 = abc.index("e")  # second_ind
    chars = char_distr(text, 2)
    y1 = abc.index(chars[0][0])  # new_first_ind
    y2 = abc.index(chars[1][0])  # new_second_ind
    a = ((y2 - y1) * gcdex(((x2 - x1) % n), n)[1]) % n
    b = (y1 - x1 * a) % n
    print(a, b)
    return decrypt_affine(text, a, b, abc)


def encrypt_replacement(text: str, abc: dict[str, str]):
    res = ""
    for symb in text:
        res += abc[symb]
    return res


hacking_caesar("Привет мир")

# abc_replace = {'а': 'б', 'б':'в', 'в':'г', 'г':'д', 'д':'е', 'е':'а'}
# print(encrypt_replacement("абвгде", abc_replace))
#
# texteng = "The sun rises over the ocean waves bringing light warmth and hope for a new day full of endless possibilities"
# textrus = "Это пример текста, который содержит ровно сто символов без учета знаков препинания."
#
# enc = encrypt_affine(textrus, 4, 2, rus, True)
# print(decrypt_affine(enc, 4, 2))
# print(hacking_affine(enc))


# while True:
#     encrypt_type = input(
#         "Выберите способ шифрования: \n1 - Шифр Цезаря;\n2 - Афинный шифр;\n3 - Общий случай.\nВведите число (1-3): ")
#     if encrypt_type.isdigit():
#         if int(encrypt_type) >= 1 and int(encrypt_type) <= 3:
#             break
#     print("Ошибка ввода!")
#     encrypt_type = input(
#         "Выберите способ шифрования: \n1 - Шифр Цезаря;\n2 - Афинный шифр;\n3 - Общий случай.\nВведите число (1-3): ")
#
# text = ''
#
# while True:
#     q1 = input(
#         "Выберите способ задния текста:\n1 - Ввести с клавиатуры;\n2 - Выбрать тестовый текст.\nВведите число (1-2): ")
#     if q1.isdigit():
#         if int(q1) >= 1 and int(q1) <= 3:
#             break
#     print("Ошибка ввода!")
#     q1 = input(
#         "Выберите способ задния текста:\n1 - Ввести с клавиатуры;\n2 - Выбрать тестовый текст.\nВведите число (1-2): ")
# lang = rus
# if q1 == '1':
#     while True:
#         lang = input("Выберите язык алфавита:\n1 - Русский;\n2 - Английский.\nВведите число (1-2): ")
#         if lang.isdigit():
#             if int(lang) >= 1 and int(lang) <= 2:
#                 break
#         print("Ошибка ввода!")
#         lang = input("Выберите язык алфавита:\n1 - Русский;\n2 - Английский.\nВведите число (1-2): ")
#     if lang == "1":
#         lang = rus
#     elif lang == '2':
#         lang = eng
#     text = input("Введите текст для шифрования:\n")
#
#
# elif q1 == '2':
#     text = "Это пример текста, который содержит ровно сто символов без учета знаков препинания."
#
# if encrypt_type == '1':
#     k = int(input("Введите число сдвига: "))
#     text = encrypt_caesar(text, k, lang)
#     print(decrypt_caesar(text, lang))
