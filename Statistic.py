import sys, re
from pathlib import Path
import json
from scipy.spatial.distance import jensenshannon
import numpy as np

from collections import Counter


# def get_bigrams(text):
#     bigrams = [text[i:i + 2] for i in range(len(text) - 1)]
#     return Counter(bigrams).most_common()


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
                answer = input("Файл поврежден. Хотите пересоздать statistic_symbols.json? [Y/N]: ").strip().lower()
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
            print("Файл statistic_symbols.json не существовал. Создан новый JSON.")
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


def bigram_stats(text, data=None):
    if data is None:
        data = {"total_bigrams": 0, "stats": {}}

    text = keep_russian_letters(text)

    for i in range(len(text) - 1):
        bigram = text[i:i + 2]
        data["total_bigrams"] += 1
        if bigram not in data["stats"]:
            data["stats"][bigram] = {"count": 1}
        else:
            data["stats"][bigram]["count"] += 1

    for bigram in data["stats"]:
        data["stats"][bigram]["percent"] = round(
            (data["stats"][bigram]["count"] / data["total_bigrams"]) * 100, 10)

    sorted_stats = dict(sorted(data["stats"].items(), key=lambda item: item[1]["count"], reverse=True))
    data["stats"] = sorted_stats
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

    return jensenshannon(reference_probs, candidate_probs)


# def compare_distributions_JS_bigram(reference_data, candidate_data) -> float:
#     """
#     Сравнивает два распределения с помощью расстояния Йенсена-Шеннона.
#     """
#     sort_reference_data, sort_candidate_data = align_distributions(reference_data, candidate_data)
#
#     reference_counts = [sort_reference_data['stats'][letter]['count'] for letter in sort_reference_data['stats'].keys()]
#     candidate_counts = [sort_candidate_data['stats'][letter]['count'] for letter in sort_candidate_data['stats'].keys()]
#
#     reference_dist = np.array(reference_counts)
#     candidate_dist = np.array(candidate_counts)
#
#     # Преобразуем абсолютные частоты в вероятности
#     reference_probs = reference_dist / np.sum(reference_dist)
#     candidate_probs = candidate_dist / np.sum(candidate_dist)
#
#     print(candidate_probs)
#
#     return jensenshannon(reference_probs, candidate_probs)


def align_distributions(reference, candidate) -> tuple[dict, dict]:
    """
    Выравнивает два распределения, добавляя отсутствующие символы с нулевой частотой.
    """
    reference_symbols = set(reference['stats'].keys())
    candidate_symbols = set(candidate['stats'].keys())

    # Добавляем отсутствующие символы в кандидата
    for symbol in reference_symbols - candidate_symbols:
        candidate['stats'][symbol] = {"count": 0, "percent": 0}

    for symbol in candidate_symbols - reference_symbols:
        reference['stats'][symbol] = {"count": 0, "percent": 0}

    # Сортируем символы по алфавиту
    sorted_reference_stats = dict(sorted(reference['stats'].items(), key=lambda item: item[0]))
    sorted_candidate_stats = dict(sorted(candidate['stats'].items(), key=lambda item: item[0]))
    reference['stats'] = sorted_reference_stats
    candidate['stats'] = sorted_candidate_stats
    return reference, candidate


def collect_statistic():
    """Вычисляет ряд распределения символов."""
    stat_path = Path("statistic_symbols.json")
    text_path = Path("text.txt")
    data = load_json(stat_path)
    text = load_text(text_path)

    print("Происходит сбор статистики...")
    symbol_stats(text, data)
    update_json(stat_path, data)


if __name__ == "__main__":
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

    ref_stat_bi = load_json(Path('statistic_bigrams.json'))
    ref_stat = load_json(Path('statistic_symbols.json'))
    ciph_stat_bi = bigram_stats(plaintext)
    ciph_stat = symbol_stats(plaintext)
    r, c = align_distributions(ref_stat_bi, ciph_stat_bi)
    print(r)
    print(c)
    print(compare_distributions_JS(ref_stat_bi, ciph_stat_bi))
    print(compare_distributions_JS(ref_stat, ciph_stat))
