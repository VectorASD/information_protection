from rgr import Graph
import socket
from uuid import uuid4
import pickle
from threading import Thread

import rgr
rgr._log = rgr._log2 = lambda *a, **kw: None # отключить логирование, иначе порвёт консоль с гигантских графов

class Alice:
    def __init__(self):
        graphA = lambda: self.loadGraph(20, 4, 10, 20)
        graphB = lambda: self.loadGraph(100, 3, 30, 50)
        graphC = lambda: self.loadGraph(1000, 3, 50, 75)
        graphD = lambda: self.loadGraph(1000, 2, 100, 100)
        graphE = lambda: self.loadGraph(10000, 2, 10, 10)
        self.base = graphA, graphB, graphC, graphD, graphE
        self.sessions = {}
        self.cache = {}
    def loadGraph(self, n, colors, MinAEP, MaxAEP):
        name = f"graphs/graph_{n}_{colors}_{MinAEP}_{MaxAEP}"
        try: return self.cache[name]
        except KeyError: pass

        try:
            #import time
            #A = time.time()
            graph = Graph().load2(name + ".pkl")
            #B = time.time()
            #graph = Graph().load(name + ".txt")
            #C = time.time()
            #print("pkl:", B - A)
            #print("txt:", C - B)
            """
    lvl: 0
pkl: 0.0019989013671875
txt: 0.0
    lvl: 1
pkl: 0.003000974655151367
txt: 0.0009989738464355469
    lvl: 2
pkl: 0.1300029754638672
txt: 0.2669987678527832
    lvl: 3
pkl: 0.1430046558380127
txt: 0.2819981575012207
    lvl: 4
pkl: 1.396998405456543
txt: 2.823002815246582

Вывод очевиден: pickle медленнее на малых значениях (графах), зато быстрее на больших
"""
            print("• Из файла:", name)
        except FileNotFoundError:
            graph = Graph().gen(n, colors, MinAEP, MaxAEP).save(name + ".txt").save2(name + ".pkl")
            print("• Новый:", name)

        self.cache[name] = graph
        return graph
    def getGraph(self, lvl, bits):
        graph = self.base[lvl]()
        #graph.print()
        publicData, privs = graph.crypto(bits)
        uuid = uuid4().int
        self.sessions[uuid] = publicData, privs
        return uuid, publicData
    def getColor(self, uuid, L, R):
        publicData, privs = self.sessions[uuid]
        assert (L, R) in publicData[3], f"Нет такого ребра: {L} {R}"
        return privs[L], privs[R]
    def handler(self, conn):
        sockfile = conn.makefile("rwb", buffering = 2048)
        uuid = None
        while True:
            try: data = pickle.load(sockfile)
            except: break
            if type(data) is int:
                assert uuid is None, "aй-яй-яй, Боб" # защита от перегрузки сессий
                lvl = data
                bits = (64, 64, 128, 256, 256)[lvl]
                uuid, _ = resp = self.getGraph(lvl, bits)
                pickle.dump(resp, sockfile)
                sockfile.flush()
            else:
                assert type(data) is tuple
                if len(data) == 3:
                    uuid2, L, R = data
                    assert uuid2 == uuid, "aй-яй-яй, Боб"
                    L, R = self.getColor(uuid, L, R)
                    pickle.dump((L, R), sockfile)
                    sockfile.flush()
                else:
                    uuid2, verdict = data
                    assert uuid2 == uuid, "aй-яй-яй, Боб"
                    assert type(verdict) is str, "Алиса принципиально принимает свои оценки только в формате строки"
                    print("Вердикт Боба:", verdict)
                    del self.sessions[uuid]
                    print("close session:", uuid) # KeepAlive (Оставаться в Живых) режим из http-протокола уже какой-то получается...
                    uuid = None # т.к. сокет тот же, а сессия уже может начаться другая ;'-}
        if uuid is not None: del self.sessions[uuid]
        print("close session:", uuid)
        sockfile.close()
        conn.close()
    def server(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # аналогично socket.socket()
        sock.bind((addr, port))
        sock.listen(4) # максимум сразу 4 Боба
        # только сейчас узнал, прямо из документации, что есть s1, s2 = socket.socketpair(),
        # но для глобальных условий не подойдёт
        print("server is up and rolled!")
        while True:
            conn, (ip, port) = sock.accept()
            print("bob connected:", ip, port)
            Thread(target = self.handler, args = (conn,)).start()

def check():
    alice = Alice()
    uuid, publicData = alice.getGraph(0, 64)
    print(uuid, publicData)
    edge = tuple(publicData[3])[0]
    L, R = alice.getColor(uuid, *edge)
    print(L, R)

alice = Alice()
alice.server("0.0.0.0", 54321)

