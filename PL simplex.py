import tkinter as tk
from tkinter import messagebox, scrolledtext
from fractions import Fraction

class SimplexeApp:
    def __init__(self, master):
        self.master = master
        master.title("Simplexe - Maximisation ")
        master.configure(bg="#f0f4f8")
        self.n_contraintes = 3  # défaut
        self.vars = 3           # variables fixes à 3
        self.entries_constraints = []
        self.signes = []  # Pour stocker les choix de signes
        self.build_interface()

    def build_interface(self):
        tk.Label(self.master, text="Méthode du Simplexe", font=("Arial", 16, "bold"), bg="#f0f4f8", fg="#003366")\
            .grid(row=0, column=0, columnspan=9, pady=10)

        tk.Label(self.master, text="Fonction Objectif : Max Z = c1·x1 + c2·x2 + c3·x3", font=("Arial", 12), bg="#f0f4f8")\
            .grid(row=1, column=0, columnspan=9)

        # Coefficients fonction objectif
        tk.Label(self.master, text="c1", bg="#f0f4f8").grid(row=2, column=1)
        tk.Label(self.master, text="c2", bg="#f0f4f8").grid(row=2, column=2)
        tk.Label(self.master, text="c3", bg="#f0f4f8").grid(row=2, column=3)

        self.c1 = tk.Entry(self.master, width=6)
        self.c2 = tk.Entry(self.master, width=6)
        self.c3 = tk.Entry(self.master, width=6)
        self.c1.grid(row=3, column=1, padx=5, pady=5)
        self.c2.grid(row=3, column=2, padx=5, pady=5)
        self.c3.grid(row=3, column=3, padx=5, pady=5)

        # Choix nombre contraintes
        tk.Label(self.master, text="Nombre de contraintes:", bg="#f0f4f8").grid(row=4, column=0, sticky='w', padx=5)
        self.spin_contraintes = tk.Spinbox(self.master, from_=1, to=10, width=5, command=self.maj_contraintes)
        self.spin_contraintes.grid(row=4, column=1, sticky='w')
        self.spin_contraintes.delete(0, tk.END)
        self.spin_contraintes.insert(0, str(self.n_contraintes))

        # Frame pour contraintes
        self.frame_contraintes = tk.Frame(self.master, bg="#f0f4f8")
        self.frame_contraintes.grid(row=5, column=0, columnspan=9, pady=10)

        self.afficher_contraintes(self.n_contraintes)

        # Bouton résoudre
        tk.Button(self.master, text="Résoudre", bg="#007acc", fg="white", font=("Arial", 11, "bold"),
                  command=self.resoudre).grid(row=6, column=0, columnspan=9, pady=10)

        # Résultat scrollable
        self.result_text = scrolledtext.ScrolledText(self.master, width=90, height=20, font=("Courier", 10))
        self.result_text.grid(row=7, column=0, columnspan=9, padx=10, pady=5)

    def afficher_contraintes(self, n):
        # Nettoyer
        for widget in self.frame_contraintes.winfo_children():
            widget.destroy()
        self.entries_constraints = []
        self.signes = []

        # Entêtes colonnes
        tk.Label(self.frame_contraintes, text="x1", bg="#f0f4f8").grid(row=0, column=1, padx=5)
        tk.Label(self.frame_contraintes, text="x2", bg="#f0f4f8").grid(row=0, column=2, padx=5)
        tk.Label(self.frame_contraintes, text="x3", bg="#f0f4f8").grid(row=0, column=3, padx=5)
        tk.Label(self.frame_contraintes, text="Signe", bg="#f0f4f8").grid(row=0, column=4, padx=5)
        tk.Label(self.frame_contraintes, text="b", bg="#f0f4f8").grid(row=0, column=5, padx=5)

        signes_possibles = ["≤", "=", "≥"]

        for i in range(n):
            tk.Label(self.frame_contraintes, text=f"Contrainte {i+1}", bg="#f0f4f8").grid(row=i+1, column=0, padx=5, sticky='w')

            row_entries = []
            for j in range(3):  # 3 coeffs variables
                entry = tk.Entry(self.frame_contraintes, width=7)
                entry.grid(row=i+1, column=j+1, padx=5, pady=3)
                row_entries.append(entry)

            var_signe = tk.StringVar(value="≤")
            option_signe = tk.OptionMenu(self.frame_contraintes, var_signe, *signes_possibles)
            option_signe.config(width=2)
            option_signe.grid(row=i+1, column=4, padx=5)
            self.signes.append(var_signe)

            entry_b = tk.Entry(self.frame_contraintes, width=7)
            entry_b.grid(row=i+1, column=5, padx=5, pady=3)
            row_entries.append(entry_b)

            self.entries_constraints.append(row_entries)

    def maj_contraintes(self):
        try:
            n = int(self.spin_contraintes.get())
            if 1 <= n <= 10:
                self.n_contraintes = n
                self.afficher_contraintes(n)
        except:
            pass

    def afficher_tableau(self, tableau, iteration):
        self.result_text.insert(tk.END, f"\n--- Itération {iteration} ---\n")
        header = ["x1", "x2", "x3"] + [f"s{i+1}" for i in range(self.n_contraintes)] + ["b"]
        larg = 10

        # Affichage header
        self.result_text.insert(tk.END, "".join(h.center(larg) for h in header) + "\n")

        # Affichage lignes
        for ligne in tableau:
            ligne_str = "".join(str(el).center(larg) for el in ligne)
            self.result_text.insert(tk.END, ligne_str + "\n")

    def resoudre(self):
        self.result_text.delete(1.0, tk.END)
        try:
            c = [Fraction(self.c1.get()), Fraction(self.c2.get()), Fraction(self.c3.get())]

            A = []
            b = []
            signes = []
            for i, row in enumerate(self.entries_constraints):
                coeffs = [Fraction(cell.get()) for cell in row[:3]]
                val_b = Fraction(row[3].get())
                signe = self.signes[i].get()
                A.append(coeffs)
                b.append(val_b)
                signes.append(signe)

            n = self.n_contraintes
            m = self.vars

            # Construire tableau simplexe : A + slack + b
            tableau = []
            for i in range(n):
                slack = [Fraction(0)] * n
                if signes[i] == "≤":
                    slack[i] = Fraction(1)
                elif signes[i] == "≥":
                    slack[i] = Fraction(-1)
                elif signes[i] == "=":
                    slack[i] = Fraction(0)  # Pas de variable d'écart ici
                tableau.append(A[i] + slack + [b[i]])

            # Ligne objectif (Z)
            tableau.append([-ci for ci in c] + [Fraction(0)] * (n + 1))

            lignes = n + 1
            colonnes = m + n + 1

            iteration = 0
            self.afficher_tableau(tableau, iteration)

            def colonne_pivot():
                min_val = Fraction(0)
                idx = -1
                for j in range(colonnes - 1):
                    if tableau[-1][j] < min_val:
                        min_val = tableau[-1][j]
                        idx = j
                return idx

            def ligne_pivot(col):
                min_ratio = float('inf')
                idx = -1
                for i in range(lignes - 1):
                    if tableau[i][col] > 0:
                        ratio = float(tableau[i][-1] / tableau[i][col])
                        if ratio < min_ratio:
                            min_ratio = ratio
                            idx = i
                return idx

            while True:
                col_p = colonne_pivot()
                if col_p == -1:
                    break
                row_p = ligne_pivot(col_p)
                if row_p == -1:
                    self.result_text.insert(tk.END, " Solution non bornée.\n")
                    return

                pivot = tableau[row_p][col_p]
                tableau[row_p] = [x / pivot for x in tableau[row_p]]

                for i in range(lignes):
                    if i != row_p:
                        facteur = tableau[i][col_p]
                        tableau[i] = [tableau[i][j] - facteur * tableau[row_p][j] for j in range(colonnes)]

                iteration += 1
                self.afficher_tableau(tableau, iteration)

            solution = [Fraction(0)] * m
            for j in range(m):
                col = [tableau[i][j] for i in range(lignes)]
                if col.count(Fraction(1)) == 1 and col.count(Fraction(0)) == lignes - 1:
                    one_index = col.index(Fraction(1))
                    solution[j] = tableau[one_index][-1]

            Z = tableau[-1][-1]

            self.result_text.insert(tk.END, "\n Solution optimale :\n")
            for i in range(m):
                self.result_text.insert(tk.END, f"x{i+1} = {solution[i]}\n")
            self.result_text.insert(tk.END, f"Z = {Z}\n")

        except Exception as e:
            messagebox.showerror("Erreur", f"Entrée invalide ou erreur:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexeApp(root)
    root.mainloop()
