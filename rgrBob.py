from lab1 import mypow
import socket
import pickle
from random import sample

bobLog = open("bob.log", "w")
def print(*arr, sep = " ", end = "\n"):
    line = sep.join(map(str, arr)) + end
    __builtins__.print(line, end = "")
    bobLog.write(line)

class Bob:
    def __init__(self):
        self.verdicts = []

    def connect(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        self.sock = sock
        self.sockfile = sock.makefile("rwb", buffering = 2048)
        return self
    def close(self):
        self.sockfile.close()
        self.sock.close()
        return self

    def startLevel(self, n):
        pickle.dump(n, self.sockfile)
        self.sockfile.flush()
        self.uuid, self.publicData = pickle.load(self.sockfile)
        print("Новая сессия:", self.uuid)
        encrypted, colors, mask2, edges, n = self.publicData
        eStr = str(encrypted[:1000])
        print("Раскраска:", eStr[:10000], "..." if len(eStr) > 10000 else "")
        print("Вариантов цветов:", colors)
        print("Маска:", mask2)
        print("n:", n)
    def closeLevel(self, verdict):
        print("Вердикт:", verdict)
        pickle.dump((self.uuid, verdict), self.sockfile)
        self.sockfile.flush()
        del self.uuid, self.publicData

    def getEdge(self, L, R):
        pickle.dump((self.uuid, L, R), self.sockfile)
        self.sockfile.flush()
        privL, privR = pickle.load(self.sockfile)
        encrypted, colors, mask2, edges, n = self.publicData
        L = mypow(encrypted[L], privL, n) & mask2
        R = mypow(encrypted[R], privR, n) & mask2
        print(f"{privL} -> {L} | {privR} -> {R}")
        return L, R

    def brain(self, lvl, EiP, maxCount = 1000):
        # EiP - Edges in Percents
        assert type(lvl) is int and type(EiP) is int
        assert lvl in range(15) and EiP in range(101)

        print("~" * 77)
        print("LEVEL:", lvl)
        self.startLevel(lvl)
        edges = self.publicData[3]
        count = len(edges) * EiP // 100
        if count > maxCount: count = maxCount # в рамках разумного
        print(f"Начинаю проверку {count} рёбер из {len(edges)} всех возможных")

        for n, (L, R) in enumerate(sample(tuple(edges), count), 1):
            print("• рёбра:", L, R)
            L, R = self.getEdge(L, R)
            if L == R:
                self.closeLevel("Алиса схитрила")
                verdict = f"LEVEL: {lvl} -> Протестировано {n}/{count}(= 10%) рёбер. Алиса схитрила"
                break
        else:
            self.closeLevel("Алиса хорошая")
            verdict = f"LEVEL: {lvl} -> Протестировано {n}/{count}(= 10%) рёбер. Алиса хорошая"
        self.verdicts.append(verdict)

        print("~" * 77)
        return self

bob = Bob().connect("localhost", 54321)
for lvl in range(6): # тестируем первые 6 уровней по 5 раз для наглядности
    for i in range(5): bob.brain(lvl, 10)
    bob.verdicts.append("~~~")
for lvl in range(6, 15): bob.brain(lvl, 10)
#bob.brain(1, 10).brain(2, 10).brain(3, 10).brain(4, 10)
bob.close()

print("=" * 77)
print("    Что скопилось в памяти Боба:")
for verdict in bob.verdicts: print(verdict)
print("=" * 77)

bobLog.close()
