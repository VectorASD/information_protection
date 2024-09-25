from lab1 import mypow, Euclid, Euclid_2, primeTest, primeGen, real_primes
from random import randint
import pickle

def invertor(a, mod):
    gcd, x = Euclid_2(a, mod)
    if gcd != 1: return # raise ValueError("Числа не взаимно простые")
    return x % mod

def coprimeGen(p):
    # необходимо найти такие 'c' и 'd', чтобы c * d % (p - 1) = 1
    while True:
        c = randint(2, p - 2)
        d = invertor(c, p - 1)
        if d is not None and c * d % (p - 1) == 1: return c, d

def ShamirAB():
    p = primeGen(100)
    print("p:", p)
    # p общие для всех абонентов

    # Алиса:
    cA, dA = coprimeGen(p)
    print("Алиса:", cA, dA)

    # Боб:
    cB, dB = coprimeGen(p)
    print("Боб:", cB, dB)

    # Алиса (хочет передать 'm' по закрытому каналу связи):
    m = randint(0, p - 1)
    x1 = mypow(m, cA, p)
    print("m:", m)
    print("x1:", x1)
    # Алиса передаёт Бобу 'x1' по открытому каналу связи

    # Боб:
    x2 = mypow(x1, cB, p)
    print("x2:", x2)
    # Боб передаёт Алисе 'x2' по открытому каналу связи

    # Алиса:
    x3 = mypow(x2, dA, p)
    print("x3:", x3)
    # Алиса передаёт Бобу 'x3' по открытому каналу связи

    # Боб:
    x4 = mypow(x3, dB, p)
    print("x4:", x4)

    assert x4 == m # где-то в будущем они лично встретились, и проверили правильность сообщения...

def testShamir():
    print("=" * 77)
    print("=" * 33, "testShamir", "=" * 34)
    print("=" * 77)
    for i in range(32):
        p = primeGen(100) # общее
        cA, dA = coprimeGen(p) # Алиса (секрет)
        cB, dB = coprimeGen(p) # Боб (секрет)

        m = randint(0, p - 1) # Алиса (секрет)
        x1 = mypow(m, cA, p) # Алиса
        x2 = mypow(x1, cB, p) # Боб
        x3 = mypow(x2, dA, p) # Алиса
        x4 = mypow(x3, dB, p) # Боб (секрет)
        print(f"{p} | {m} -> {x4}")
        assert id(m) != id(x4) and m == x4, "Шамир не прошёл проверку"

    # Переменные без пометки "секрет", т.е. проходящие через канал открытой связи:
    # (p, x1, x2, x3). Еви ничего с этим не может поделать без ПК размером с солнце

    # Проблема: после первого же сообщения cA, dA, cB и dB придётся выкинуть
    # из-за чего нет смысла хранить ключи для постоянного использования
    # нет разделения на приватный и публичный ключ, т.к. они все одноразовые

    # Слишком много пересылок

class ShamirKey:
    def gen(self, bits):
        self.p = p = primeGen(bits) # общее
        self.cA, self.dA = coprimeGen(p) # только у Алиса
        self.cB, self.dB = coprimeGen(p) # только у Боба
        return self
    def enc(self, msg):
        p, cA, cB = self.p, self.cA, self.cB
        x1 = mypow(msg, cA, p) # Алиса посчитала, отправила Бобу
        x2 = mypow(x1, cB, p) # Боб просчитал, у себя оставил
        return x2
    def dec(self, x2):
        p, dA, dB = self.p, self.dA, self.dB
        x3 = mypow(x2, dA, p) # Боб отправил Алисе, она посчитала, отправила Бобу
        x4 = mypow(x3, dB, p) # Боб посчитал, узнал содержимое
        return x4
    def coder(self, MPL, prefix):
        return self.enc, self.dec, self.p.bit_length(), MPL, prefix, self.p, 1, self
    def save(self, name):
        with open(name, "wb") as file: pickle.dump((self.p, self.cA, self.dA, self.cB, self.dB), file)
        return self
    def load(self, name):
        with open(name, "rb") as file: self.p, self.cA, self.dA, self.cB, self.dB = pickle.load(file)
        return self
    def savePublic(self, stream):
        stream.write(b"\0")
        pickle.dump((self.p, self.cA, self.cB), stream)
        return self
    def loadPublic(self, stream):
        self.p, self.cA, self.cB = pickle.load(stream)
        self.dA = self.dB = None # потеряшка (выведена из строя функция dec)
        return self
    def print(self):
        print("~" * 77)
        print("p:", self.p, "\n")
        print("cdA:", self.cA, "|", self.dA, "\n")
        print("cdB:", self.cB, "|", self.dB)
        print("~" * 77)
        return self
    def __eq__(self, op2):
        return self.p == op2.p and self.cA == op2.cA and self.dA == op2.dA and self.cB == op2.cB and self.dB == op2.dB

def testShamirKey():
    ShamirKey().gen(64).print().save("keys/Shamir64.key")
    sk = ShamirKey().gen(1024).print().save("keys/Shamir1024.key")
    sk2 = ShamirKey().load("keys/Shamir1024.key")
    assert sk == sk2, "Ошибка сериализации/десериализации"
    msg = randint(0, sk2.p - 1)
    print(msg, "|", sk2.dec(sk.enc(msg)))
    assert msg == sk.dec(sk2.enc(msg)), "Проблемы кодирования/декодирования"





def ElGamalAB():
    p = primeGen(100)
    g = primeGen(100 - 1) # p > g
    # p и g общие для всех абонентов. Абонентов от 2 до бесконечности

    # Алиса:
    m = randint(0, p - 1)
    # Алиса хочет передать Бобу 'm' и запрашивает публичный ключ:

    # Боб:
    priv = randint(0, p - 1)
    pub = mypow(g, priv, p)
    print("priv,pub:", priv, pub)
    # Боб передаёт Алисе ТОЛЬКО pub

    # Алиса (имеет только (p, g), pub):
    while True:
        k = randint(1, p - 2)
        if Euclid(k, p - 1) == 1: break # вообще не обязательно, только ради устойчивости
        # в учебнике этого почему-то не написано, зато в первых же попавшихся яндекс картинках... XD
    r = mypow(g, k, p)
    e = mypow(pub, k, p) * m % p
    print("m,k:", m, k)
    print("r,e:", r, e)
    # Алиса передаёт Бобу (r, e) и держит в тайне (m, k)

    # Боб (имеет только (p, g), (priv, pub), (r, e)):
    m2 = mypow(r, p - 1 - priv, p) * e % p
    print("m2:", m2)

    assert m == m2 # где-то в будущем они лично встретились, и проверили правильность сообщения...

def testElGamal():
    print("=" * 77)
    print("=" * 33, "testGamal", "=" * 34)
    print("=" * 77)
    for i in range(32):
        p = primeGen(100) # общее
        g = primeGen(100 - 1) # общее. p > g

        priv = randint(0, p - 1) # Боб (секрет)
        pub = mypow(g, priv, p) # Боб

        m = randint(0, p - 1) # Алиса (секрет)
        while True:
            k = randint(1, p - 2) # Алиса (секрет)
            if Euclid(k, p - 1) == 1: break
        r = mypow(g, k, p) # Алиса
        e = mypow(pub, k, p) * m % p # Алиса
        m2 = mypow(r, p - 1 - priv, p) * e % p # Боб (секрет)
        print(f"{m} -> ({r}, {e}) -> {m2}")
        assert id(m) != id(m2) and m == m2, "Эль-Гамаль не прошёл проверку"

    # Переменные без пометки "секрет", т.е. проходящие через канал открытой связи:
    # (p, g, pub, r, e). Еви ничего с этим не может поделать без ПК размером с солнце

    # Достоинство: уже есть понятие публичный и приватный ключ
    # Недостатки: НО они (ключи) опять одноразовые XD нет смысла хранить

    # Пересылка хоть и одна, но сообщение теперь в 2 раза больше

class ElGamalKey:
    def gen(self, bits):
        self.p = p = primeGen(bits) # общее
        self.g = g = primeGen(bits - 1) # общее. p > g
        self.priv = priv = randint(2, p - 1) # только у Боба
        self.pub = mypow(g, priv, p) # только у Боба
        # для подписи
        priv2 = randint(2, p - 1)
        while Euclid(p - 1, priv2) != 1: priv2 = randint(2, p - 1)
        self.priv2, self.pub2 = priv2, mypow(g, priv2, p)
        return self
    def enc(self, msg, _):
        p, g, pub = self.p, self.g, self.pub # Алиса запросила у Боба pub, она же полностью покрывает этот метод
        while True:
            k = randint(1, p - 2)
            if Euclid(k, p - 1) == 1: break
        r = mypow(g, k, p)
        e = mypow(pub, k, p) * msg % p
        return r, e # отправила Бобу ТОЛЬКО это
    def dec(self, r, e):
        p = self.p
        return (mypow(r, p - 1 - self.priv, p) * e % p,) # Боб вскрыл сообщение
    def coder(self, MPL, prefix):
        return self.enc, self.dec, self.p.bit_length(), MPL, prefix, self.p, 2, self
    def save(self, name):
        with open(name, "wb") as file: pickle.dump((self.p, self.g, self.priv, self.pub, self.priv2, self.pub2), file)
        return self
    def load(self, name):
        with open(name, "rb") as file: self.p, self.g, self.priv, self.pub, self.priv2, self.pub2 = pickle.load(file)
        return self
    def savePublic(self, stream):
        stream.write(b"\1")
        pickle.dump((self.p, self.g, self.pub, self.pub2), stream)
        return self
    def loadPublic(self, stream):
        self.p, self.g, self.pub, self.pub2 = pickle.load(stream)
        self.priv = self.priv2 = None # потеряшка (выведена из строя функция dec)
        return self
    def print(self):
        print("~" * 77)
        print("pg:", self.p, "|", self.g, "\n")
        print("priv:", self.priv, "\n")
        print("pub:", self.pub, "\n")
        print("priv2:", self.priv2, "\n")
        print("pub2:", self.pub2)
        print("~" * 77)
        return self
    def __eq__(self, op2):
        return self.p == op2.p and self.g == op2.g and self.priv == op2.priv and self.pub == op2.pub
    def sign(self, msg):
        p = self.p
        u = (msg - self.priv * self.pub2) % (p - 1)
        s = (Euclid_2(self.priv2, p - 1)[1] * u) % (p - 1)
        return s
    def unsign(self, s):
        p = self.p
        msg = mypow(self.pub, self.pub2, p) * mypow(self.pub2, s, p) % p
        return msg # на самом деле это не msg, а mypow(self.g, msg, p)
    def coder2(self, MPL, prefix):
        return self.unsign, self.sign, self.p.bit_length(), MPL, prefix, self.p, 1, self

def testElGamalKey():
    ElGamalKey().gen(64).print().save("keys/ElGamal64.key")
    sk = ElGamalKey().gen(1024).print().save("keys/ElGamal1024.key")
    sk2 = ElGamalKey().load("keys/ElGamal1024.key")
    assert sk == sk2, "Ошибка сериализации/десериализации"
    msg = randint(0, sk2.p - 1)
    print(msg, "|", sk2.dec(*sk.enc(msg, None))[0])
    assert msg == sk.dec(*sk2.enc(msg, None))[0], "Проблемы кодирования/декодирования"
#testElGamalKey()
#exit()





def GilbertVernam():
    print("=" * 77)
    print("=" * 32, "GilbertVernam", "=" * 32)
    print("=" * 77)
    for i in range(32):
        n = 100
        max = (1 << n) - 1
        key = randint(0, max)
        msg = randint(0, max)
        enc = msg ^ key
        dec = enc ^ key
        print(f"{msg} -> {enc} -> {dec}")
        assert msg == dec # я верю, что xor на xor = отсутствие xor
        # так что отдельно что-то тестировать нет смысла
        # Проблема: ключи одноразовые. Способа доставки не предусмотрено. Может быть key = 0, тогда enc = msg

class GVkey:
    def gen(self, bits, count):
        self.bits = bits
        max = (1 << self.bits) - 1
        self.base = *(randint(0, max) for i in range(count)),
        self.encC = self.decC = 0
        return self
    def reset(self):
        self.encC = self.decC = 0
        return self
    def enc(self, m):
        n = self.encC
        self.encC = n + 1
        return m ^ self.base[n % len(self.base)]
    def dec(self, m):
        n = self.decC
        self.decC = n + 1
        return m ^ self.base[n % len(self.base)]
    def coder(self, MPL, prefix):
        return self.enc, self.dec, self.bits, MPL, prefix, 1 << self.bits, 1, self
    def save(self, name):
        with open(name, "wb") as file: pickle.dump((self.bits, self.base), file)
        return self
    def load(self, name):
        with open(name, "rb") as file: self.bits, self.base = pickle.load(file)
        self.encC = self.decC = 0
        return self
    def print(self):
        print("~" * 77)
        print("bits:", self.bits, "| counters:", self.encC, self.decC, "\n")
        print("base[0]:", self.base[0], "\n")
        print("base[1]:", self.base[1], "\n")
        print("base[2]:", self.base[2], "\n")
        print("base[3]:", self.base[3], "\n")
        print("base[4]:", self.base[4], "\n...")
        print("~" * 77)
        return self
    def __eq__(self, op2):
        return self.bits == op2.bits and self.base == op2.base

def testGVkey():
    GVkey().gen(64, 5000).print().save("keys/GV64.key")
    sk = GVkey().gen(1024, 5000).print().save("keys/GV1024.key")
    sk2 = GVkey().load("keys/GV1024.key")
    assert sk == sk2, "Ошибка сериализации/десериализации"
    maxMsg = (1 << sk.bits) - 1
    for i in range(10):
        msg = randint(0, maxMsg)
        print(msg, "|", sk2.dec(sk.enc(msg)))
        assert msg == sk.dec(sk2.enc(msg)), "Проблемы кодирования/декодирования"





def RSA_keygen(nL):
    def check_edges(n):
        psize = n * 9 // 16
        pmin = (1 << psize - 1) + 1
        pmax = (1 << psize) - 1
        assert pmin.bit_length() == psize == pmax.bit_length()
        qsize = n * 7 // 16
        if n % 16: qsize += 1
        qmin = (1 << qsize - 1) + 1
        qmax = (1 << qsize) - 1
        assert qmin.bit_length() == qsize == qmax.bit_length()
        #print("p:", pmin, "..", pmax)
        #print("q:", qmin, "..", qmax)
        nmin, nmax = pmin * qmin, pmax * qmax
        yeah = n in range(nmin.bit_length(), nmax.bit_length() + 1)
        #if yeah: print("n:", nmin, "..", nmax, "|->", n, nmin.bit_length(), nmax.bit_length())
        assert yeah
    #for n in range(5, 1000): check_edges(n)
    #вывод: если использовать обычный интервал для p и q: n * 9 // 16, n * 7 // 16,
    # то условие аккуратности будет достижимо ТОЛЬКО при n % 16 == 0 and n > 4
    # если прибавить +1 к размеру p ИЛИ q, тогда аккуратность будет достижима ДЛЯ ВСЕХ n > 4
    # если прибавить +1 к размеру И p, И q, тогда аккуратность будет НЕ достижима при n % 16 == 0

    def check_pq_sizes(n):
        psize, qsize = n * 9 // 16, n * 7 // 16
        if n % 16: qsize += 1
        pqsize = psize + qsize
        #print(n, psize, qsize, pqsize)
        assert pqsize == n 
    #for n in range(5, 100000): check_pq_sizes(n)
    #вывод: моя идея +1 к qsize (или psize) нарушает условие nsize = qsize + psize при n % 16 == 0
    # ПО ЭТОМУ ТЕПЕРЬ +1 НЕ задаётся при n % 16 == 0, т.е. задаётся при n % 16 != 0
    # после корректировки check_edges этому правило, ниодин assert не провалил проверку!

    def fail_checker():
        # d is not None по сути gcd(c, f) == 1, т.е. gcd(c, (p - 1) * (q - 1)) == 1, где c, p, q - простые
        primes = real_primes[:200]
        fail = {p: 0 for p in primes}
        d_set = set()
        for exp in primes:
            for p in primes:
                for q in primes:
                    if p <= q: continue

                    n = p * q
                    nL = n.bit_length()
                    psize, qsize = nL * 9 // 16, nL * 7 // 16
                    if nL % 16: qsize += 1
                    if q.bit_length() != qsize or p.bit_length() != psize: continue

                    f = (p - 1) * (q - 1)
                    if exp >= f: continue

                    d = invertor(exp, f)
                    d2 = Euclid_2(exp, f)[1] % f
                    if d is None:
                        print(exp, f, "|", p, q, "|", d2, exp * d2 % f)
                        fail[exp] += 1
                        d_set.add(d2)
        print(d_set)
        for p in primes: print(p, "->", fail[p])
    #fail_checker()
    # fail_checker доказывает, что не существует такой 'exp', что гарантировала бы условие gcd(exp, f) == 1
    # зато выяснилось, что во ВСЕХ случаях нарушения, т.е. gcd(exp, f) != 1, коэффициент Безу (т.е. d) == 1

    assert nL >= 5
    #shift = n // 16
    psize, qsize = nL * 9 // 16, nL * 7 // 16
    if nL % 16: qsize += 1
    if psize == qsize:
        psize += 1
        qsize -= 1

    p = primeGen(psize) # primeGen(nL // 2 + nL // 16) # primeGen(nL // 2 + shift)
    q = primeGen(qsize) # primeGen(nL // 2 - nL // 16) # primeGen(nL // 2 - shift)
    # p > q
    n = p * q

    change_p = False
    while n.bit_length() != nL:
        if change_p: p = primeGen(psize)
        else: q = primeGen(qsize)
        change_p = not change_p
        n = p * q
    assert p.bit_length() == psize and q.bit_length() == qsize and n.bit_length() == nL # все 3 условия на практике здесь ненарушимы

    f = (p - 1) * (q - 1)
    #print("p:", p)
    #print("q:", q)
    #print("n:", n)
    #print("f:", f)
    # exp = 2 всегда не проходит проверку gcd == 1, т.к. p и q - нечётные, значит (p - 1) * (q - 1) - всегда чётное
    exp = 3 if nL < 32 else 0x10001
    while True:
        #print("check", exp)
        if primeTest(exp):
            gcd, d = Euclid_2(exp, f)
            d %= f
            if gcd == 1 and exp * d % f == 1: break
        exp += 1
    #print("exp:", exp)
    #print("exp2:", d)
    if False:
        enc = *(mypow(i, exp, n) for i in range(min(n, 5000))),
        dec = *(mypow(i, d, n) for i in enc),
        print(enc[:64], len(enc))
        print(dec[:64], dec == tuple(range(len(dec))))
    return p, q, n, f, exp, d

class RSAkey:
    def gen(self, bits):
        self.p, self.q, self.n, self.f, self.exp, self.d = RSA_keygen(bits)
        return self
    def enc(self, m): return mypow(m, self.exp, self.n)
    def dec(self, m): return mypow(m, self.d, self.n)
    def coder(self, MPL, prefix):
        return self.enc, self.dec, self.n.bit_length(), MPL, prefix, self.n, 1, self
    def save(self, name):
        with open(name, "wb") as file: pickle.dump((self.p, self.q, self.n, self.f, self.exp, self.d), file)
        return self
    def load(self, name):
        with open(name, "rb") as file: self.p, self.q, self.n, self.f, self.exp, self.d = pickle.load(file)
        return self
    def savePublic(self, stream):
        stream.write(b"\2")
        pickle.dump((self.exp, self.n), stream)
        return self
    def loadPublic(self, stream):
        self.exp, self.n = pickle.load(stream)
        self.p = self.q = self.f = self.d = None # потеряшка (выведена из строя функция dec)
        return self
    def print(self):
        print("~" * 77)
        print("p:", self.p, "\n")
        print("q:", self.q, "\n")
        print("n:", self.n, "\n")
        print("f:", self.f, "\n")
        print("exp:", self.exp, "\n")
        print("exp2:", self.d)
        print("~" * 77)
        return self
    def __eq__(self, op2):
        return self.p == op2.p and self.q == op2.q and self.n == op2.n and self.f == op2.f and self.exp == op2.exp and self.d == op2.d

def testRSAkey():
    RSAkey().gen(64).print().save("keys/RSA64.key")
    sk = RSAkey().gen(1024).print().save("keys/RSA1024.key")
    sk2 = RSAkey().load("keys/RSA1024.key")
    assert sk == sk2, "Ошибка сериализации/десериализации"
    for i in range(10):
        msg = randint(0, sk.n - 1)
        print(msg, "|", sk2.dec(sk.enc(msg)))
        assert msg == sk.dec(sk2.enc(msg)), "Проблемы кодирования/декодирования"





registeredKeyLoaders ={}
def loadPublicKey(stream):
    n = stream.read(1)[0]
    if n == 0: return ShamirKey().loadPublic(stream)
    if n == 1: return ElGamalKey().loadPublic(stream)
    if n == 2: return RSAkey().loadPublic(stream)
    return registeredKeyLoaders[n](stream)
def registerKeyLoader(n, loadPublicF): registeredKeyLoaders[n] = loadPublicF



if __name__ == "__main__":
    ShamirAB()
    testShamir()
    ElGamalAB()
    testElGamal()
    GilbertVernam()

    testShamirKey()
    testElGamalKey()
    testGVkey()
    testRSAkey()

    #RSAkey().gen(128).print()
