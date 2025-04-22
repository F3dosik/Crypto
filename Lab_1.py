import string, heapq
from pathlib import Path

from Statistic import keep_russian_letters, load_json, symbol_stats, align_distributions, \
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

# Функция поиска лучшего ключа по заданным рядам распределения
def find_best_key(reference_data, candidate_data):
    """
    Находит ключ, который дает распределение, наиболее близкое к эталонному.
    """
    reference_distribution = [reference_data['stats'][letter]['count'] for letter in reference_data['stats'].keys()]

    best_key = None
    min_distance = float('inf')
    for key, candidate_distribution in candidate_data.items():
        candidate_distribution = [candidate_distribution['stats'][letter]['count'] for letter in
                                  candidate_distribution['stats'].keys()]
        # Выбираем метод сравнения (например, Йенсена-Шеннона)
        distance = compare_distributions_JS(reference_distribution, candidate_distribution)

        if distance < min_distance:
            min_distance = distance
            best_key = key

    return best_key, min_distance


# Шифр Цезаря
def encrypt_caesar(text, k, abc=None, info: bool = False):
    print(f'Открытый текст: {text}')

    if abc is None:
        abc = rus
    text = keep_russian_letters(text)
    n = len(abc)

    if info:
        for s in abc:
            print(f"{abc.index(s)} {s} -> {(abc.index(s) + k) % n} {abc[(abc.index(s) + k) % n]}")

    res = ''.join(abc[(abc.index(char) + k) % n] for char in text)
    if k > 0:
        print(f'Результат шифрования: {res}')
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

    reference_data = load_json(Path('statistic.json'))
    ciphertext_data = symbol_stats(text)

    candidates = {}

    reference_stats = list(reference_data['stats'].items())
    ciphertext_stats = list(ciphertext_data['stats'].items())
    for i in range(5):
        for j in range(5):
            cand_symbol = reference_stats[i][0]
            cand_symbol_ind = abc.index(cand_symbol)

            ref_symbol = ciphertext_stats[j][0]
            ref_symbol_ind = abc.index(ref_symbol)

            k = (ref_symbol_ind - cand_symbol_ind) % n

            candidate_data = {"total_symbols": ciphertext_data['total_symbols'], "stats": {}}
            candidate_stats = candidate_data['stats']
            # Меняем ряд распределения текста по ключу
            for letter in candidate_stats:
                candidate_stats[abc[(abc.index(letter) - k) % n]] = ciphertext_stats[letter]

            candidate_data['stats'] = candidate_stats

            # Добавляем отсутствующие символы в статистике
            align_distributions(reference_data, candidate_data)

            # candidates = dict: {key: int, stats: {letter: {count: int, percent: float}}}
            candidates[k] = candidate_data

    k, d = find_best_key(reference_data, candidates)
    print(f'Лучшим ключом сдвига является: k = {k} с расстоянием Йенсена-Шеннона d = {d}')
    print(f'Результат дешифрования: {encrypt_caesar(text, -k)}')

# Аффинный шифр
def encrypt_affine(text: str, a: int, b: int, abc=None, info: bool = False):
    print(f'Открытый текст: {text}')

    if abc is None:
        abc = rus

    n = len(abc)

    # Проверка взаимной простоты a и n
    while gcd(a, n) != 1:
        coprime_list = [i for i in range(1, n) if gcd(i, n) == 1]
        print(
            "Ошибка! Коэффициент a должен быть взаимнопрост с мощностью алфавита.\nВыберите новый коэффициент из предложенных: ")
        a = int(input(f"{coprime_list}\n"))

    # Убираем лишние символы
    text = keep_russian_letters(text)

    if info:
        print(f"Шифрование y = ax + b, где a = {a}, b = {b}.")
        for s in abc:
            print(f"{abc.index(s)} {s} -> {(abc.index(s) * a + b) % n} {abc[(abc.index(s) * a + b) % n]}")

    res = ''.join(abc[(abc.index(letter) * a + b) % n] for letter in text)
    print(f'Результат шифрования: {res}')
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
    # поиск обратного с помощью расширенного алгоритма Евклида
    ar = (gcdex(a, n)[1]) % n

    res = ''.join(abc[((abc.index(letter) - b) * ar) % n] for letter in text)

    return res


def hacking_affine(text: str, abc=None):
    if abc is None:
        abc = rus

    n = len(abc)

    reference_data = load_json(Path('statistic.json'))
    reference_stats = reference_data['stats']

    ciphertext_data = symbol_stats(text)
    ciphertext_stats = ciphertext_data['stats']


    for i in range(3):
        if i == 0:
            x1 = list(reference_data['stats'].items())[0][0]
            x1_ind = abc.index(x1)
            x2 = list(reference_data['stats'].items())[1][0]
            x2_ind = abc.index(x2)
        elif i == 1:
            x1 = list(reference_data['stats'].items())[0][0]
            x1_ind = abc.index(x1)
            x2 = list(reference_data['stats'].items())[2][0]
            x2_ind = abc.index(x2)
        elif i == 2:
            x1 = list(reference_data['stats'].items())[1][0]
            x1_ind = abc.index(x1)
            x2 = list(reference_data['stats'].items())[2][0]
            x2_ind = abc.index(x2)

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

# Проверка работоспособности дешифратора шифра Цезаря
# for k in range(33):
#     hacking_caesar(encrypt_caesar("Брехня! — уверенно опровергал широколицый красногвардеец. — Брехню вам всучивают. Я перед тем как из Ростова выйтить, в церкву ходил и причастие принимал.", k))
