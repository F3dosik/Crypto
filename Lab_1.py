# -*- coding: utf-8 -*-

import random
from pathlib import Path
from Statistic import keep_russian_letters, load_json, symbol_stats, compare_distributions_JS, bigram_stats

rus = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
       'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', ' ', 'я']
eng = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
       'w', 'x', 'y', 'z', ' ']


def shuffle_string(s):
    # Преобразуем строку в список символов (так как строки неизменяемы)
    chars = list(s)
    # Перемешиваем символы
    random.shuffle(chars)
    # Собираем обратно в строку
    return ''.join(chars)


def swap_two_random_chars(key):
    # Преобразуем строку в список символов (так как строки неизменяемы)
    # Выбираем два случайных индекса
    i, j = random.sample(range(len(key)), 2)
    # Меняем символы местами
    key[i], key[j] = key[j], key[i]
    # Собираем обратно в строку
    return key


def decrypt_ciphertext(ciphertext, key):
    ciphertext = keep_russian_letters(ciphertext)
    res = ''
    for i in range(len(ciphertext)):
        res += key[rus.index(ciphertext[i])]
    return res


def reverse_key(key):
    rev_key = 33 * ['']
    for i in range(len(key)):
        rev_key[rus.index(key[i])] = rus[i]
    return rev_key

def keys_matching(k1, k2):
    return sum(a == b for a, b in zip(k1, k2))

def hack_ciphertext_JS(ciphertext):
    # Инициализируем k случайным перемешиванием алфавита
    # shuffle_abc = rus[:]
    # random.shuffle(shuffle_abc)
    # key = shuffle_abc
    key = ['у', 'щ', 'р', 'и', ' ', 'ч', 'з', 'в', 'д', 'г', 'л', 'ы', 'ф', 'ь', 'э', 'т', 'о', 'ш', 'б', 'я', 'к', 'й',
           'м', 'е', 'с', 'ж', 'а', 'ъ', 'н', 'ц', 'ю', 'п', 'х']

    temp_decrypt = decrypt_ciphertext(ciphertext, key)

    temp_decrypt_data = symbol_stats(temp_decrypt)
    reference_data = load_json(Path("statistic_symbols.json"))

    distance = compare_distributions_JS(reference_data, temp_decrypt_data)

    key_stability = 0

    while key_stability != 10000:
        key_tmp = swap_two_random_chars(key)
        temp_decrypt = decrypt_ciphertext(ciphertext, key_tmp)
        temp_decrypt_data = symbol_stats(temp_decrypt)
        temp_distance = compare_distributions_JS(reference_data, temp_decrypt_data)
        if temp_distance < distance:
            distance = temp_distance
            key_stability = 0
            key = key_tmp
        elif temp_distance >= distance:
            key_stability += 1
        print(key)

    return key

# def hack_ciphertext_JS(ciphertext):
#     # Инициализируем k случайным перемешиванием алфавита
#     # shuffle_abc = rus[:]
#     # random.shuffle(shuffle_abc)
#     # key = shuffle_abc
#     key = ['у', 'щ', 'р', 'и', ' ', 'ч', 'з', 'в', 'д', 'г', 'л', 'ы', 'ф', 'ь', 'э', 'т', 'о', 'ш', 'б', 'я', 'к', 'й',
#            'м', 'е', 'с', 'ж', 'а', 'ъ', 'н', 'ц', 'ю', 'п', 'х']
#
#     temp_decrypt = decrypt_ciphertext(ciphertext, key)
#
#     ciphertext_mono_stats = symbol_stats(temp_decrypt)
#     ciphertext_bi_stats = bigram_stats(temp_decrypt)
#
#     reference_mono_stats = load_json(Path('statistic_symbols.json'))
#     reference_bi_stats = load_json(Path('statistic_bigrams.json'))
#
#     distance_JS_mono = compare_distributions_JS(reference_mono_stats, ciphertext_mono_stats)
#     distance_JS_bi = compare_distributions_JS(reference_bi_stats, ciphertext_bi_stats)
#
#     alpha = 1
#
#     total_distance = distance_JS_mono * alpha + distance_JS_bi * (1 - alpha)
#
#     key_stability = 0
#
#     while key_stability != 10000:
#         key_tmp = swap_two_random_chars(key)
#         temp_decrypt = decrypt_ciphertext(ciphertext, key_tmp)
#
#         ciphertext_mono_stats = symbol_stats(temp_decrypt)
#         ciphertext_bi_stats = bigram_stats(temp_decrypt)
#
#         distance_JS_mono = compare_distributions_JS(reference_mono_stats, ciphertext_mono_stats)
#         distance_JS_bi = compare_distributions_JS(reference_bi_stats, ciphertext_bi_stats)
#
#         temp_total_distance = distance_JS_mono * alpha + distance_JS_bi * (1 - alpha)
#         print(key_tmp)
#         print(temp_total_distance)
#
#         if temp_total_distance < total_distance:
#             total_distance = temp_total_distance
#             key_stability = 0
#             key = key_tmp
#         elif temp_total_distance >= total_distance:
#             key_stability += 1
#
#     print(total_distance)
#     return key


def hack_ciphertext_bigrams(ciphertext, key):
    ciphertext_mono = decrypt_ciphertext(ciphertext, key)

    ciphertext_mono_stats = symbol_stats(ciphertext_mono)
    ciphertext_bi_stats = bigram_stats(ciphertext_mono)

    reference_mono_stats = load_json(Path('statistic_symbols.json'))
    reference_bi_stats = load_json(Path('statistic_bigrams.json'))

    reference_stats_list = list(reference_bi_stats["stats"].items())

    distance_JS_mono = compare_distributions_JS(reference_mono_stats, ciphertext_mono_stats)
    distance_JS_bi = compare_distributions_JS(reference_bi_stats, ciphertext_bi_stats)

    alpha = 0.5

    total_distance = distance_JS_mono * alpha + distance_JS_bi * (1 - alpha)

    key_stability = 0

    while key_stability != 10000:
        key_tmp = swap_two_random_chars(key)
        temp_decrypt = decrypt_ciphertext(ciphertext, key_tmp)
        temp_decrypt_data = symbol_stats(temp_decrypt)
        temp_distance = compare_distributions_JS(reference_data, temp_decrypt_data)
        if temp_distance < distance:
            distance = temp_distance
            key_stability = 0
            key = key_tmp
        elif temp_distance >= distance:
            key_stability += 1
        print(key)

    for i in range(len(ciphertext_JS) - 1):
        bigram = ciphertext_JS[i:i + 2]
        min_diff = float('inf')
        candidate_bigram = ''
        for elem in reference_stats_list:
            temp_diff = abs(elem[1]['percent'] - temp_decrypt_data['stats'][elem]['percent'])
            if temp_diff > min_diff:
                break
            elif temp_diff < min_diff:
                min_diff = temp_diff
                candidate_bigram = elem[0]
        temp_key[key_list.index(bigram[0])] = candidate_bigram[0]
        temp_key[key_list.index(bigram[1])] = candidate_bigram[1]
        temp_decrypt = decrypt_ciphertext(ciphertext)


def hack(ciphertext):
    key = hack_ciphertext_JS(ciphertext)
    hack_ciphertext_bigrams(ciphertext, key)


key = ['у', 'щ', 'р', 'и', ' ', 'ч', 'з', 'в', 'д', 'г', 'л', 'ы', 'ф', 'ь', 'э', 'т', 'о', 'ш', 'б', 'я', 'к', 'й', 'м', 'е', 'с', 'ж', 'а', 'ъ', 'н', 'ц', 'ю', 'п', 'х']
rev_key = reverse_key(key)
plaintext = """ Убери все символы переноса строки
    Новое лицо это был молодой князь Андрей Болконский, муж маленькой княгини. Не столько по тому, что молодой князь приехал так поздно, но все-таки был принят хозяйкой самым любезным образом, сколько по тому, как он вошел в комнату, было видно, что он один из тех светских молодых людей, которые так избалованы светом, что даже презирают его. Молодой князь был небольшого роста, весьма красивый, сухощавый брюнет, с несколько истощенным видом, коричневым цветом лица, в чрезвычайно изящной одежде и с крошечными руками и ногами. Все в его фигуре, начиная от усталого, скучающего взгляда до ленивой и слабой походки, представляло самую резкую противоположность с его маленькою, оживленною женой. Ему, видимо, все бывшие в гостиной не только были знакомы, но уж надоели ему так, что и смотреть на них и слушать их ему было очень скучно, потому что он вперед знал все, что будет. Из всех же прискучивших ему лиц лицо его хорошенькой жены, казалось, больше всех ему надоело. С кислою, слабою гримасой, портившей его красивое лицо, он отвернулся от нее, как будто подумал: "Тебя только недоставало, чтобы вся эта компания совсем мне опротивела". Он поцеловал руку Анны Павловны с таким видом, как будто готов был бог знает что дать, чтоб избавиться от этой тяжелой обязанности, и щурясь, почти закрывая глаза и морщась, оглядывал все общество.
       -- У вас съезд, -- сказал он тоненьким голоском и кивнул головой кое-кому, кое-кому подставил свою руку, предоставляя ее пожатию.
       -- Вы собираетесь на войну, князь? -- сказала Анна Павловна.
       -- Генерал Кутузов, -- сказал он, ударяя на последнем слоге зов как француз, снимая перчатку с белейшей, крошечной руки и потирая ею глаза, -- генерал-аншеф Кутузов зовет меня к себе в адъютанты.
       -- А Лиза, ваша жена?
       -- Она поедет в деревню.
       -- Как вам не грех лишать нас вашей прелестной жены?
       Молодой адъютант сделал выпяченными губами презрительный звук, какой делают только французы, и ничего не отвечал.
       -- Андрей, -- сказала его жена, обращаясь к мужу тем же кокетливым тоном, каким она обращалась и к посторонним, -- подите сюда, садитесь, послушайте, какую историю рассказывает виконт о мадемуазель Жорж и Буонапарте.
       Андрей зажмурился и сел совсем в другую сторону, как будто не слышал жены.
       -- Продолжайте, виконт, -- сказала Анна Павловна. -- Виконт рассказывал, как герцог Энгиенский бывал у мадемуазель Жорж, -- прибавила она, обращаясь к вошедшему, чтобы он мог следить за продолжением рассказа.
       -- Мнимое соперничество Буонапарте и герцога из-за Жорж, -- сказал князь Андрей таким тоном, как будто смешно было кому-нибудь не знать про это, и повалился на ручку кресла. В это время молодой человек в очках, называемый мсье Пьер, со времени входа князя Андрея в гостиную не спускавший с него радостных, дружелюбных глаз, подошел к нему и взял его за руку. Князь Андрей так мало был любопытен, что, не оглядываясь, сморщил наперед лицо в гримасу, выражавшую досаду на того, кто трогает его, но, увидав улыбающееся лицо Пьера, улыбнулся тоже, и вдруг все лицо его преобразилось. Доброе и умное выражение вдруг явилось на нем.
       -- Как? Ты здесь, кавалергард мой милый? -- спросил князь радостно, но с покровительственным и надменным оттенком.
       -- Я знал, что вы будете, -- отвечал Пьер. -- Я приеду к вам ужинать, -- прибавил он тихо, чтобы не мешать виконту, который продолжал свой рассказ. -- Можно?
       -- Нет, нельзя, -- сказал князь Андрей, смеясь и отворачиваясь, но пожатием руки давая знать Пьеру, что этого не нужно было спрашивать.
       Виконт рассказал, как мадемуазель Жорж умоляла герцога спрятаться, как герцог сказал, что он никогда ни перед кем не прятался, как мадемуазель Жорж сказала ему: "Ваше высочество, ваша шпага принадлежит королю и Франции", -- и как герцог все-таки спрятался под белье в другой комнате, и как Наполеону сделалось дурно, и герцог вышел из-под белья и увидел перед собой Буонапарте.
       -- Прелестно, восхитительно! -- послышалось между слушателями.
       Даже Анна Павловна, заметив, что самое затруднительное место истории пройдено благополучно, и успокоившись, вполне могла наслаждаться рассказом. Виконт разгорелся и, грассируя, говорил с одушевлением актера...
       -- Враг его дома, похититель трона, тот, кто возглавлял его нацию, был здесь, перед ним, неподвижно распростертый на земле и, может быть, при последнем издыхании. Как говорил великий Корнель: "Злобная радость поднималась в его сердце, и только оскорбленное величие помогло ему не поддаться ей".
       Виконт остановился и, сбираясь повести еще сильнее свой рассказ, улыбнулся, как будто успокаивая дам, которые уже слишком были взволнованы. Совершенно неожиданно во время этой паузы красавица княжна Элен посмотрела на часы, переглянулась с отцом и вместе с ним встала, и этим движением расстроила кружок и прервала рассказ.
       -- Мы опоздаем, пап<, -- сказала она просто, продолжая сиять на всех своею улыбкой.
       -- Вы меня извините, мой милый виконт, -- обратился князь Василий к французу, ласково притягивая его за рукав вниз к стулу, чтобы он не вставал. -- Этот несчастный праздник у посланника лишает меня удовольствия и прерывает вас.
       -- Очень мне грустно покидать ваш восхитительный вечер, -- сказал он Анне Павловне.
       Дочь его, княжна Элен, слегка придерживая складки платья, пошла между стульев, и улыбка просияла еще светлее на ее прекрасном лице."""
d = decrypt_ciphertext(plaintext, key)
k = hack_ciphertext_JS(d)
print(decrypt_ciphertext(d, k))
print(k)
print(rev_key)
print(keys_matching(k, rev_key))



