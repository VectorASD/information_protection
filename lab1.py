from random import randint
from math import gcd as builtin_gcd
from fractions import Fraction
import sys
sys.set_int_max_str_digits(1000000)
from time import time





# просто функция побитового возведения в степень + немного модульной алгебры
def mypow(num, exp, mod):
    if type(num) is not int or type(exp) is not int or type(mod) is not int:
        raise TypeError("mypow() all arguments not are integers")
    if exp < 0: raise ValueError("base is not invertible for the given modulus")
    if mod == 0: raise ValueError("mypow() 3rd argument cannot be 0")

    num %= mod
    res = 1
    while exp:
        exp, bit = divmod(exp, 2)
        if bit: res = res * num % mod
        num = num * num % mod
        #print(bit, num) # только степени num: 1, 2, 4, 8...
    return res

def test_mypow():
    print()
    print("=" * 77)
    print("=" * 33, "test_mypow", "=" * 33)
    print("=" * 77)
    for i in range(100):
        num, base, mod = randint(-99, 99), randint(0, 99999999999999999999), randint(-99, 98)
        if mod >= 0: mod += 1 # 0..98 -> 1..99

        my_res = mypow(num, base, mod)
        builtin_res = pow(num, base, mod) # просто для проверки собственного pow (mypow)
        print(f"mypow({num}, {base}, {mod}) = {my_res} (builtin: {builtin_res})")
        assert my_res == builtin_res, "Тест mypow провален :/"





def Euclid(a, b): # обычный
    while b: a, b = b, a % b
    return a

def Euclid_2(a, b): # расширенный, но только с одним коэффициентами Безу
    ax, bx = 1, 0
    while b:
        q, mod = divmod(a, b)
        a, ax, b, bx = (b, bx,
            mod, ax - q * bx)
    return a, ax

def Euclid_3(a, b): # расширенный, с обоими коэффициентами Безу
    #if a < b: a, b = b, a # a >= b ... А на деле в этом нет смысла
    ax, ay = 1, 0 # a = a * ax + b * ay
    bx, by = 0, 1 # b = a * bx + b * by
    #print(a, ax, ay)
    #print(b, bx, by)
    while b:
        q, mod = divmod(a, b)
        a, ax, ay, b, bx, by = (b, bx, by,
            mod, ax - q * bx, ay - q * by) # новая строка
        # предпоследнюю строку забываем, а в конец добавляем новую
        # 'a' всегда! >= 'b' из-за того, модуль меньше старой b
        #print(b, bx, by, "| q =", q)
    return a, ax, ay

def testEuclid():
    print()
    print("=" * 77) # Trebuchet MS
    print("=" * 34, "testEuclid", "=" * 34)
    print("=" * 77)
    for i in range(100):
        a, b = randint(-99, 99), randint(-99, 99)
        
        gcd = Euclid(a, b)
        gcdA, x = Euclid_2(a, b)
        assert gcd == gcdA
        gcdB, xA, y = Euclid_3(a, b)
        assert gcd == gcdB and x == xA

        gcd2 = a * x + b * y
        gcd3 = builtin_gcd(a, b)
        # почему-то встроенный gcd пропускает результат по модулю O_o
        # в криптографии не критично, т.к. обычно нет отрицательных чисел там, где используется Euclid
        print(f"gcd({a}, {b}) = {gcd}, {x}, {y} (builtin: {gcd3}, xy: {gcd2})")
        assert abs(gcd) == gcd3, "Неверный gcd"
        assert gcd == gcd2, "Неверный x и y"





def MillerRabinTest(n, k):
    if n < 2: return False
    d = n - 1
    r = 0
    while not (d & 1):
        r += 1
        d >>= 1
    for _ in range(k):
        a = randint(2, n - 2)
        x = mypow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = mypow(x, 2, n)
            if x == 1: return False
            if x == n - 1: break
        else: return False
    return True

def primeTest(num):
    if num < 10: return num in {2, 3, 5, 7}
    if not (num & 1): return False
    bitsize = num.bit_length()
    k = 3 if bitsize >= 1536 else 4 if bitsize >= 1024 else 7 if bitsize >= 512 else 10
    return MillerRabinTest(num, k)

real_primes = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329, 3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433, 3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529, 3533, 3539, 3541, 3547, 3557, 3559, 3571, 3581, 3583, 3593, 3607, 3613, 3617, 3623, 3631, 3637, 3643, 3659, 3671, 3673, 3677, 3691, 3697, 3701, 3709, 3719, 3727, 3733, 3739, 3761, 3767, 3769, 3779, 3793, 3797, 3803, 3821, 3823, 3833, 3847, 3851, 3853, 3863, 3877, 3881, 3889, 3907, 3911, 3917, 3919, 3923, 3929, 3931, 3943, 3947, 3967, 3989, 4001, 4003, 4007, 4013, 4019, 4021, 4027, 4049, 4051, 4057, 4073, 4079, 4091, 4093, 4099, 4111, 4127, 4129, 4133, 4139, 4153, 4157, 4159, 4177, 4201, 4211, 4217, 4219, 4229, 4231, 4241, 4243, 4253, 4259, 4261, 4271, 4273, 4283, 4289, 4297, 4327, 4337, 4339, 4349, 4357, 4363, 4373, 4391, 4397, 4409, 4421, 4423, 4441, 4447, 4451, 4457, 4463, 4481, 4483, 4493, 4507, 4513, 4517, 4519, 4523, 4547, 4549, 4561, 4567, 4583, 4591, 4597, 4603, 4621, 4637, 4639, 4643, 4649, 4651, 4657, 4663, 4673, 4679, 4691, 4703, 4721, 4723, 4729, 4733, 4751, 4759, 4783, 4787, 4789, 4793, 4799, 4801, 4813, 4817, 4831, 4861, 4871, 4877, 4889, 4903, 4909, 4919, 4931, 4933, 4937, 4943, 4951, 4957, 4967, 4969, 4973, 4987, 4993, 4999, 5003, 5009, 5011, 5021, 5023, 5039, 5051, 5059, 5077, 5081, 5087, 5099, 5101, 5107, 5113, 5119, 5147, 5153, 5167, 5171, 5179, 5189, 5197, 5209, 5227, 5231, 5233, 5237, 5261, 5273, 5279, 5281, 5297, 5303, 5309, 5323, 5333, 5347, 5351, 5381, 5387, 5393, 5399, 5407, 5413, 5417, 5419, 5431, 5437, 5441, 5443, 5449, 5471, 5477, 5479, 5483, 5501, 5503, 5507, 5519, 5521, 5527, 5531, 5557, 5563, 5569, 5573, 5581, 5591, 5623, 5639, 5641, 5647, 5651, 5653, 5657, 5659, 5669, 5683, 5689, 5693, 5701, 5711, 5717, 5737, 5741, 5743, 5749, 5779, 5783, 5791, 5801, 5807, 5813, 5821, 5827, 5839, 5843, 5849, 5851, 5857, 5861, 5867, 5869, 5879, 5881, 5897, 5903, 5923, 5927, 5939, 5953, 5981, 5987, 6007, 6011, 6029, 6037, 6043, 6047, 6053, 6067, 6073, 6079, 6089, 6091, 6101, 6113, 6121, 6131, 6133, 6143, 6151, 6163, 6173, 6197, 6199, 6203, 6211, 6217, 6221, 6229, 6247, 6257, 6263, 6269, 6271, 6277, 6287, 6299, 6301, 6311, 6317, 6323, 6329, 6337, 6343, 6353, 6359, 6361, 6367, 6373, 6379, 6389, 6397, 6421, 6427, 6449, 6451, 6469, 6473, 6481, 6491, 6521, 6529, 6547, 6551, 6553, 6563, 6569, 6571, 6577, 6581, 6599, 6607, 6619, 6637, 6653, 6659, 6661, 6673, 6679, 6689, 6691, 6701, 6703, 6709, 6719, 6733, 6737, 6761, 6763, 6779, 6781, 6791, 6793, 6803, 6823, 6827, 6829, 6833, 6841, 6857, 6863, 6869, 6871, 6883, 6899, 6907, 6911, 6917, 6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039, 7043, 7057, 7069, 7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207, 7211, 7213, 7219, 7229, 7237, 7243, 7247, 7253, 7283, 7297, 7307, 7309, 7321, 7331, 7333, 7349, 7351, 7369, 7393, 7411, 7417, 7433, 7451, 7457, 7459, 7477, 7481, 7487, 7489, 7499, 7507, 7517, 7523, 7529, 7537, 7541, 7547, 7549, 7559, 7561, 7573, 7577, 7583, 7589, 7591, 7603, 7607, 7621, 7639, 7643, 7649, 7669, 7673, 7681, 7687, 7691, 7699, 7703, 7717, 7723, 7727, 7741, 7753, 7757, 7759, 7789, 7793, 7817, 7823, 7829, 7841, 7853, 7867, 7873, 7877, 7879, 7883, 7901, 7907, 7919
def testPrimeTest():
    primes = []
    # real_primes получил из чьего-то кода на решето Эратосфена (первые 1000 простых чисел)
    for num in range(real_primes[-1] + 5):
        if primeTest(num): primes.append(num)
    assert tuple(primes) == real_primes, "PrimeTest не сдал тест"

def primeGen(nbits):
    assert nbits >= 2 # вечный цикл при nbits < 2
    min = (1 << nbits - 1) + 1
    max = (1 << nbits) - 1
    while True: # брутефорсим решение
        odd = randint(min, max)
        if primeTest(odd): return odd

#print(set(primeGen(2) for i in range(100))) # {3}
#print(set(primeGen(3) for i in range(100))) # {5, 7}
#print(set(primeGen(4) for i in range(100))) # {11, 13}
#print(set(primeGen(5) for i in range(100))) # {17, 19, 23, 29, 31}
#print(set(primeGen(6) for i in range(100))) # {37, 41, 43, 47, 53, 59, 61}





def make_pi(digits): # переделанный https://stackoverflow.com/questions/9004789/1000-digits-of-pi-in-python
    assert digits >= 4 # зачем на меньше 3.141?
    q, r, t, k, m, x = 1, 0, 1, 1, 3, 3
    res = bytearray()
    while True:
        if 4 * q + r - t < m * t:
            res.append(b"0123456789"[m])
            if len(res) > digits: break
            if len(res) == 1: res += b"."
            q, r, t, k, m, x = 10*q, 10*(r-m*t), t, k, (10*(3*q+r))//t - 10*m, x
            #print(q.bit_length(), r.bit_length(), t.bit_length()) # на 1000-ой цифре уже в каждом числе по 37.25k битов :/
        else:
            q, r, t, k, m, x = q*k, (2*q+r)*x, t*x, k+1, (q*(7*k+2)+r*x)//(t*x), x+2
    return Fraction(res.decode("utf-8"))

def faster_make_pi(digits): # ещё одна версия Spigot's алгоритма под PI. Быстрее, но floating point может дать течь
    assert digits >= 4
    k, a, b, a1, b1 = 2, 4, 1, 12, 4
    res = bytearray()
    while True:
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p*a + q*a1, p*b + q*b1
        d, d1 = a / b, a1 / b1
        while d == d1:
            res.append(b"0123456789"[int(d)])
            if len(res) > digits: return Fraction(res.decode("utf-8"))
            if len(res) == 1: res += b"."
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a / b, a1 / b1

def test_pi_makers():
    T = time()
    a = make_pi(10000)
    T2 = time()
    b = faster_make_pi(10000)
    T3 = time()
    print((T2 - T) / (T3 - T2), a == b) # 4.354990197399873 True

def MODP_gen(bits, digits, delta): # синтезировал на основе https://datatracker.ietf.org/doc/html/rfc3526
    # суть сразу очевидна: 8 байтов 0xFF + простое число + 8 байтов 0xFF
    # но из-за требования того, что результат должен быть простым числом,
    # есть delta - первое смещение, выдающее простое число
    prime = (1 << bits) - (1 << bits - 64) - 1
    prime += int(faster_make_pi(digits) * (1 << bits - 130) + delta) << 64
    #bytes = (bits + 7) // 8
    #print(prime.to_bytes(bytes).hex())
    assert primeTest(prime)
    gen = 2
    return prime, gen

def find_MODP_digits(bits, correct, delta):
    R = 4
    while True:
        if MODP_gen(bits, R, delta)[0] == correct: break
        R <<= 1
    L = R >> 1
    while L < R:
        M = (L + R) // 2
        if MODP_gen(bits, M, delta)[0] == correct: R = M
        else: L = M + 1
    print(f"use:\np, g = MODP_gen({bits}, {L}, {delta})")

# p2 = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C... - уже когда-то проссчитанное число Network Working Group
# find_MODP_digits(8192, p2, 4743158) печатает, сколько цифр нужно в числе-PI для корректной работы MODP_gen

MODP_groups = {
    5: lambda: MODP_gen(1536, 425, 741804),
    14: lambda: MODP_gen(2048, 579, 124476),
    15: lambda: MODP_gen(3072, 887, 1690314),
    16: lambda: MODP_gen(4096, 1196, 240904),
    17: lambda: MODP_gen(6144, 1812, 929484),
    18: lambda: MODP_gen(8192, 2428, 4743158)
}
"""
>>> (1536 - 130) / 425 -> 3.308235294117647
>>> (2048 - 130) / 579 -> 3.312607944732297
>>> (3072 - 130) / 887 -> 3.3167981961668547
>>> (4096 - 130) / 1196 -> 3.3160535117056855
>>> (6144 - 130) / 1812 -> 3.3189845474613686
>>> (8192 - 130) / 2428 -> 3.3204283360790776
Выяснил методом подбора, что если нам нужно правильное PI-число,
после умножения на некоторую N, то количество цифр PI-числа должно
составлять примерно N / (10 / 3)

p, g = MODP_groups[18]()
q = p >> 1
assert primeTest(q) Для всех MODP это утверждение тоже верно 
"""





def DiffieHelman(p, g, use_print = False):
    # p - prime
    # g - generator

    a = randint(0, 999999) # секрет Алисы
    A = mypow(g, a, p)
    # Алиса отправила Бобу (g, p, A)

    b = randint(0, 999999) # секрет Боба
    B = mypow(g, b, p)
    Bkey = mypow(A, b, p)
    # Боб отправил Алисе (B)

    Akey = mypow(B, a, p)
    if use_print: print(f"private: {a}, {b} | public: {p}, {g};\n    {A}, {B} |\n    key: {Akey}, {Bkey}")

    assert Akey == Bkey, "Ошибка :/"
    assert id(Akey) != id(Bkey), "Akey и Bkey должны иметь разные источники получения"
    # на практике это невозможно, т.к. я не делаю Akey = Bkey или наоборот

    # Akey = mypow(B, a, p) = mypow(mypow(g, b, p), a, p) = mypow(g, a * b, p) = mypow(mypow(g, a, p), b, p) = mypow(A, b, p) = Bkey
    # Простой (почти) математикой доказано, что Akey = Bkey
    # Судя по ограничения mypow, a и b >= 0, g вообще любое, p != 0, от чего Akey и Bkey могут быть отрицательными, НО ВСЁ РАВНО одинаковыми
    # Интересный факт: если 'p' не является простым, то всё равно Akey = Bkey

    # нашёл в интернете NIST SP800-56 для проверки публичных ключей
    # assert A > 2 and mypow(A, (p - 1) // 2, p) == 1, "неверный публичный ключ A"
    # assert B > 2 and mypow(B, (p - 1) // 2, p) == 1, "неверный публичный ключ B"
    # но убрал, т.к. в учебнике нет требования и эту проверку делать

    return a, A, Akey, b, B, Bkey # не смотря на то, что Akey = Bkey, это для правдоподобности, да и id у них всегда разные

def testDiffieHelman():
    print()
    print("=" * 77)
    print("=" * 32, "DiffieHelman", "=" * 33)
    print("=" * 77)
    for i in range(10):
        while True:
            p = primeGen(100)
            q = p >> 1
            if primeTest(q):
                g = randint(2, p - 2)
                if mypow(g, q, p) != 1: break
        # при g = 2, 3 не все простые числа проходят тест NIST SP800-56
        DiffieHelman(p, g, True)
    for i in range(10):
        p, g = MODP_groups[5]()
        DiffieHelman(p, g, True)





def GelfondSchenks(a, b, p):
    # a**x % p = b, найти x
    assert primeTest(p), "p должно быть простым"
    assert a in range(1, p), "a должно быть от 1 до p (без p)"
    assert b in range(1, p), "b должно быть от 1 до p (без p)"

    m = k = int(p ** 0.5) + 1 # находим m и k, чтобы m * k > p, m = k
    # на 44 странице учебника видно, почему не надо брать m или k больше корня p + 1
    # это из-за ограничения a < p, b < p
    row = {mypow(a, i * m, p): i for i in range(1, k + 1)}
    for j in range(1, m):
        rec = b * mypow(a, j, p) % p
        try:
            i = row[rec]
            x = i * m - j
            return x
        except KeyError: pass
    # и действительно! Трудоёмкость mypow: log2(p)
    # значит трудоёмкость всего алгоритма: 2 * sqrt(p) * log2(p)
    # если с j = 1 найдёт сразу ответ, тогда просто: (1 + sqrt(p)) * log2(p)

def testGelfondSchenks():
    print()
    print("=" * 77)
    print("=" * 30, "testGelfondSchenks", "=" * 30)
    print("=" * 77)
    for i in range(10):
        prime = primeGen(20)
        a, y = randint(1, prime - 1), randint(1, prime - 1)
        x = GelfondSchenks(a, y, prime)
        if x is None:
            print(f"GelfondSchenks({a}, {y}, {prime}) -> нет решения")
            continue
        y2 = mypow(a, x, prime)
        print(f"GelfondSchenks({a}, {y}, {prime}) = {x} | a**x%p = {y2}")
        assert y == y2, "GelfondSchenks провалил ПЕРВУЮ проверку"
    for i in range(32):
        prime = primeGen(20)
        a, x = randint(1, prime - 1), randint(1, prime - 1)
        y = mypow(a, x, prime)
        x2 = GelfondSchenks(a, y, prime)
        assert x2 is not None, "Да ну"
        y2 = mypow(a, x2, prime)
        print(f"{a} ** {x} % {prime} = {y}    GelfondSchenks({a}, {y}, {prime}) = {x2}")
        print(f"    x = x2 ? {x == x2}; a ** x2 % prime = y2 = {y2}; y == y2 ? {y == y2}")
        assert y == y2, "GelfondSchenks провалил ВТОРУЮ проверку"
        





if __name__ == "__main__":
    #test_mypow()
    #testEuclid()
    #testPrimeTest()
    #testDiffieHelman()
    testGelfondSchenks()
