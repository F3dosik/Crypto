import string
from collections import Counter

ALPHABET = string.ascii_uppercase


def preprocess(text):
    return ''.join(filter(str.isalpha, text.upper()))


def index_of_coincidence(text):
    N = len(text)
    freqs = Counter(text)
    ic = sum(f * (f - 1) for f in freqs.values()) / (N * (N - 1)) if N > 1 else 0
    return ic


def estimate_key_length(ciphertext, max_key_length=20):
    avg_ics = []
    for key_len in range(1, max_key_length + 1):
        ic_sum = 0
        for i in range(key_len):
            substring = ciphertext[i::key_len]
            ic_sum += index_of_coincidence(substring)
        avg_ics.append(ic_sum / key_len)
    best_guess = avg_ics.index(max(avg_ics)) + 1
    return best_guess


def caesar_decrypt(text, shift):
    return ''.join(ALPHABET[(ALPHABET.index(c) - shift) % 26] for c in text)


def frequency_analysis(text):
    freqs = Counter(text)
    most_common_letter = freqs.most_common(1)[0][0]
    # Предположим, что самая частая буква в английском — E (индекс 4)
    return (ALPHABET.index(most_common_letter) - ALPHABET.index('E')) % 26


def find_vigenere_key(ciphertext, key_len):
    key = ''
    for i in range(key_len):
        group = ciphertext[i::key_len]
        shift = frequency_analysis(group)
        key += ALPHABET[shift]
    return key


def decrypt_vigenere(ciphertext, key):
    plaintext = ''
    key_indices = [ALPHABET.index(k) for k in key]
    for i, char in enumerate(ciphertext):
        shift = key_indices[i % len(key)]
        plaintext += ALPHABET[(ALPHABET.index(char) - shift) % 26]
    return plaintext


# === Пример использования ===

ciphertext = """
LXFOPVEFRNHR
""".strip()

ciphertext = preprocess(ciphertext)

key_len = estimate_key_length(ciphertext)
print(f"[+] Предполагаемая длина ключа: {key_len}")

key = find_vigenere_key(ciphertext, key_len)
print(f"[+] Предполагаемый ключ: {key}")

plaintext = decrypt_vigenere(ciphertext, key)
print(f"[+] Расшифрованный текст: {plaintext}")
