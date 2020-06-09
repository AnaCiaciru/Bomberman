import copy
import math
import time


# inainte elem_identice()

def castigator(lista):
    """ Primeste o lista si returneaza
    -> simbolul jucatorului castigator (daca lista contine doar un simbol de jucator)
    -> sau False (daca a fost remiza sau daca nu s-a terminat jocul)
    """
    mt = set(lista)  # pot avea simbolurile "#,1,2, ,p"
    if '1' in mt and '2' not in mt:
        return '1'
    if '2' in mt and '1' not in mt:
        return '2'
    return False


"""-------------------------- Clasa JOC -----------------------------------------------------------------------------"""


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    NR_LINII = 22
    NR_COLOANE = 22
    JMIN = None
    JMAX = None
    PERETE = '#'  # configuratia ptr blocaj
    GOL = ' '
    matr = []  # tabla de joc
    protectii_JMIN = 0  # numarul de protectii acumulate
    protectii_JMAX = 0
    bomba_JMIN = 0  # nu au bombe plasate
    bomba_JMAX = 0
    bi, bj = -1, -1  # coordonatele bombelor
    Bi, Bj = -1, -1
    k = 0  # nr ul de mutari

    def __init__(self, tabla=None, ):
        if tabla is None:
            self.matr = [Joc.PERETE] * self.NR_LINII * self.NR_COLOANE
        else:
            self.matr = tabla
            self.NR_LINII = len(tabla)
            self.NR_COLOANE = len(tabla[0])

    def __str__(self):
        str = ""
        for i in range(self.NR_LINII):
            for s in self.matr[i]:
                str += s
        return str

    def final(self):
        lista = []
        for i in range(self.NR_LINII):
            x = set(self.matr[i])  # adaugam doar caracterele unice de pe fiecare linie
            for j in x:
                lista.append(j)
        return castigator(lista)

    def pozitii(self, jucator):
        """
        stiu sigur ca el este pe tabla
        :param jucator: simbolul jucatorului
        :return: un tuplu (i_linie, j_coloana) - pozitia jucatorului
        """

        for i in range(self.NR_LINII):
            if jucator in self.matr[i]:
                for j in range(self.NR_COLOANE):
                    if self.matr[i][j] == jucator:
                        return i, j
        return None  # in caz de orice

    def pozitie_valida(self, i, j):
        """
        :return: False daca iese din tabla sau intra in perete
        """
        if 0 <= i < self.NR_LINII and 0 <= j < self.NR_COLOANE:
            if self.matr[i][j] == self.GOL or self.matr[i][j] == 'p':
                return True
        return False

    def explodeaza_bomba(self, l_curent, c_curent, simbol):
        # pe pozitia (l_curent, j_curent) se afla sigur o bomba
        self.matr[l_curent][c_curent] = self.GOL

        for l in range(self.NR_LINII):
            chr = self.matr[l][c_curent]
            if chr not in ['p', 'b', 'B', '1', '2', '\n']:
                self.matr[l][c_curent] = self.GOL

            if simbol == self.JMIN:
                if self.protectii_JMIN > 0:
                    self.protectii_JMIN -= 1
            else:
                if self.protectii_JMAX > 0:
                    self.protectii_JMAX -= 1

        for c in range(self.NR_COLOANE):
            chr = self.matr[l_curent][c]
            if chr not in ['p', 'b', 'B', '1', '2', '\n']:
                self.matr[l_curent][c] = self.GOL

            if simbol == self.JMIN:
                if self.protectii_JMIN > 0:
                    self.protectii_JMIN -= 1
            else:
                if self.protectii_JMAX > 0:
                    self.protectii_JMAX -= 1

    def cauta_explozie(self, i_juc, j_juc, jucator):
        # functia verifica daca este o bomba prin apropiere si o explodeaza

        lin = [-1, 0, 1, 0]
        col = [0, -1, 0, 1]
        if jucator == "JMIN":
            bomba = 'B'
            simbol = self.JMIN
        else:
            bomba = 'b'
            simbol = self.JMAX

        for i in range(4):
            # calculez coordonatele pozitiei posibilei bombe
            l_curent = lin[i] + i_juc
            c_curent = col[i] + j_juc
            if self.pozitie_valida(l_curent, c_curent):
                if self.matr[l_curent][c_curent] == bomba:
                    self.explodeaza_bomba(l_curent, c_curent, simbol)

    def mutari_joc(self, jucator):
        """
        :param jucator: simbolul jucatorului care face mutarea
        :return: o lista de configuratii posibile
        """

        # gasesc pozitia jucatorului
        poz_lin, poz_col = self.pozitii(jucator)

        """
         se poate deplasa w - sus, a - stanga, s - jos, d - dreapta
         
            1. configuratiile in care nu am bomba
            2. configuratiile cu bomba 
            
         - pot lua protectie
         - pot ajunge langa o bomba O_O !!!!!!!!!   
        """

        l_mutari = []

        # cu cat adun ca sa ma pot deplasa
        lin = [-1, 0, 1, 0]
        col = [0, -1, 0, 1]

        for i in range(4):
            # calculez coordonatele pozitiei posibile deplasari
            l_curent = lin[i] + poz_lin
            c_curent = col[i] + poz_col

            # daca ma pot deplasa acolo
            if self.pozitie_valida(l_curent, c_curent):

                # e posibil sa iau o protectie
                if self.matr[l_curent][c_curent] == 'p':
                    self.protectii_JMAX += 1

                if self.k == 2:
                    # configuratie in care las bomba
                    if self.bomba_JMAX == 1:
                        self.explodeaza_bomba(self.Bi, self.Bj, self.JMAX)

                    self.Bi, self.Bj = poz_lin, poz_col
                    temp = copy.deepcopy(self)  # fac o copie la tabla
                    temp.matr[poz_lin][poz_col] = 'B'  # plasez o bomba
                    temp.matr[l_curent][c_curent] = jucator  # marchez pozitia urmatoare
                    temp.bomba_JMAX = 1  # marchez faptul ca am lasat o bomba
                    temp.k = 0
                    l_mutari.append(temp)
                else:
                    # 1. configuratie in care nu las bomba
                    temp = copy.deepcopy(self)  # fac o copie la tabla
                    temp.matr[poz_lin][poz_col] = self.GOL  # eliberez pozitia
                    temp.matr[l_curent][c_curent] = jucator  # marchez pozitia urmatoare
                    l_mutari.append(temp)
        return l_mutari

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        if t_final == Joc.JMAX:
            return 99 + adancime
        elif t_final == Joc.JMIN:
            return -99 - adancime
        elif t_final == 'remiza':
            return 0
        else:
            i1, j1 = self.pozitii('1')
            i2, j2 = self.pozitii('2')

            # distanta Manhattan intre acest jucator si cel oponent
            return abs(i1 - i2) + abs(j1 - j2)

            # distanta euclidiana
           # return math.sqrt((i1 - i2)**2 + (j1-j2)**2)


"""-------------------------- Clasa STARE ---------------------------------------------------------------------------"""


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari_joc() care ofera lista cu
    configuratiile posibile in urma mutarii unui jucator
    """

    ADANCIME_MAX = None

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc  # un obiect de tip Joc => „tabla_joc.matr”
        self.j_curent = j_curent  # simbolul jucatorului curent

        # adancimea in arborele de stari
        #	(scade cu cate o unitate din „tata” in „fiu”)
        self.adancime = adancime

        # scorul starii (daca e finala, adica frunza a arborelui)
        # sau scorul celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []  # lista va contine obiecte de tip Stare

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def jucator_opus(self):
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def mutari_stare(self):
        l_mutari = self.tabla_joc.mutari_joc(self.j_curent)
        juc_opus = self.jucator_opus()

        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]
        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Jucator curent:" + self.j_curent + ")\n"
        return sir


"""------------------------ Algoritmul MinMax -----------------------------------------------------------------------"""


def min_max(stare):
    # Daca am ajuns la o frunza a arborelui, adica:
    # - daca am expandat arborele pana la adancimea maxima permisa
    # - sau daca am ajuns intr-o configuratie finala de joc
    if stare.adancime == 0 or stare.tabla_joc.final():
        # calculam scorul frunzei apeland "estimeaza_scor"
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # Altfel, calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari_stare()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)

    # actualizez scorul „tatalui” = scorul „fiului” ales
    stare.scor = stare.stare_aleasa.scor
    return stare


"""------------------------ Algoritmul Alpha-Beta -------------------------------------------------------------------"""


def alpha_beta(alpha, beta, stare):
    # Daca am ajuns la o frunza a arborelui, adica:
    # - daca am expandat arborele pana la adancimea maxima permisa
    # - sau daca am ajuns intr-o configuratie finala de joc
    if stare.adancime == 0 or stare.tabla_joc.final():
        # calculam scorul frunzei apeland "estimeaza_scor"
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # Conditia de retezare:
    if alpha >= beta:
        return stare  # este intr-un interval invalid, deci nu o mai procesez

    # Calculez toate mutarile posibile din starea curenta (toti „fiii”)
    stare.mutari_posibile = stare.mutari_stare()

    if stare.j_curent == Joc.JMAX:
        scor_curent = float('-inf')  # scorul „tatalui” de tip MAX

        # pentru fiecare „fiu” de tip MIN:
        for mutare in stare.mutari_posibile:
            # calculeaza scorul fiului curent
            stare_noua = alpha_beta(alpha, beta, mutare)

            # incerc sa imbunatatesc (cresc) scorul si alfa
            # „tatalui” de tip MAX, folosind scorul fiului curent
            if scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:  # verific conditia de retezare
                    break  # NU se mai extind ceilalti fii de tip MIN


    elif stare.j_curent == Joc.JMIN:
        scor_curent = float('inf')  # scorul „tatalui” de tip MIN

        # pentru fiecare „fiu” de tip MAX:
        for mutare in stare.mutari_posibile:
            stare_noua = alpha_beta(alpha, beta, mutare)

            # incerc sa imbunatatesc (scad) scorul si beta
            # „tatalui” de tip MIN, folosind scorul fiului curent
            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:  # verific conditia de retezare
                    break  # NU se mai extind ceilalti fii de tip MAX

    # actualizez scorul „tatalui” = scorul „fiului” ales
    stare.scor = stare.stare_aleasa.scor

    return stare


"""------------------------------------------------------------------------------------------------------------------"""


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()
    if (final):
        if (final == "remiza"):
            print("Remiza!")
        else:
            print("A castigat " + final)

        return True

    return False


def main():
    # initializare algoritm
    global adancime, i_jucator, j_jucator, bomba, i_init, j_init
    raspuns_valid = False
    while not raspuns_valid:
        tip_algoritm = input("Ce algoritm ati dori sa folosim? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-Beta\n ")
        if tip_algoritm == "exit":
            return
        if tip_algoritm in ['1', '2']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")

    print("\n")
    # initializare ADANCIME_MAX
    raspuns_valid = False
    while not raspuns_valid:
        print("La ce nivel ati dori sa jucati?")
        print("usor, mediu, greu")
        option = input("Nivelul: ")
        if option == "exit":
            return
        if option in ["usor", "mediu", "greu"]:
            if option == "usor":
                adancime = 5
            if option == "mediu":
                adancime = 8
            if option == "greu":
                adancime = 12
            Stare.ADANCIME_MAX = adancime
            raspuns_valid = True
        else:
            print("Trebuie sa introduceti usor, mediu sau greu.")
    print("\n")

    # initializare jucatori
    raspuns_valid = False
    while not raspuns_valid:
        Joc.JMIN = input("Doriti sa jucati cu 1 sau cu 2? ").lower()
        if Joc.JMIN == "exit":
            return
        if (Joc.JMIN in ['1', '2']):
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie 1 sau 2.")
    Joc.JMAX = '2' if Joc.JMIN == '1' else '1'
    print("\n")

    # initializare tabla
    fin = open("harta.txt", "r")
    harta = []
    linie = fin.readline()
    while linie:
        harta.append(list(map(str, linie)))
        linie = fin.readline()

    tabla_curenta = Joc(harta)
    print("Tabla initiala")
    print(tabla_curenta)

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, '1', Stare.ADANCIME_MAX)

    nr_linii = stare_curenta.tabla_joc.NR_LINII
    nr_coloane = stare_curenta.tabla_joc.NR_COLOANE
    while True:
        if stare_curenta.j_curent == Joc.JMIN:
            # muta jucatorul
            raspuns_valid = False
            while not raspuns_valid:
                try:
                    t_inainte = int(round(time.time() * 1000))
                    print("w - sus, s - jos, d - dreapta, a - stanga ")
                    mutare = input("Mutarea ta = ")
                    if mutare == "exit":
                        return
                    i_jucator, j_jucator = stare_curenta.tabla_joc.pozitii(Joc.JMIN)
                    i_init, j_init = i_jucator, j_jucator

                    if mutare == "w":
                        i_jucator -= 1
                    if mutare == "s":
                        i_jucator += 1
                    if mutare == "d":
                        j_jucator += 1
                    if mutare == "a":
                        j_jucator -= 1

                    if stare_curenta.tabla_joc.pozitie_valida(i_jucator, j_jucator):
                        raspuns_valid = True
                    else:
                        print("Exista deja un simbol in pozitia ceruta.")

                except ValueError:
                    print("Simbolul introdus trebuie sa fie w, s, d, sau a!")

            # dupa iesirea din while sigur am valide atat linia cat si coloana
            # deci pot plasa simbolul pe "tabla de joc"

            raspuns_valid = False
            while not raspuns_valid:
                bomba = input("Lasi bomba? (da/nu)")
                if bomba == "exit":
                    return
                if bomba in ["da", "nu"]:
                    raspuns_valid = True
                else:
                    print("Raspunsul nu este valid!")

            # verific daca vrea bomba
            if bomba == "da":
                if stare_curenta.tabla_joc.bomba_JMIN == 0:  # nu am o bomba plasata deja
                    stare_curenta.tabla_joc.matr[i_init][j_init] = 'b'
                    stare_curenta.tabla_joc.bi = i_init
                    stare_curenta.tabla_joc.bj = j_init
                    stare_curenta.tabla_joc.bomba_JMIN = 1
                else:
                    print("Aveti deja o bomba plasata!")
                    raspuns_valid = False
                    while not raspuns_valid:
                        option = input("Doriti sa activati bomba si sa plasati una noua? (da/nu)")
                        if option == "exit":
                            return
                        if option in ["da", "nu"]:
                            raspuns_valid = True
                    if option == "da":
                        stare_curenta.tabla_joc.explodeaza_bomba(stare_curenta.tabla_joc.bi, stare_curenta.tabla_joc.bj,
                                                                 "JMIN")
                        stare_curenta.tabla_joc.bi = i_init
                        stare_curenta.tabla_joc.bj = j_init
                        stare_curenta.tabla_joc.matr[i_init][j_init] = 'b'
                    else:
                        stare_curenta.tabla_joc.matr[i_init][j_init] = stare_curenta.tabla_joc.GOL
            else:
                stare_curenta.tabla_joc.matr[i_init][j_init] = stare_curenta.tabla_joc.GOL

            t_dupa = int(round(time.time() * 1000))
            print("Jucatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
            print("Scorul ptr jucator este: ", stare_curenta.scor)

            # verific daca am o protectie
            if stare_curenta.tabla_joc.matr[i_jucator][j_jucator] == 'p':
                stare_curenta.tabla_joc.protectii_JMIN += 1
            stare_curenta.tabla_joc.matr[i_jucator][j_jucator] = Joc.JMIN

            # acum vad daca avem explozie
            stare_curenta.tabla_joc.cauta_explozie(i_jucator, j_jucator, "JMIN")

            # afisarea starii jocului in urma mutarii utilizatorului
            print("\nTabla dupa mutarea jucatorului")
            print(str(stare_curenta))

            # testez daca jocul a ajuns intr-o stare finala
            # si afisez un mesaj corespunzator in caz ca da
            if (afis_daca_final(stare_curenta)):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = stare_curenta.jucator_opus()

        # --------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))
            stare_curenta.tabla_joc.k += 1
            if tip_algoritm == '1':
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm==2
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc

            i_jucator, j_jucator = stare_curenta.tabla_joc.pozitii(Joc.JMAX)
            stare_curenta.tabla_joc.cauta_explozie(i_jucator, j_jucator, "JMAX")

            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
            print("Scorul ptr calculator este: ", stare_curenta.scor)
            if (afis_daca_final(stare_curenta)):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = stare_curenta.jucator_opus()


if __name__ == "__main__":
    t_inainte = int(round(time.time() * 1000))
    main()
    t_dupa = int(round(time.time() * 1000))
    print("Jocul a durat timp de " + str(t_dupa - t_inainte) + " milisecunde.")
