from hashlib import sha256

def bitcoinHash(data):
    return sha256(sha256(data).digest()).digest()[::-1]

def blockHash(version, prevBlock, merkleRoot, timestamp, bits, nonce):
    from struct import pack
    block = pack("<I32s32sIII", version, prevBlock[::-1], merkleRoot[::-1], timestamp, bits, nonce) # https://en.bitcoin.it/wiki/Block_hashing_algorithm
    hash = bitcoinHash(block) # цель проверки
    return block, hash
def checkBHash():
    # информацию о генезис-блоке изъята моим же инструментом: https://vectorasd.ru/BlockchainExplorer
    # timestamp 1231006505 это "04.01.2009, 00:15:05". Т.е. первый вздох bitcoin mainnet был в эту самую секунду
    block, hash = blockHash(1, b"\0" * 32, bytes.fromhex("4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"), 1231006505, 0x1d00ffff, 2083236893)
    assert len(block) == 80
    assert hash.hex() == "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
    print("It's ok!") # теперь доказано, что этот хешер реально биткоиновский
    print("block:", block.hex())
    print("hash:", hash.hex())
# checkBHash()



from lab1 import mypow, primeTest, Euclid_2
from lab2 import ShamirKey, ElGamalKey, RSAkey, loadPublicKey, registerKeyLoader
from lab2buffers import Wrapper
from io import BytesIO
import pickle
import os
from random import randint



def signer(data, coder, output):
    hash = bitcoinHash(data)
    #coder[7].print()
    print("hash:", hash.hex())

    wr = Wrapper(hash, coder, invertor = True).data2chain().ECB().CBC(9876543210)
    encrypted = wr.data.read()
    wr = Wrapper(encrypted, coder, invertor = True).CBC(9876543210, dec = True).ECB(dec = True).chain2data()
    decrypted = wr.data.read()
    print("decr:", decrypted.hex())
    assert hash == decrypted # свою же подпись прочекал, вернее, способность coder восстановить хеш назад

    pickle.dump((encrypted, coder[3], coder[4]), output)
    coder[7].savePublic(output)
    output.write(data)



class SignError(Exception): pass

def signChecker(input):
    sign = pickle.load(input)
    public = loadPublicKey(input)
    data = input.read()
    hash = bitcoinHash(data)

    #public.print()
    if type(sign) is int: # this is ElGamal
        hash = int.from_bytes(hash, "little")
        unsign = public.unsign(sign)
        unsign2 = mypow(public.g, hash, public.p)
        if unsign != unsign2: raise SignError("Неверная подпись: %s != %s" % (unsign, unsign2))
        return data

    if len(sign) == 2: # GOST
        sign, r = sign
        # public.y += 1 Стоит чуть нарушить 'y', так сразу портится проверка
        hash = int.from_bytes(hash, "little")
        print(hash)
        unsign = public.check_sign(hash, sign, r)
        print("sign:", sign)
        print("\nr:", r)
        print("\nv:", unsign)
        print()
        if r != unsign: raise SignError("Неверная подпись: %s != %s" % (r, unsign))
        return data

    sign, MPL, prefix = sign
    coder = public.coder(MPL, prefix)

    wr = Wrapper(sign, coder, invertor = True).CBC(9876543210, dec = True).ECB(dec = True).chain2data()
    decrypted = wr.data.read()
    print("decr:", decrypted.hex())
    print("hash:", hash.hex())
    if decrypted != hash: raise SignError("Неверная подпись: %s != %s" % (decrypted.hex(), hash.hex()))

    return data



def signerElGamal(data, key, output): # и для GOST пойдёт
    hash = bitcoinHash(data)
    hash = int.from_bytes(hash, "little")
    print("hash:", hash)
    sign = key.sign(hash)
    print("\nsign:", sign)

    pickle.dump(sign, output)
    key.savePublic(output)
    output.write(data)



class GOST:
    def gen(self, bits):
        max = (1 << bits) - 1
        q = randint(0, max)
        b = randint(0, max)
        p = q * b + 1
        while not primeTest(p):
            b = randint(0, max)
            p = q * b + 1
        self.q, self.p = q, p

        g = randint(1, p - 1)
        a = mypow(g, b, p)
        while a < 2:
            g = randint(1, p - 1)
            a = mypow(g, b, p)
        self.a = a

        x = randint(1, q - 1)
        y = mypow(a, x, p)
        self.x, self.y = x, y
        return self
    def print(self):
        print("~" * 77)
        print("p:", self.p, "\n")
        print("q:", self.q, "\n")
        print("a:", self.a, "\n")
        print("priv:", self.x, "\n")
        print("pub:", self.y)
        print("~" * 77)
        return self
    def sign(self, msg):
        r = sign = 0
        p, q, a, x = self.p, self.q, self.a, self.x
        while not sign:
            while not r:
                k = randint(1, q - 1)
                r = mypow(a, k, p) % q
            sign = (k * msg + x * r) % q
        return sign, r
    def check_sign(self, msg, sign, r):
        p, q, a, y = self.p, self.q, self.a, self.y
        bezu = Euclid_2(msg, q)[1]
        if bezu < 1: bezu += q

        u1, u2 = (sign * bezu) % q, (-r * bezu) % q
        return (mypow(a, u1, p) * mypow(y, u2, p)) % p % q
    def save(self, name):
        with open(name, "wb") as file: pickle.dump((self.p, self.q, self.a, self.x, self.y), file)
        return self
    def load(self, name):
        with open(name, "rb") as file: self.p, self.q, self.a, self.x, self.y = pickle.load(file)
        return self
    def savePublic(self, stream):
        stream.write(b"\3")
        pickle.dump((self.p, self.q, self.a, self.y), stream)
        return self
    def loadPublic(self, stream):
        self.p, self.q, self.a, self.y = pickle.load(stream)
        self.x = None # потеряшка (нечем будет подпись подделать)
        return self
registerKeyLoader(3, lambda stream: GOST().loadPublic(stream))



def checkGOST():
    #GOST().gen(1024).print().save("keys/GOST_1024.key")
    key = GOST().load("keys/GOST_1024.key").print()
    data = "Какие-то полезные данные/нагрузка".encode("utf-8")
    stream = BytesIO()
    signerElGamal(data, key, stream)
    print()
    print(stream.getvalue().hex())
    print("~~~")
    stream.seek(0)
    data2 = signChecker(stream)
    print(data2.decode("utf-8"))
    exit()
#checkGOST()



def checkSigner():
    coderRSA = RSAkey().load("keys/RSA1024.key").coder(2, b"\0\x10")
    coderShamir = ShamirKey().load("keys/Shamir1024.key").coder(2, b"\0\x11")
    keyElGamal = ElGamalKey().load("keys/ElGamal1024.key")
    keyGOST = GOST().load("keys/GOST_1024.key")

    name1 = "Гарри Поттер и философский камень.txt"

    for name, signName, coderOrKey in (
        (None, "signs/small_RSA.sign", coderRSA),
        (None, "signs/small_Shamir.sign", coderShamir),
        (None, "signs/small_ElGamal.sign", keyElGamal),
        (None, "signs/small_GOST.sign", keyGOST),

        (name1, "signs/big_RSA.sign", coderRSA),
        (name1, "signs/big_Shamir.sign", coderShamir),
        (name1, "signs/big_ElGamal.sign", keyElGamal),
        (name1, "signs/big_GOST.sign", keyGOST),
    ):
        print("~" * 77)
        print(signName)
        if name is None: data = "Какие-то полезные данные/нагрузка".encode("utf-8")
        else:
            with open(name, "rb") as file: data = file.read()

        isElGamal = type(coderOrKey) is not tuple
        signF = signerElGamal if isElGamal else signer

        with open(signName, "wb") as stream:
            signF(data, coderOrKey, stream)
        print("~" * 77)
        print()

def checkSignChecker():
    for fileName in os.listdir("signs"):
        signName = os.path.join("signs", fileName)
        print("~" * 77)
        print("CHECK:", signName)

        with open(signName, "rb") as stream:
            if os.stat(signName).st_size < 1024:
                print()
                print(stream.read().hex())
                print()
                stream.seek(0)
            data = signChecker(stream).decode("utf-8")
            if len(data) < 128: print("data:", data)
            else: print("data:", data[:256])
            print("it's ok!")
        print("~" * 77)
        print()



if __name__ == "__main__":
    checkSigner()
    checkSignChecker()
