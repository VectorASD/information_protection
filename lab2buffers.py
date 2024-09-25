from random import randint
import io
import os
from lab2 import ShamirKey, ElGamalKey, GVkey, RSAkey
from time import time



#os.chdir(os.path.split(__file__)[0])

def Coder(e, e2, n, MPL, prefix):
  # MPL - minimal padding length
  enc = lambda msg: pow(msg, e, n)
  dec = lambda msg: pow(msg, e2, n)
  return enc, dec, n.bit_length(), MPL, prefix, n

class IOGenerator(io.RawIOBase):
  def __init__(self, gen, blockL):
    self._closed = False
    self.gen = iter(gen)
    self.blockL = blockL
  @property
  def closed(self): return self._closed
  def close(self): self._closed = True

  def readable(self): return True
  def seekable(self): return False
  def readinto(self, b):
    if not isinstance(b, memoryview): b = memoryview(b)
    b = b.cast('B')
    #print("ri:", b, len(b), len(b) % 9)
    pos = 0
    for i in range(len(b) // self.blockL):
      try: data = next(self.gen)
      except StopIteration: data = b""
      if not data:
        #self._closed = True
        break
      pos2 = pos + len(data)
      b[pos:pos2] = data
      pos = pos2
    return pos

def makeBuffer(gen, blockL, resL):
  buff = io.BufferedReader(IOGenerator(gen, blockL), blockL)
  buff.Length = resL
  return buff

"""
barr = bytearray(b"abcdefghijklmnopqrst" * 5000000)
for i in range(20):
  barr2 = barr[5:]
  print(i)
  barr2[0] = ord("Z")
mv = memoryview(barr)
for i in range(20):
  barr2 = mv[i * 4:]
  print(barr2)
  barr2[i % 3] = ord("_")
  barr2[3] = ord("|")
print(barr[:50])
exit()
"""

def data2chain(data, coder):
  def gen(data, coder):
    MPL, prefix = coder[3:5]
    dL = data.Length
    blockL = (coder[2] + 5) // 8
    innerL = blockL - (len(prefix) + MPL + 1)
    bN = (dL + innerL - 1) // innerL
    min_dL = dL // bN
    full = (bN - (bN * innerL - dL)) % bN
    yield blockL, blockL * bN
    for b in range(bN):
      L = min_dL + (b < full)    
      yield bytes((
        *prefix,
        *(randint(1, 255) for _ in range(innerL - L + MPL)),
        0,
        *data.read(L)
      ))
  it = iter(gen(data, coder))
  blockL, resL = next(it)
  return makeBuffer(it, blockL, resL)

def chain2data(chain, coder):
  def gen(chain, blockL, prefix):
    pL = len(prefix)
    while True:
      block = chain.read(blockL)
      if not block: break
      assert block[:pL] == prefix, "Возможно, ключ не тот"
      yield block[pL:].split(b"\0", 1)[1]
  blockL = (coder[2] + 5) // 8
  gen = gen(chain, blockL, coder[4])
  return makeBuffer(gen, blockL, 0)

def ECB(data, coder, dec = False, invertor = False):
  def ECB(data, blockL, crypto):
    pos = 0
    while True:
      block = data.read(blockL)
      if not block: break
      yield int.to_bytes(crypto(int.from_bytes(block, "big")), blockL, "big")
  def ECB_ElG(data, blockL, crypto):
    pos = 0
    block2 = b""
    while True:
      block = data.read(blockL)
      if dec: block2 = data.read(blockL)
      if not block or dec and not block2: break
      for b in crypto(int.from_bytes(block, "big"), int.from_bytes(block2, "big")):
        yield int.to_bytes(b, blockL, "big")
  blockL = (coder[2] + 5) // 8
  BPC = coder[6] # blocks per crypto
  gen = (ECB_ElG if BPC == 2 else ECB)(data, blockL, coder[bool(dec) ^ bool(invertor)])
  return makeBuffer(gen, blockL, data.Length)

def CBC(data, impurity, coder, dec = False, invertor = None):
  prevBlock = impurity
  def CBC(data, n, blockL, crypto):
    nonlocal prevBlock
    #print("•", int.to_bytes(maxPB, blockL, "big").hex())
    while True:
      block = data.read(blockL)
      if not block: break
      block = int.from_bytes(block, "big")
      if dec:
        enc = (crypto(block) - prevBlock) % n
        prevBlock = block
      else:
        #a, b = int.to_bytes(block, blockL, "big").hex(), prevBlock
        enc = prevBlock = crypto((block + prevBlock) % n)
        #decc = int.to_bytes((coder[1](enc) - b) % n, blockL, "big").hex()
        #print(a, "->", int.to_bytes(enc, blockL, "big").hex(), "->", decc, a == decc)
      yield int.to_bytes(enc, blockL, "big")
  def CBC_ElG(data, n, blockL, crypto):
    nonlocal prevBlock
    while True:
      block = data.read(blockL)
      if not block: break
      block = int.from_bytes(block, "big")
      if dec:
        block2 = data.read(blockL)
        if not block2: break
        block2 = int.from_bytes(block2, "big")
        encs = *((b - prevBlock) % n for b in crypto(block, block2)),
        prevBlock = block ^ block2
      else:
        encs = crypto((block + prevBlock) % n, None)
        prevBlock = encs[0] ^ encs[1]
      for b in encs: yield int.to_bytes(b, blockL, "big")
  blockL = (coder[2] + 5) // 8
  BPC = coder[6] # blocks per crypto
  gen = (CBC_ElG if BPC == 2 else CBC)(data, coder[5], blockL, coder[bool(dec) ^ bool(invertor)])
  return makeBuffer(gen, blockL, data.Length)





class Wrapper:
  def __init__(self, data, coder = None, invertor = False):
    if isinstance(data, io.IOBase):
      if isinstance(data, io.FileIO):
        data.Length = os.stat(data.name).st_size
      elif isinstance(data, io.BufferedReader) and isinstance(data.raw, io.FileIO):
        data.Length = os.stat(data.raw.name).st_size
    else:
      if isinstance(data, str): data = data.encode("utf-8")
      if not isinstance(data, bytes): data = bytes(data)
      L, data = len(data), io.BytesIO(data)
      data.Length = L
    self.data = data
    if coder is not None: self.coder = coder
    if invertor is not None: self.invertor = invertor
  def read(self):
    return self.data.read()
  def clone(self):
    data = self.data.read()
    self.data = data2 = io.BytesIO(data)
    data2.Length = len(data)
    return Wrapper(data, self.coder, self.invertor)
  def data2chain(self, coder = None):
    new = data2chain(self.data, self.coder if coder is None else coder)
    self.__init__(new, invertor = None)
    return self
  def chain2data(self, coder = None):
    new = chain2data(self.data, self.coder if coder is None else coder)
    self.__init__(new, invertor = None)
    return self
  def ECB(self, coder = None, dec = False, invertor = None):
    new = ECB(self.data, self.coder if coder is None else coder, dec, self.invertor if invertor is None else invertor)
    self.__init__(new, invertor = None)
    return self
  def CBC(self, impurity, coder = None, dec = False, invertor = None):
    new = CBC(self.data, impurity, self.coder if coder is None else coder, dec, self.invertor if invertor is None else invertor)
    self.__init__(new, invertor = None)
    return self
  def save(self, name, chunkL = 1024):
    data = self.data
    with open(name, "wb") as file:
      while True:
        chunk = data.read(chunkL)
        if not chunk: break
        file.write(chunk)





def tests():
  coder = Coder(65537, 5309611821765868125, 11174926311377982577,
    2, b"\2")
  coder2 = Coder(65537, 30531945418473611754235620517209409495319119269239924395672581216826461813815472809725918295516106756014102712617593987229247693166252522272705286260612264235461277174748461998448659407587057606282067438404889326592556999029877938366893023503882428090017951042732480945818066254211116691072388038466066283817, 117835940574200877070687230542156119786510165452457271369129848372130959772217457248160150010790830249625831781215432373891007954009580799257186679295784243466542142825214117575545807093939085127170425634740507765636460493733127118150715418690595261823508778243007181601898488277129952079416943784083186400983,
    2, b"\2")

  wr = Wrapper(range(100), coder)
  print(wr.data2chain().clone().read().hex())
  print("~")
  print(wr.chain2data().read().hex())
  print("~" * 77)

  wr = Wrapper(range(100), coder)
  print(wr.data2chain().data2chain().clone().read().hex())
  print("~")
  print(wr.chain2data().chain2data().read().hex())
  print("~" * 77)

  wr = Wrapper(range(100), coder)
  print(wr.data2chain().ECB().clone().read().hex())
  print("~")
  print(wr.ECB(dec = True).chain2data().read().hex())
  print("~" * 77)

  wr = Wrapper(range(100), coder)
  print(wr.data2chain().ECB().ECB().clone().read().hex())
  print("~")
  print(wr.ECB(dec = True).ECB(dec = True).chain2data().read().hex())
  print("~" * 77)

  wr = Wrapper(range(100), coder)
  print(wr.data2chain().ECB(dec = True).clone().read().hex())
  print("~")
  print(wr.ECB().chain2data().read().hex())
  print("~" * 77)

  wr = Wrapper(range(100), coder)
  print(wr.data2chain().CBC(123).clone().read().hex())
  print("~")
  print(wr.CBC(123, dec = True).chain2data().read().hex())
  print("~" * 77)





def checker():
  coder = RSAkey().load("keys/RSA64.key").coder(2, b"\1")
  coder2 = RSAkey().load("keys/RSA1024.key").coder(2, b"\2")
  coder3 = ShamirKey().load("keys/Shamir64.key").coder(2, b"\3")
  coder4 = ShamirKey().load("keys/Shamir1024.key").coder(2, b"\4")
  coder5 = GVkey().load("keys/GV64.key").coder(2, b"\5")
  coder6 = GVkey().load("keys/GV1024.key").coder(2, b"\6")
  coder7 = ElGamalKey().load("keys/ElGamal64.key").coder(2, b"\5")
  coder8 = ElGamalKey().load("keys/ElGamal1024.key").coder(2, b"\6")

  for coder, name, name2, name3 in (
    (coder, "img.jpg", "prod/RSA_imgA.enc", "prod/RSA_imgA_dec.jpg"),
    (coder2, "img.jpg", "prod/RSA_imgB.enc", "prod/RSA_imgB_dec.jpg"),
    (coder, "img2.jpg", "prod/RSA_img2A.enc", "prod/RSA_img2A_dec.jpg"),
    (coder2, "img2.jpg", "prod/RSA_img2B.enc", "prod/RSA_img2B_dec.jpg"),
    
    (coder3, "img.jpg", "prod/Shamir_imgA.enc", "prod/Shamir_imgA_dec.jpg"),
    (coder4, "img.jpg", "prod/Shamir_imgB.enc", "prod/Shamir_imgB_dec.jpg"),
    (coder3, "img2.jpg", "prod/Shamir_img2A.enc", "prod/Shamir_img2A_dec.jpg"),
    (coder4, "img2.jpg", "prod/Shamir_img2B.enc", "prod/Shamir_img2B_dec.jpg"),
    
    (coder5, "img.jpg", "prod/GV_imgA.enc", "prod/GV_imgA_dec.jpg"),
    (coder6, "img.jpg", "prod/GV_imgB.enc", "prod/GV_imgB_dec.jpg"),
    (coder5, "img2.jpg", "prod/GV_img2A.enc", "prod/GV_img2A_dec.jpg"),
    (coder6, "img2.jpg", "prod/GV_img2B.enc", "prod/GV_img2B_dec.jpg"),
    
    (coder7, "img.jpg", "prod/ElGamal_imgA.enc", "prod/ElGamal_imgA_dec.jpg"),
    (coder8, "img.jpg", "prod/ElGamal_imgB.enc", "prod/ElGamal_imgB_dec.jpg"),
    (coder7, "img2.jpg", "prod/ElGamal_img2A.enc", "prod/ElGamal_img2A_dec.jpg"),
    (coder8, "img2.jpg", "prod/ElGamal_img2B.enc", "prod/ElGamal_img2B_dec.jpg"),
  ):
    GV = name2.startswith("prod/GV")
    if GV: coder[7].reset()

    print(name, name2, name3)
    start = time()
    with open(name, "rb") as file:
      if GV: wr = Wrapper(file, coder).data2chain().CBC(987654321)
      else: wr = Wrapper(file, coder).data2chain().ECB().CBC(123456789)
      print("file tell:", file.tell()) # 0 ;'-}
      wr.save(name2)
      print("file tell:", file.tell(), time() - start, "s.")

    start = time()
    with open(name2, "rb") as file:
      if GV: wr = Wrapper(file, coder).CBC(987654321, dec = True).chain2data()
      else: wr = Wrapper(file, coder).CBC(123456789, dec = True).ECB(dec = True).chain2data()
      print("file tell:", file.tell()) # 0 ;'-}
      wr.save(name3)
      print("file tell:", file.tell(), time() - start, "s.")
    if GV: print("Counters:", coder[-1].encC, coder[-1].decC) 
    print("~" * 77)

if __name__ == "__main__": checker()

"""
data = io.BytesIO(bytes(range(100)))
data.Length = 100

chain = data2chain(data, coder)
enc = b''.join(ECB(chain, coder))
print(enc.hex(), len(enc))

data = io.BytesIO(enc)
data.Length = len(enc)

dec = b''.join(chain2data(ECB(data, coder, True), coder))
print(tuple(dec))
"""
