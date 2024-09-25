from lab1 import primeGen, primeTest, Euclid_2, mypow
from random import randint, shuffle

""" https://ru.wikipedia.org/wiki/Ментальный_покер

Алгоритм
Алгоритм перетасовки карт с использованием коммутативного шифрования выглядит следующим образом[3]:

Алиса и Боб соглашаются использовать определенную «колоду» карт. На практике это означает, что они согласны использовать множество чисел или других данных таких, что каждый элемент множества представляет собой карту.
Алиса шифрует каждую карту колоды, используя ключ А.
Алиса тасует карты.
Алиса передает зашифрованную и перемешанную колоду Бобу. Он не знает, где какие карты.
Боб выбирает шифрование ключа B и использует его для шифрования каждой карты из уже зашифрованной и перетасованной колоды.
Боб тасует колоду.
Боб передает дважды зашифрованную и перетасованную колоду обратно Алисе.
Алиса расшифровывает каждую карту, используя её ключ А. Но шифрование Боба все ещё остается, то есть она не знает, где какие карты.
Алиса выбирает ключ шифрования каждой карты (А1, А2 и т. д.) и шифрует их по отдельности.
Алиса передает колоду Бобу.
Боб расшифровывает каждую карту, используя его ключ В. Индивидуальное шифрование Алисы все ещё остается, то есть он не знает, где какие карты.
Боб выбирает ключ для шифрования каждой карты (B1, B2 и т. д.) и шифрует их по отдельности.
Боб передает колоду обратно Алисе.
Алиса показывает колоду всем игрокам (в данном случае игроки — Алиса и Боб).
Теперь колода перемешана.

Во время игры Алиса и Боб будут забирать карты из колоды, для которых известен порядок в перемешанной колоде. Когда кто-либо из игроков захочет увидеть свои карты, он будет запрашивать соответствующие ключи от другого игрока. Этот игрок (после проверки того, что игрок действительно имеет право смотреть на карты) передает индивидуальные ключи для этих карт другому игроку. Также необходимо проверить, что игрок не пытался запросить ключ к картам, которые ему не принадлежат.
"""

def deckGen(letsShuffle):
    cards = []
    app = cards.append
    for suit in "♥♣♦♠": # черви, трефы, бубны, пики
        for face in ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'): app(face + suit)
    if letsShuffle: shuffle(cards)
    deck = {i: card for i, card in enumerate(cards, 2)}
    print("deck:", deck)
    return deck
    # "♥♦" - красные
    # "♣♠" - белые

def keysGen(players, p1):
    coprimes, inverteds = [], []
    for i in range(players):
        while True:
            coprime = randint(2, p1 - 1)
            gcd, inverted = Euclid_2(coprime, p1)
            if gcd == 1: break
        if inverted < 0: inverted += p1

        if coprime > inverted: coprime, inverted = inverted, coprime # для большей криптостойкости
        coprimes.append(coprime)
        inverteds.append(inverted)
    return coprimes, inverteds

def MentalPoker(players):
    while True:
        q = primeGen(64)
        p = 2 * q + 1
        if primeTest(p): break
    print("prime:", p)

    coprimes, inverteds = keysGen(players, p - 1)
    print("coprimes:", coprimes) # публичные ключи для шифрования
    print("inverteds:", inverteds) # приватные ключи для расшифровки

    test = 1234567890
    for pub in coprimes: test = mypow(test, pub, p)
    print("test:", test)
    test2 = test3 = test

    for priv in inverteds: test2 = mypow(test2, priv, p)
    print("test2:", test2)
    assert test2 == 1234567890

    for priv in inverteds[::-1]: test3 = mypow(test3, priv, p)
    print("test3:", test3)
    assert test3 == 1234567890

    print("\tИными словами...")
    pubMul = privMul = 1
    for pub in coprimes: pubMul *= pub
    for priv in inverteds: privMul *= priv
    print("pubMul:", pubMul)
    print("privMul:", privMul)

    test4 = mypow(1234567890, pubMul, p)
    print("test4:", test4)
    assert test4 == test

    test5 = mypow(test4, privMul, p)
    print("test5:", test5)
    assert test5 == 1234567890

    test6 = mypow(mypow(1234567890, privMul, p), pubMul, p)
    print("test6:", test6)
    assert test6 == 1234567890

    # игра начинается (у игроков нет чита в виде privMul переменной, иначе толку...)

    deck = deckGen(True)
    keys = tuple(deck.keys())
    print(keys, "\n")

    # гоняем колоду по каждому игроку, а он, в свою очередь, расходует РОВНО ОДИН и ТОТ ЖЕ САМЫЙ ключ
    for i, pub in enumerate(coprimes, 1):
        keys = [mypow(key, pub, p) for key in keys]
        shuffle(keys)
        print(f"после {i} игрока: {keys}\n")
    del coprimes # выкидываем публичные ключи... они нам больше не понадобятся
    # теперь В КАЖДОЙ карте публичный ключ КАЖДОГО

    # print(*(mypow(key, privMul, p) for key in keys)) # ой, случайно подсмотрел ;'-}



    pos = 0
    def getCard():
        nonlocal pos
        try: card = keys[pos]
        except IndexError: raise Exception("Увы, но колода кончилась")
        pos += 1
        return card

    circleMode = True
    cardsPerHand = 2
    tableSize = 5

    table = tuple(getCard() for i in range(tableSize))

    if circleMode: # просто влияет на очерёдность вызовов getCard()
        hands = [[] for i in range(players)]
        for j in range(cardsPerHand):
            for i in range(players): hands[i].append(getCard())
    else:
        hands = [tuple(getCard() for j in range(cardsPerHand)) for i in range(players)]

    print("Стол:", table)
    print("На руках:", hands)

    # расшифровка карт на столе
    for i in range(players):
        table = *(mypow(table[j], inverteds[i], p) for j in range(len(table))),
    print("Стол:", table)
    print()
    print("Карты на столе:", *(deck[key] for key in table))

    # расшифровка карт на руках
    hands = list(hands)
    for i in range(players):
        for j in range(players):
            if i != j: # пора каждому игроку прогнать свои карты через всех остальных ПО КРУГУ
                hands[i] = *(mypow(key, inverteds[j], p) for key in hands[i]),
        hands[i] = *(mypow(key, inverteds[i], p) for key in hands[i]), # и только в конце ЧЕРЕЗ СЕБЯ
        # я упущу механизм проверки, чтобы игрок не мог подглядеть у других или в неразобранной колоде

    for i in range(players): print(f"карты {i + 1}-го игрока:", *(deck[key] for key in hands[i]))

    # а вот быстрый способ подсмотреть колоду или оставшиеся карты, например, если кто-то сдался, когда осталось 2 игрока:
    lost = keys[pos:]
    print("Оставшиеся (подсмотренные) карты:", *(deck[mypow(key, privMul, p)] for key in lost))



if __name__ == '__main__':
    MentalPoker(3)
    input("Enter...")
