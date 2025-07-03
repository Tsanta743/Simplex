import tkinter as tk
from tkinter import messagebox, scrolledtext
from fractions import Fraction
import pandas as pd

def afficher_tableau(tableau, base, variables, etape):
    cols = variables + ["Sol"]
    index = base + ["Z"]
    df = pd.DataFrame(tableau, columns=cols, index=index)
    return f"\n🔄 Étape {etape} :\n{df.to_string()}\n"

def afficher_resultat_final(tableau, base, variables, n_vars):
    res = "\n✅ Résultat final :\n"
    final_values = {var: Fraction(0) for var in variables[:n_vars]}

    for j, var in enumerate(variables[:n_vars]):
        col = [tableau[i][j] for i in range(len(tableau)-1)]
        is_base = sum(1 for val in col if val == 1) == 1 and all(val in [0, 1] for val in col)
        if is_base:
            row_index = col.index(1)
            final_values[var] = tableau[row_index][-1]

    for var in sorted(final_values):
        res += f"{var} = {final_values[var]}\n"
    res += f"Z = {tableau[-1][-1]}\n"
    return res


def simplexe_max_fraction(A, b, c):
    A = [[Fraction(aij) for aij in row] for row in A]
    b = [Fraction(bi) for bi in b]
    c = [Fraction(ci) for ci in c]

    m, n = len(A), len(A[0])
    total_vars = n + m
    tableau = [[Fraction(0)] * (total_vars + 1) for _ in range(m + 1)]

    for i in range(m):
        for j in range(n):
            tableau[i][j] = A[i][j]
        tableau[i][n + i] = Fraction(1)
        tableau[i][-1] = b[i]

    for j in range(n):
        tableau[-1][j] = -c[j]

    variables = [f"x{j+1}" for j in range(n)] + [f"s{i+1}" for i in range(m)]
    base = [f"s{i+1}" for i in range(m)]

    etape = 0
    log = afficher_tableau(tableau, base, variables, etape)

    while True:
        last_row = tableau[-1][:-1]
        if all(x <= 0 for x in last_row):
            break

        pivot_col = last_row.index(max(last_row))
        ratios = []
        for i in range(m):
            if tableau[i][pivot_col] > 0:
                ratios.append(tableau[i][-1] / tableau[i][pivot_col])
            else:
                ratios.append(Fraction('inf'))

        if all(r == Fraction('inf') for r in ratios):
            return "❌ Problème non borné."

        pivot_row = ratios.index(min(ratios))
        pivot = tableau[pivot_row][pivot_col]
        tableau[pivot_row] = [x / pivot for x in tableau[pivot_row]]

        for i in range(m + 1):
            if i != pivot_row:
                coef = tableau[i][pivot_col]
                tableau[i] = [
                    tableau[i][j] - coef * tableau[pivot_row][j]
                    for j in range(total_vars + 1)
                ]

        base[pivot_row] = variables[pivot_col]
        etape += 1
        log += afficher_tableau(tableau, base, variables, etape)

    log += afficher_resultat_final(tableau, base, variables, n)
    return log

# Interface Tkinter
class SimplexeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplexe - Résolution exacte (Fraction)")
        self.root.geometry("850x650")

        tk.Label(root, text="Fonction Objectif (ex: 3 5 4)").pack()
        self.obj_entry = tk.Entry(root, width=80)
        self.obj_entry.pack()

        tk.Label(root, text="Contraintes (ex: 2 3 0 <= 8)").pack()
        self.constraints_text = scrolledtext.ScrolledText(root, width=80, height=5)
        self.constraints_text.pack()

        tk.Button(root, text="Résoudre", command=self.resoudre).pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(root, width=100, height=30)
        self.result_text.pack()

    def resoudre(self):
        try:
            c = list(map(Fraction, self.obj_entry.get().strip().split()))
            raw_constraints = self.constraints_text.get("1.0", tk.END).strip().split("\n")

            A, b = [], []
            for line in raw_constraints:
                parts = line.strip().split()
                *coeffs, sign, rhs = parts
                if sign != "<=":
                    raise ValueError("Seules les contraintes <= sont supportées dans cette version.")
                A.append(list(map(Fraction, coeffs)))
                b.append(Fraction(rhs))

            result = simplexe_max_fraction(A, b, c)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexeApp(root)
    root.mainloop()
