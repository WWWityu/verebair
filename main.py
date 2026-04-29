from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

class RendszerHiba(Exception):
    pass

class ValidaciosHiba(RendszerHiba):
    pass

class JaratNemTalalhatoHiba(RendszerHiba):
    pass

class JaratNemElerhetoHiba(RendszerHiba):
    pass

class FoglalasNemTalalhatoHiba(RendszerHiba):
    pass

class Jarat(ABC):
    def __init__(self, jaratszam, celallomas, jegyar, indulas, ferohely):
        self.jaratszam = jaratszam
        self.celallomas = celallomas
        self.jegyar = jegyar
        self.indulas = indulas
        self.ferohely = ferohely

    @property
    def jaratszam(self):
        return self._jaratszam

    @jaratszam.setter
    def jaratszam(self, ertek):
        if not isinstance(ertek, str) or not ertek.strip():
            raise ValidaciosHiba("A járatszám nem lehet üres.")
        self._jaratszam = ertek.strip().upper()

    @property
    def celallomas(self):
        return self._celallomas

    @celallomas.setter
    def celallomas(self, ertek):
        if not isinstance(ertek, str) or not ertek.strip():
            raise ValidaciosHiba("A célállomás nem lehet üres.")
        self._celallomas = ertek.strip()

    @property
    def jegyar(self):
        return self._jegyar

    @jegyar.setter
    def jegyar(self, ertek):
        if not isinstance(ertek, int) or ertek <= 0:
            raise ValidaciosHiba("A jegyár csak pozitív egész szám lehet.")
        self._jegyar = ertek

    @property
    def indulas(self):
        return self._indulas

    @indulas.setter
    def indulas(self, ertek):
        if not isinstance(ertek, datetime):
            raise ValidaciosHiba("Az indulás időpontja hibás.")
        self._indulas = ertek

    @property
    def ferohely(self):
        return self._ferohely

    @ferohely.setter
    def ferohely(self, ertek):
        if not isinstance(ertek, int) or ertek <= 0:
            raise ValidaciosHiba("A férőhelyek száma csak pozitív egész lehet.")
        self._ferohely = ertek

    @property
    @abstractmethod
    def tipus(self):
        pass


class BelfoldiJarat(Jarat):
    def __init__(self, jaratszam, celallomas, jegyar, indulas, ferohely, menetido):
        super().__init__(jaratszam, celallomas, jegyar, indulas, ferohely)
        self.menetido = menetido

    @property
    def menetido(self):
        return self._menetido

    @menetido.setter
    def menetido(self, ertek):
        if not isinstance(ertek, int) or ertek <= 0:
            raise ValidaciosHiba("A menetidő csak pozitív egész szám lehet.")
        self._menetido = ertek

    @property
    def tipus(self):
        return "Belföldi"


class NemzetkoziJarat(Jarat):
    def __init__(self, jaratszam, celallomas, jegyar, indulas, ferohely, orszag):
        super().__init__(jaratszam, celallomas, jegyar, indulas, ferohely)
        self.orszag = orszag

    @property
    def orszag(self):
        return self._orszag

    @orszag.setter
    def orszag(self, ertek):
        if not isinstance(ertek, str) or not ertek.strip():
            raise ValidaciosHiba("Az ország nem lehet üres.")
        self._orszag = ertek.strip()

    @property
    def tipus(self):
        return "Nemzetközi"


class JegyFoglalas:
    def __init__(self, foglalas_id, utas_neve, jarat, foglalas_ideje):
        self.foglalas_id = foglalas_id
        self.utas_neve = utas_neve
        self.jarat = jarat
        self.foglalas_ideje = foglalas_ideje

    @property
    def foglalas_id(self):
        return self._foglalas_id

    @foglalas_id.setter
    def foglalas_id(self, ertek):
        if not isinstance(ertek, int) or ertek <= 0:
            raise ValidaciosHiba("A foglalás azonosítója hibás.")
        self._foglalas_id = ertek

    @property
    def utas_neve(self):
        return self._utas_neve

    @utas_neve.setter
    def utas_neve(self, ertek):
        if not isinstance(ertek, str) or not ertek.strip():
            raise ValidaciosHiba("Az utas neve nem lehet üres.")
        self._utas_neve = ertek.strip()

    @property
    def jarat(self):
        return self._jarat

    @jarat.setter
    def jarat(self, ertek):
        if not isinstance(ertek, Jarat):
            raise ValidaciosHiba("A foglaláshoz érvényes járat kell.")
        self._jarat = ertek

    @property
    def foglalas_ideje(self):
        return self._foglalas_ideje

    @foglalas_ideje.setter
    def foglalas_ideje(self, ertek):
        if not isinstance(ertek, datetime):
            raise ValidaciosHiba("A foglalás ideje hibás.")
        self._foglalas_ideje = ertek

    @property
    def ar(self):
        return self.jarat.jegyar


class LegiTarsasag:
    def __init__(self, nev):
        self.nev = nev
        self._jaratok = []
        self._foglalasok = []
        self._kovetkezo_id = 1

    @property
    def nev(self):
        return self._nev

    @nev.setter
    def nev(self, ertek):
        if not isinstance(ertek, str) or not ertek.strip():
            raise ValidaciosHiba("A légitársaság neve nem lehet üres.")
        self._nev = ertek.strip()

    @property
    def jaratok(self):
        return list(self._jaratok)

    @property
    def foglalasok(self):
        return list(self._foglalasok)

    def jarat_hozzaad(self, jarat):
        for letezo in self._jaratok:
            if letezo.jaratszam == jarat.jaratszam:
                raise ValidaciosHiba("Ez a járatszám már szerepel a rendszerben.")
        self._jaratok.append(jarat)

    def jarat_keres(self, jaratszam):
        keresett = jaratszam.strip().upper()
        for jarat in self._jaratok:
            if jarat.jaratszam == keresett:
                return jarat
        raise JaratNemTalalhatoHiba("Nem találom a megadott járatot.")

    def szabad_helyek(self, jaratszam):
        jarat = self.jarat_keres(jaratszam)
        foglalt = 0
        for foglalas in self._foglalasok:
            if foglalas.jarat.jaratszam == jarat.jaratszam:
                foglalt += 1
        return jarat.ferohely - foglalt

    def foglalhato_e(self, jaratszam, foglalas_ideje):
        jarat = self.jarat_keres(jaratszam)

        if jarat.indulas <= datetime.now():
            return False

        if foglalas_ideje < datetime.now():
            return False

        if foglalas_ideje > jarat.indulas:
            return False

        if self.szabad_helyek(jaratszam) <= 0:
            return False

        return True

    def jegy_foglal(self, utas_neve, jaratszam, foglalas_ideje_szoveg):
        if not utas_neve.strip():
            raise ValidaciosHiba("Add meg az utas nevét.")

        if not jaratszam.strip():
            raise ValidaciosHiba("Válassz járatot.")

        if not foglalas_ideje_szoveg.strip():
            raise ValidaciosHiba("Válassz foglalási időpontot.")

        try:
            foglalas_ideje = datetime.strptime(foglalas_ideje_szoveg.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValidaciosHiba("A kiválasztott időpont formátuma hibás.")

        jarat = self.jarat_keres(jaratszam)

        if not self.foglalhato_e(jarat.jaratszam, foglalas_ideje):
            raise JaratNemElerhetoHiba("Erre a járatra most nem tudok foglalást felvenni.")

        uj_foglalas = JegyFoglalas(self._kovetkezo_id, utas_neve, jarat, foglalas_ideje)
        self._foglalasok.append(uj_foglalas)
        self._kovetkezo_id += 1
        return uj_foglalas.ar

    def foglalas_hozzaad(self, utas_neve, jaratszam, foglalas_ideje):
        jarat = self.jarat_keres(jaratszam)

        if not self.foglalhato_e(jarat.jaratszam, foglalas_ideje):
            raise JaratNemElerhetoHiba("A mintafoglalást nem tudom rögzíteni ehhez a járathoz.")

        self._foglalasok.append(JegyFoglalas(self._kovetkezo_id, utas_neve, jarat, foglalas_ideje))
        self._kovetkezo_id += 1

    def foglalas_lemond(self, foglalas_id):
        for index, foglalas in enumerate(self._foglalasok):
            if foglalas.foglalas_id == foglalas_id:
                del self._foglalasok[index]
                return
        raise FoglalasNemTalalhatoHiba("Nem találom a megadott foglalást.")

    def foglalasok_listaz(self):
        return sorted(
            self._foglalasok,
            key=lambda f: (f.jarat.indulas, f.jarat.jaratszam, f.utas_neve.lower())
        )


def minta_adatok():
    # előre betöltöm a légitársaságot, a járatokat és a foglalásokat, hogy a program indulás után rögtön használható legyen.
    tarsasag = LegiTarsasag("VerebAir R8Q3N0")
    most = datetime.now().replace(second=0, microsecond=0)

    tarsasag.jarat_hozzaad(BelfoldiJarat("VA101", "Debrecen", 15990, most + timedelta(days=2, hours=3), 4, 55))
    tarsasag.jarat_hozzaad(BelfoldiJarat("VA202", "Pécs", 13990, most + timedelta(days=3, hours=2), 3, 60))
    tarsasag.jarat_hozzaad(NemzetkoziJarat("VA890", "Róma", 49990, most + timedelta(days=5, hours=4), 5, "Olaszország"))
    tarsasag.jarat_hozzaad(NemzetkoziJarat("VA901", "Bécs", 32990, most + timedelta(days=4, hours=1), 6, "Ausztria"))
    tarsasag.jarat_hozzaad(NemzetkoziJarat("VA902", "Prága", 35990, most + timedelta(days=4, hours=5), 6, "Csehország"))
    tarsasag.jarat_hozzaad(NemzetkoziJarat("VA903", "Berlin", 42990, most + timedelta(days=6, hours=2), 7, "Németország"))
    tarsasag.jarat_hozzaad(NemzetkoziJarat("VA904", "Párizs", 58990, most + timedelta(days=7, hours=3), 8, "Franciaország"))
    tarsasag.jarat_hozzaad(NemzetkoziJarat("VA905", "Madrid", 61990, most + timedelta(days=8, hours=2), 8, "Spanyolország"))

    mintak = [
        ("Verebes Vivien", "VA101", most + timedelta(hours=1)),
        ("Verebes Veronika", "VA101", most + timedelta(hours=2)),
        ("Verebes Vanda", "VA202", most + timedelta(hours=3)),
        ("Verebes Viktória", "VA202", most + timedelta(hours=4)),
        ("Verebes Viktor", "VA890", most + timedelta(hours=5)),
        ("Verebes Vivien", "VA890", most + timedelta(hours=6)),
    ]

    for utas_neve, jaratszam, foglalas_ideje in mintak:
        tarsasag.foglalas_hozzaad(utas_neve, jaratszam, foglalas_ideje)

    return tarsasag


class Alkalmazas:
    def __init__(self, root):
        self.root = root
        self.tarsasag = minta_adatok()

        self.root.title("Légitársasági jegyfoglaló rendszer")
        self.root.geometry("1750x980")
        self.root.minsize(1500, 900)

        self.felulet_felepit()
        self.frissit()

    def felulet_felepit(self):
        # két egyszerű táblát használok, hogy bal oldalon a járatokat, jobb oldalon pedig a foglalásokat lehessen kényelmesen átlátni.
        cim = tk.Label(
            self.root,
            text=f"{self.tarsasag.nev} - egyszerű jegyfoglaló rendszer",
            font=("Arial", 20, "bold"),
            pady=12,
        )
        cim.pack()

        alcim = tk.Label(
            self.root,
            text="Induláskor 1 légitársaság, 8 járat és 6 foglalás van előre betöltve.",
            font=("Arial", 10),
            pady=4,
        )
        alcim.pack()

        fo = tk.Frame(self.root, padx=12, pady=10)
        fo.pack(fill="both", expand=True)

        bal = tk.LabelFrame(fo, text="Járatok", padx=10, pady=10)
        bal.pack(side="left", fill="both", expand=True, padx=(0, 6))

        jobb = tk.LabelFrame(fo, text="Foglalások", padx=10, pady=10)
        jobb.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self.jaratok_tabla = ttk.Treeview(
            bal,
            columns=("tipus", "jaratszam", "cel", "indulas", "ar", "szabad"),
            show="headings",
            height=15,
        )
        for oszlop, szoveg in [
            ("tipus", "Típus"),
            ("jaratszam", "Járatszám"),
            ("cel", "Célállomás"),
            ("indulas", "Indulás"),
            ("ar", "Jegyár"),
            ("szabad", "Szabad hely"),
        ]:
            self.jaratok_tabla.heading(oszlop, text=szoveg)

        self.jaratok_tabla.column("tipus", width=150, anchor="center")
        self.jaratok_tabla.column("jaratszam", width=120, anchor="center")
        self.jaratok_tabla.column("cel", width=180, anchor="w")
        self.jaratok_tabla.column("indulas", width=190, anchor="center")
        self.jaratok_tabla.column("ar", width=120, anchor="e")
        self.jaratok_tabla.column("szabad", width=110, anchor="center")
        self.jaratok_tabla.pack(fill="both", expand=True)

        urlap = tk.Frame(bal, pady=10)
        urlap.pack(fill="x")

        tk.Label(urlap, text="Utas neve:").grid(row=0, column=0, sticky="w", pady=4)
        self.utas_entry = tk.Entry(urlap, width=26)
        self.utas_entry.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        tk.Label(urlap, text="Járatszám:").grid(row=1, column=0, sticky="w", pady=4)
        self.jaratszam_valaszto = ttk.Combobox(urlap, width=23, state="readonly")
        self.jaratszam_valaszto.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        tk.Label(urlap, text="Foglalás ideje:").grid(row=2, column=0, sticky="w", pady=4)
        self.idopont_valaszto = ttk.Combobox(urlap, width=23, state="readonly")
        self.idopont_valaszto.grid(row=2, column=1, sticky="w", padx=5, pady=4)

        tk.Label(
            urlap,
            text="Én itt már listából választok járatot és időpontot is.",
            fg="gray",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 5))

        gombok = tk.Frame(bal, pady=6)
        gombok.pack(fill="x")

        tk.Button(gombok, text="Jegy foglalása", width=18, command=self.jegy_foglal).pack(side="left", padx=(0, 8))
        tk.Button(gombok, text="Mezők törlése", width=18, command=self.mezok_torlese).pack(side="left")

        self.foglalasok_tabla = ttk.Treeview(
            jobb,
            columns=("id", "utas", "jaratszam", "cel", "indulas", "ar"),
            show="headings",
            height=15,
        )
        for oszlop, szoveg in [
            ("id", "Foglalás ID"),
            ("utas", "Utas"),
            ("jaratszam", "Járatszám"),
            ("cel", "Célállomás"),
            ("indulas", "Indulás"),
            ("ar", "Ár"),
        ]:
            self.foglalasok_tabla.heading(oszlop, text=szoveg)

        self.foglalasok_tabla.column("id", width=110, anchor="center")
        self.foglalasok_tabla.column("utas", width=190, anchor="w")
        self.foglalasok_tabla.column("jaratszam", width=120, anchor="center")
        self.foglalasok_tabla.column("cel", width=170, anchor="w")
        self.foglalasok_tabla.column("indulas", width=190, anchor="center")
        self.foglalasok_tabla.column("ar", width=120, anchor="e")
        self.foglalasok_tabla.pack(fill="both", expand=True)

        also = tk.Frame(jobb, pady=10)
        also.pack(fill="x")

        tk.Label(also, text="Lemondandó foglalás ID:").grid(row=0, column=0, sticky="w", pady=4)
        self.foglalas_id_entry = tk.Entry(also, width=20)
        self.foglalas_id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        tk.Button(also, text="Foglalás lemondása", width=18, command=self.foglalas_lemond).grid(row=1, column=0, sticky="w", pady=8)
        tk.Button(also, text="Frissítés", width=18, command=self.frissit).grid(row=1, column=1, sticky="e", pady=8)

        self.statusz = tk.StringVar(value="Kész. Várom a következő műveletet.")
        status_keret = tk.Frame(self.root, bd=1, relief="sunken")
        status_keret.pack(fill="x", side="bottom")
        tk.Label(status_keret, textvariable=self.statusz, anchor="w", padx=8, pady=6).pack(fill="x")

        self.jaratok_tabla.bind("<<TreeviewSelect>>", self.jarat_kattintas)
        self.foglalasok_tabla.bind("<<TreeviewSelect>>", self.foglalas_kattintas)
        self.jaratszam_valaszto.bind("<<ComboboxSelected>>", self.jarat_valasztva)

    def jarat_lista_frissit(self):
        # feltöltöm a választható járatlistát, hogy semmit ne kelljen kézzel beírni.
        jaratszamok = [jarat.jaratszam for jarat in self.tarsasag.jaratok]
        self.jaratszam_valaszto["values"] = jaratszamok

    def foglalasi_idopontok(self, jaratszam):
        # előre legenerálok néhány választható időpontot a kiválasztott járathoz, hogy ne kelljen a foglalás idejét kézzel beírni.
        jarat = self.tarsasag.jarat_keres(jaratszam)
        most = datetime.now().replace(second=0, microsecond=0)
        kezdes = most + timedelta(minutes=30)
        vege = jarat.indulas - timedelta(minutes=30)

        if kezdes >= vege:
            return []

        kulonbseg = vege - kezdes
        lepesszam = 6
        percek = max(30, int(kulonbseg.total_seconds() // 60 / lepesszam))

        idopontok = []
        aktualis = kezdes

        while aktualis <= vege and len(idopontok) < 8:
            idopontok.append(aktualis.strftime("%Y-%m-%d %H:%M"))
            aktualis += timedelta(minutes=percek)

        utolso = vege.strftime("%Y-%m-%d %H:%M")
        if utolso not in idopontok:
            idopontok.append(utolso)

        return idopontok[:8]

    def idopont_valaszto_frissit(self):
        jaratszam = self.jaratszam_valaszto.get().strip()

        if not jaratszam:
            self.idopont_valaszto["values"] = []
            self.idopont_valaszto.set("")
            return

        try:
            idopontok = self.foglalasi_idopontok(jaratszam)
            self.idopont_valaszto["values"] = idopontok
            if idopontok:
                self.idopont_valaszto.current(0)
                self.statusz.set("A foglalási időpontok frissítve lettek a kiválasztott járathoz.")
            else:
                self.idopont_valaszto.set("")
                self.statusz.set("Ehhez a járathoz most nem tudok választható időpontot adni.")
        except RendszerHiba:
            self.idopont_valaszto["values"] = []
            self.idopont_valaszto.set("")

    def jarat_valasztva(self, event=None):
        self.idopont_valaszto_frissit()

    def frissit(self):
        # újratöltöm a táblákat, hogy a képernyő biztosan a legfrissebb adatokat mutassa foglalás vagy lemondás után.
        self.jarat_lista_frissit()

        for sor in self.jaratok_tabla.get_children():
            self.jaratok_tabla.delete(sor)

        for jarat in self.tarsasag.jaratok:
            self.jaratok_tabla.insert(
                "",
                "end",
                values=(
                    jarat.tipus,
                    jarat.jaratszam,
                    jarat.celallomas,
                    jarat.indulas.strftime("%Y-%m-%d %H:%M"),
                    f"{jarat.jegyar} Ft",
                    self.tarsasag.szabad_helyek(jarat.jaratszam),
                ),
            )

        for sor in self.foglalasok_tabla.get_children():
            self.foglalasok_tabla.delete(sor)

        for foglalas in self.tarsasag.foglalasok_listaz():
            self.foglalasok_tabla.insert(
                "",
                "end",
                values=(
                    foglalas.foglalas_id,
                    foglalas.utas_neve,
                    foglalas.jarat.jaratszam,
                    foglalas.jarat.celallomas,
                    foglalas.jarat.indulas.strftime("%Y-%m-%d %H:%M"),
                    f"{foglalas.ar} Ft",
                ),
            )

        self.statusz.set("Az adatok frissítése megtörtént.")
        if self.jaratszam_valaszto.get().strip():
            self.idopont_valaszto_frissit()

    def jegy_foglal(self):
        try:
            ar = self.tarsasag.jegy_foglal(
                self.utas_entry.get().strip(),
                self.jaratszam_valaszto.get().strip(),
                self.idopont_valaszto.get().strip(),
            )
            self.frissit()
            self.mezok_torlese()
            self.statusz.set(f"Sikeres foglalás. Fizetendő: {ar} Ft")
            messagebox.showinfo("Siker", f"A foglalás sikeres. Fizetendő összeg: {ar} Ft")
        except RendszerHiba as hiba:
            self.statusz.set(f"Hiba: {hiba}")
            messagebox.showerror("Hiba", str(hiba))

    def foglalas_lemond(self):
        try:
            foglalas_id = int(self.foglalas_id_entry.get().strip())
            self.tarsasag.foglalas_lemond(foglalas_id)
            self.frissit()
            self.foglalas_id_entry.delete(0, tk.END)
            self.statusz.set("A foglalás lemondása sikeres.")
            messagebox.showinfo("Siker", "A foglalás lemondása sikeres.")
        except ValueError:
            self.statusz.set("A foglalás azonosítója csak szám lehet.")
            messagebox.showerror("Hiba", "A foglalás azonosítója csak szám lehet.")
        except RendszerHiba as hiba:
            self.statusz.set(f"Hiba: {hiba}")
            messagebox.showerror("Hiba", str(hiba))

    def mezok_torlese(self):
        self.utas_entry.delete(0, tk.END)
        self.jaratszam_valaszto.set("")
        self.idopont_valaszto.set("")
        self.idopont_valaszto["values"] = []

    def jarat_kattintas(self, event=None):
        kijelolt = self.jaratok_tabla.selection()
        if not kijelolt:
            return
        ertekek = self.jaratok_tabla.item(kijelolt[0], "values")
        self.jaratszam_valaszto.set(ertekek[1])
        self.idopont_valaszto_frissit()
        self.statusz.set(f"Kiválasztott járat: {ertekek[1]} - {ertekek[2]}")

    def foglalas_kattintas(self, event=None):
        kijelolt = self.foglalasok_tabla.selection()
        if not kijelolt:
            return
        ertekek = self.foglalasok_tabla.item(kijelolt[0], "values")
        self.foglalas_id_entry.delete(0, tk.END)
        self.foglalas_id_entry.insert(0, ertekek[0])
        self.statusz.set(f"Kiválasztott foglalás: {ertekek[0]}")


def main():
    # indul az ablakos felületet.
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    Alkalmazas(root)
    root.mainloop()


if __name__ == "__main__":
    main()
