from lab1 import primeGen, primeTest, Euclid_2, mypow
from lab2 import getCoprime, RSAkey
from lab3 import bitcoinHash
from names import nameGen

from random import randint, choice

def hasher(num):
    bytez = (num.bit_length() + 7) // 8
    data = num.to_bytes(bytez, "big")
    return int.from_bytes(bitcoinHash(data), "little")

class Server:
    def __init__(self):
        self.choices = {"Да": 0, "Нет": 1, "Воздержусь": 2}
        self.choicesR = {v : k for k, v in self.choices.items()}

        key = RSAkey().load("keys/RSA1024.key")
        self.n, self.exp, self.d = key.n, key.exp, key.d
        self.r = getCoprime(self.n)

        self.names = set()
        self.blanks = []
        print("Готов к приёму голосов!")

    def getChoices(self):
        return self.choices
    def getPubKey(self):
        return self.n, self.exp, self.r

    def sendVote(self, name, num, sign):
        if name in self.names: return f'{name}, не хитри'
        self.names.add(name)
        self.blanks.append((name, num, sign))
        return "Голос на рассмотрении"

    def calcBlanks(self):
        print("Голосование окончено, сервер отключён от глобальной сети")
        # Допустим, только сейчас стало доступно приватное число (self.d), для безопасности
        n, pub, priv = self.n, self.exp, self.d

        counter = {v: 0 for v in self.choices.values()}
        for name, num, sign in self.blanks:
            _s = mypow(sign, priv, n)
            inv = Euclid_2(self.r, n)[1] % n
            s = _s * inv % n

            hash, expected = hasher(num), mypow(s, pub, n)
            if hash == expected:
                print(f"Голос '{name}' принят:", self.choicesR[num & 3])
                counter[num & 3] += 1
            else:
                print(f"Голос '{name}' отклонен")
                print("\nhash:", hash)
                print("\nexpected:", expected)
                print()

        print("\nПроголосовавшие:", *sorted(self.names))
        print("\nРезультаты голосования:")
        print("За: \t\t", counter[0])
        print("Против:\t\t", counter[1])
        print("Воздержались:\t", counter[2])



class Client:
    def __init__(self, S):
        self.n, self.exp, self.r = S.getPubKey()
        self.choices = S.getChoices()
        self.choices2 = tuple(self.choices.keys())
        self.S = S
    def getChoices(self):
        return self.choices2
    def sign(self, choice):
        n, exp, r = self.n, self.exp, self.r
        bits = 256
        num = randint(0, (1 << bits) - 1)

        num = num << 2 | choice
        hash = hasher(num)
        sign = hash * mypow(r, exp, n) % n
        return num, sign
    def vote(self, name, s):
        choice = self.choices[s]
        num, sign = self.sign(choice)
        return self.S.sendVote(name, num, sign)



if __name__ == '__main__':
    S = Server()

    print("~" * 77)
    C = Client(S) # подключение к серверу
    arr = C.getChoices()
    print("Допустимый выбор:", arr)
    for i in range(100):
        name = nameGen()
        c = choice(arr)

        # не имеет специализированного софта, хочет накрутить голоса от чужих имёт, либо ещё что-то
        victim = not randint(0, 7)

        if victim: verdict = S.sendVote(name, 123, 1232312442213)
        else: verdict = C.vote(name, c)

        print(f"'{name}' проголосовал {c} с вердиктом: {verdict}")
    print("~" * 77)

    S.calcBlanks()
