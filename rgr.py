from lab2 import RSAkey
from random import randint, sample, choice
import pickle

class Graph:
    def gen(self, n, colors, MinAEP):
        # MinAEP = Minimum Additional Edges in Percent
        if not (type(n) is int and type(colors) is int and type(MinAEP) is int):
            raise TypeError("Неверные типы входных данных gen - генератора цветных правильных графов")
        if not (n >= 5 and colors >= 2 and MinAEP in range(101)):
            raise ValueError("Неверные входные данные gen - генератора цветных правильных графов")

        Vcolors = [None] * n # vertex colors
        indexes = sample(range(n), n)
        # sample просто перемешивает range(n) и выдаёт первые n элементов,
        # т.е. на выходе ВСЕГДА перестановка от 0 до n-1
        assert len(set(indexes)) == n, "Не перестановка :/"

        root = indexes.pop(0)
        Vcolors[root] = randint(0, colors-1)
        edges = set()
        used = [root]
        for L in indexes: # в L всегда попадает НЕ занятая вершина
            R = choice(used) # в R всегда попадает занятая вершина
            used.append(L)
            color = Vcolors[R]
            color2 = randint(0, colors-2)
            if color2 >= color: color2 += 1 # color2 будет гарантированно от 0 до colors-1 и не равен color
            Vcolors[L] = color2
            edges.add((min(L, R), max(L, R)))
        assert all(color is not None for color in Vcolors), "есть неразукрашенные вершины :/"
        assert all(Vcolors[L] != Vcolors[R] for L, R in edges), "это НЕ правильное дерево :/"
        # теперь гарантируется, что Vcolors полностью заполнен цветами от 0 до colors-1,
        # а также edges - правильное, с точки зрения раскраски, ДЕРЕВО (из каждой веришины существует путь в каждую)
        self.Vcount = n
        self.edges = edges
        self.colors = colors
        self.Vcolors = tuple(Vcolors)
        self.source = f"gen({n}, {colors}, {MinAEP})"
        print(sorted(edges))
        print(Vcolors)

        if MinAEP: # при MinAEP == 0 нет смысла искать edges2, следовательно, и применять его
            edges2 = []
            for L in range(n - 2):
                for R in range(L + 1, n):
                    if (L, R) in edges: continue
                    if Vcolors[L] == Vcolors[R]: continue
                    edges2.append((L, R))
            print("max дополнительных рёбер (MaxAE):", len(edges2))
            # КАЖДОЕ и хотябы одно ребро в edges2 уже ломает свойство дерева в edges,
            # не нарушая при этом правильность расраски

            MinAE = len(edges2) * MinAEP // 100 # len(edges2) <-> MaxAE
            AE = randint(MinAE, len(edges2))
            print(f"AE: {MinAE}..{len(edges2)} -> {AE}")
            edges.update(sample(edges2, AE)) # ;'-} просто одной строчкой
            print(sorted(edges))
            assert all(Vcolors[L] != Vcolors[R] for L, R in edges), "это НЕ правильный граф :/"

        assert all(L < R for L, R in edges), "во всех рёбрах, во избежание избыточности, L обязаны быть меньше R"
        return self

    def save(self, name): # человекочитаемый, как по заданию
        try: self.Vcount; self.edges; self.colors; self.Vcolors; self.source
        except AttributeError: raise Exception("Нельзя сохранить граф-пустышку. Используйте gen, load или load2")
        with open(name, "w") as file:
            writer = file.write
            writer(f"{self.Vcount} {len(self.edges)}\n")
            for L, R in self.edges: writer(f"{L} {R}\n")
            writer(f"{self.colors}\n")
            writer(" ".join(map(str, self.Vcolors)))
        return self

    def load(self, name): # обратная функция к save
        for attr in ("Vcount", "edges", "colors", "Vcolors", "source"):
            try:
                getattr(self, attr)
                raise Exception("Нельзя через load() загрузить граф после gen, load или load2. Создайте новый граф")
            except AttributeError: pass

        with open(name, "r") as file:
            readNums = lambda: map(int, file.readline().split())
            self.Vcount, m = readNums()
            self.edges = set(tuple(readNums()) for i in range(m))
            self.colors = int(file.readline())
            self.Vcolors = tuple(readNums())
        self.source = f"load({name!r})"
        self.check()
        return self

    def check(self):
        n, edges, colors, Vcolors = self.Vcount, self.edges, self.colors, self.Vcolors
        Range = range(n)
        assert all(L in Range and R in Range and L != R for L, R in edges), "недопустимые значения L и R"
        assert all(L < R for L, R in edges), "во всех рёбрах, во избежание избыточности, L обязаны быть меньше R"

        assert all(Vcolors[L] != Vcolors[R] for L, R in edges), "это НЕ правильный граф :/"
        assert n >= 5, "должно быть, по крайней мере, 5 вершин"
        assert colors >= 2, "должно быть, по крайней мере, 2 цвета"
        R = range(colors)
        assert all(color in R for color in Vcolors), "все цвета раскраски должны быть от 0 до colors-1"

    def print(self):
        print("~" * 77)
        print(f"Источник: {self.source}")
        print(f"Всего вершин: {self.Vcount}")
        print(f"Рёбра: {sorted(self.edges)}")
        print(f"Вариантов цветов: {self.colors}")
        print(f"Раскрашка вершин: {self.Vcolors}")
        print("~" * 77)

    def __eq__(L, R):
        return L.Vcount == R.Vcount and L.edges == R.edges and L.colors == R.colors and L.Vcolors == R.Vcolors

    def save2(self, name): # бинарный вариант, с элементом pickle, проще и быстрее пишется, надёжнее, ̶к̶о̶м̶п̶а̶к̶т̶н̶е̶е̶
        try: self.Vcount; self.edges; self.colors; self.Vcolors; self.source
        except AttributeError: raise Exception("Нельзя сохранить граф-пустышку. Используйте gen, load или load2")
        with open(name, "wb") as file: pickle.dump((self.Vcount, self.edges, self.colors, self.Vcolors), file)
        return self

    def load2(self, name): # обратная функция к save2
        for attr in ("Vcount", "edges", "colors", "Vcolors", "source"):
            try:
                getattr(self, attr)
                raise Exception("Нельзя через load() загрузить граф после gen, load или load2. Создайте новый граф")
            except AttributeError: pass

        with open(name, "rb") as file: self.Vcount, self.edges, self.colors, self.Vcolors = pickle.load(file)
        self.source = f"load2({name!r})"
        self.check()
        return self

def checkError(func):
    try: func()
    except Exception as e:
        print("ok error:", e)
        return
    raise Exception("Нет исключения там, где должно быть")

def tester():
    graph = Graph().gen(20, 4, 10).save("graphs/first.txt")
    checkError(lambda: Graph().save("error.txt"))
    checkError(lambda: graph.load(""))

    graph2 = Graph().load("graphs/first.txt")
    graph.print()
    graph2.print()

    assert graph == graph2, "Проблемы в сравнителе графов"
    graph2.edges.add((0, 0)) # такого быть не может, поэтому ВСЯКО добавится, так ещё и check завалит гарантированно
    assert graph != graph2, "Проблемы в сравнителе графов"
    checkError(graph2.check)

    # Яндекс-Нейро ответила, что файлы формата pickle должны называться как *.pkl - официальная версия
    graph.save2("graphs/first.pkl")
    graph3 = Graph().load2("graphs/first.pkl")
    graph3.print()
    assert graph == graph3, "Ошибка сериализации или десериализации pickle :/"
    graph3.colors = 1
    assert graph != graph3, "Проблемы в сравнителе графов"
    checkError(graph3.check)



tester()
