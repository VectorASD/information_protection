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

        self.names = set()
        self.blanks = []
        self.name2num = {}
        print("Готов к приёму голосов!")

    def getChoices(self):
        return self.choices
    def getPubKey(self):
        return self.n, self.exp

    def sendVote(self, name, num, sign):
        if name in self.names: return f'{name}, не хитри'
        self.names.add(name)

        _s = mypow(sign, self.d, self.n)
        self.name2num[name] = num
        return _s

    def sendVote2(self, name, s):
        self.blanks.append((name, s))
        return "Голос на рассмотрении"

    def calcBlanks(self):
        print("Голосование окончено, сервер отключён от глобальной сети")
        # Допустим, только сейчас стало доступно приватное число (self.d), для безопасности
        n, pub = self.n, self.exp

        counter = {v: 0 for v in self.choices.values()}
        S = 0
        names = set()
        for name, s in self.blanks:
            if name in names:
                print(f"Голос '{name}' отклонен из-за повторяющегося имени")
                continue
            names.add(name)

            num = self.name2num[name]
            hash, expected = hasher(num), mypow(s, pub, n)
            if hash == expected:
                print(f"Голос '{name}' принят:", self.choicesR[num & 3])
                counter[num & 3] += 1
                S += 1
            else:
                print(f"Голос '{name}' отклонен")
                print("\nhash:", hash)
                print("\nexpected:", expected)
                print()

        print("\nПроголосовавшие:", *sorted(self.names))
        print("\nРезультаты голосования (всего %s):" % S)
        print("За: \t\t", counter[0])
        print("Против:\t\t", counter[1])
        print("Воздержались:\t", counter[2])



class Client:
    def __init__(self, S):
        self.n, self.exp = S.getPubKey()
        self.choices = S.getChoices()
        self.choices2 = tuple(self.choices.keys())
        self.S = S
    def getChoices(self):
        return self.choices2
    def sign(self, choice):
        n, exp = self.n, self.exp
        bits = 256
        num = randint(0, (1 << bits) - 1)

        r = getCoprime(self.n)
        num = num << 2 | choice
        hash = hasher(num)
        sign = hash * mypow(r, exp, n) % n
        return num, sign, r
    def unsign(self, _s, r):
        n = self.n
        inv = Euclid_2(r, n)[1] % n
        s = _s * inv % n
        return s
    def vote(self, name, s):
        choice = self.choices[s]
        num, sign, r = self.sign(choice)
        _s = self.S.sendVote(name, num, sign)
        if type(_s) is str: return _s
        s = self.unsign(_s, r)
        return self.S.sendVote2(name, s)

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

        if victim:
            verdict = S.sendVote(name, 123, 1232312442213)
            if type(verdict) is int: verdict = S.sendVote2(name, verdict * 123)
        else: verdict = C.vote(name, c)

        print(f"'{name}' проголосовал {c} с вердиктом: {verdict}")
    print("~" * 77)

    S.calcBlanks()
