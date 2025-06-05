from collections import Counter
import math

from Statistic import load_json, keep_russian_letters, load_text, symbol_stats
from pathlib import Path
from math import gcd
from functools import reduce

rus = [' ', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
       'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']


def vigenere(plaintext, key, mode="encrypt"):
    plaintext = keep_russian_letters(plaintext)
    key = keep_russian_letters(key)
    res = ''
    key_ind = 0

    if mode == "encrypt":  # Шифрование
        shift_func = lambda p, k: (rus.index(p) + rus.index(k)) % 33
    elif mode == "decrypt":  # Дешифрование
        shift_func = lambda p, k: (rus.index(p) - rus.index(k)) % 33

    for i in range(len(plaintext)):
        p = plaintext[i]
        k = key[key_ind]
        res += rus[shift_func(p, k)]
        key_ind = (key_ind + 1) % len(key)

    return res


data = load_json(Path('statistic_symbols.json'))['stats']
total = load_json(Path('statistic_symbols.json'))['total_symbols']



def ref_c_i(stats):
    ind = 0
    for symbol in stats.values():
        ind += (symbol['percent']) ** 2
    return ind



def c_i(stats):
    total = stats['total_symbols']
    stats = stats['stats']
    ind = 0
    for symbol in stats.values():
        ind += (symbol['count'] * (symbol['count'] - 1)) / (total * (total - 1))
    return ind
# print(c_i(data))
# print(c_ii(data))


reference_ind = c_i(data)


def decrypt(text):
    text_stat = symbol_stats(text)['stats']
    min_dist = float('inf')
    candidate = 0
    for length in range(3, min(len(text), 10)):
        column = text[::length]
        stats = symbol_stats(column)['stats']
        ind = c_i(stats)
        print(ind)
        if abs(ind - reference_ind) < min_dist:
            min_dist = abs(ind - reference_ind)
            candidate = length
    return candidate




# def find_repeats(text):
#     distances = set()
#     seen = set()
#     for length in range(3, 4):
#         for i in range(len(text) - length + 1):
#             subtext = text[i:i + length]
#             if subtext in seen:
#                 continue
#             seen.add(subtext)
#             positions = []
#             start = 0
#             while True:
#                 pos = text.find(subtext, start)
#                 if pos == -1:
#                     break
#                 positions.append(pos)
#                 start = pos + 1
#             # Теперь для каждой подстроки считаем расстояния между соседними позициями
#             for j in range(1, len(positions)):
#                 distances.add(positions[j] - positions[j - 1])
#     return distances
#
#
# def get_common_divisor(distances):
#     divisors = []
#     for d in distances:
#         if d < 2:
#             continue
#         # Собираем все делители d
#         for i in range(2, int(math.sqrt(d)) + 1):
#             if d % i == 0:
#                 divisors.append(i)
#                 if i != d // i:
#                     divisors.append(d // i)
#     if not divisors:
#         return None
#     # Возвращаем самый частый делитель
#     return Counter(divisors).most_common(1)[0][0]


plaintext = """Он до того струсил, увидав Шатова, что тотчас же захлопнул форточку и убежал на кровать. Шатов стал неистово стучать и кричать.
   - Как вы смеете так стучать среди ночи? - грозно, но замирая от страху, крикнул Лямшин, по крайней мере минуты через две решившись отворить снова форточку и убедившись, наконец, что Шатов пришел один.
   - Вот вам револьвер; берите обратно, давайте пятнадцать рублей.
   - Что это, вы пьяны? Это разбой; я только простужусь. Постойте, я сейчас плед накину.
   - Сейчас давайте пятнадцать рублей. Если не дадите, буду стучать и кричать до зари; я у вас раму выбью.
   - А я закричу караул, и вас в каталажку возьмут.
   - А я немой, что ли? Я не закричу караул? Кому бояться караула, вам или мне?"""
p = """СЪСШ ЩГЖИСЮБЩЫРО ФЧ РЛЫОУУПЦЛЫ ЦЙУБЭЫФСЮДЯ ЛКЧААЮЦЩДХИЯ Б ХЙЕУЖ ШЩ ЧЙХК ЯПУЩА УОРЧЙ ЧЬЩ ЬЙЬЩУЙЙЧ Е ПЛЖЮС ЧАХОИ ЩЦ ЛЩДФСНБЮСЛ Щ ЙККЦЖЦЛЩ ЭЙСНШТ ЩЧЫОВХЮДИ ЗЗН ЛЪЯД ЛЕЖОН ЕЮЧЪЛМСРТЖЦЬВЖ ЛГСЗЙЬЧШ НФЧЗ ЧЮАЮЕ ЛЖЙКУАХЙНАИЕЬВ ЙЦЛ ККФЩУЮИЙЧ З ЬЦСЙВГЫХ СОЗЖЪНШШО ЛЪЯД ЦСЗНКЕШЛГЫХ ЦЩЗШО ЦСПЛЛТП С ЧАХЙВЩ ЮЙЦСЗХФС КЗСАХЦЩ СЙФФЗШО ЛЪЯД РЛЬНГЫХЪЖ ДПХЛЕЗ НФЧГХЛ ШЙ ШУЩ ЮОЕЛХЧУЛУ ЩКЯЙЛЩНКЫЭА ЕЧРЮЗЫГЧЖФЖ ЩЦ ЧРШЙЛЩМ ДЛВОЖЫРО КЙЯЛЫОЖЧЖФПШЙЪНХ ХЙЕЩЖ СЪСШ СЬЛРНГ ШПРТЗПЗН ЧЕЧУЦЖЪЕЩУС РЫСОНШЙ ЩЩТЖЛТЕЗ СЪСПХЛ СПРЬЛЕСЧШЙЪНХЩ ЪЙУЖЫЬЛ ЯЧВАЕЧИ ЩРЩТ ОЕФЖЫХЪЖ ДХЩЩЩХОВХЮДФ ЩРЩТ Щ ЗМУВ ЫЩГЕПЫЛЖПЯЛЩ Е ШУБЭЫЛЯЖ ЛЩДФСНБЮСЖ ШПБВЩ КЛЩА УОРЧЙ С ЛЪЯД Р ЮЯЙЭЩИЙЯЩ ЭЧНЛЯДФ ДЙРЧБЩЫРО ЫФЖ НЖЫФМ ЕРУЛКФТЕЗ У ЬЩУ ЧНШЙЪЖЧКИ ЧЩЫЙЕЧЗАФДЭСФ ЮЙНЭЩСЦТА З СЪСШ РГФПЛТ З ЙЪЬЛЕО ЛР ИОСЩХ АФЧЭЧ ЩЮЯОЧАИОЬШЙО ЦСЙМУБУХЬЛЖ ЪЩНЖЩСБЮСФ НЗНГЯХСЮАКУЛА ЬЙЧБМС Л ГЖФФШПШУБЕФФШЮЧФ ЛЪЬЮАЮСФ НИИ ДЛЯЧЫЛ ЙЩЪБЮСОЛЕЙЬШЙТ СЩЬЦЛ НЖЫФМ Е НФЧКУЩЕ КЙЧК ЮОЩФЦЧЧЩУЧ УБЬЦЩЛЪЩГЖЗО ЛЪЯ ЫГЯ ЭЙЕ ЧЙФПЯЙ ШУЩ ОЫЛР АЪВЛЕСЖР ЪЬЧАХ ЧААКШФЦЖЦГ НЖЫЖЕ ЕЧОЕЙПЬЛКЫП ЩЮЫФСЖЪЬЛТ С РЛЫОУУПЫФТГЦЩМ ЫОЖЧЖФПШЙЪНЩ УЦЩЪЙЧАСПРЛА ХСЦЛЕ ЛЛНЙЛ ЗЛЯХ ЛЪЯ ЦФЩЬКФУЮЧ ЕБЭ ЦФЩЬКФУЮЧ ЯШЙМЩЛЪЩГЖЗО СЩЬЦЛ ЯЙЫЩСАЗ ЩШЗ ЧНСППГЫХ УГЯ ЮОЛЖЪОСШЙ ХЬЛРЧЩФЯЙОЩЖ ЦФДУЧНСД ЦГ ЗЮОЫШЩЗ РРЙПФДХЕ ЛЪЯ ЧЧШЙМЩ ЧЗШГ ЕЙНФТЗ"""
ciphertext = vigenere(plaintext, "ВСПЛЕСК")
ps = "абааба"
# print(reference_ind)
# print(c_i(data))
# print(data)
print(reference_ind)
plaintext = keep_russian_letters(plaintext)
print(decrypt(plaintext))
