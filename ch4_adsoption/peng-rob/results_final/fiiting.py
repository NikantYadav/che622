#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import glob

# -----------------------------
# CONSTANTS
# -----------------------------
AVOGADRO = 6.02214076e23         # molecules/mol
COAL_MASS_MG = 28603.9           # mg
COAL_MASS_G = COAL_MASS_MG / 1000.0   # g

# -----------------------------
# Read absolute adsorption (mmol/g)
# -----------------------------
def read_absolute_mmol(pattern="isotherm_P*.dat"):
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError("No isotherm files found.")

    pressures = []
    n_ch4 = []

    for filename in files:
        with open(filename) as f:
            for line in f:
                if line.startswith("#"): 
                    continue
                data = line.split()
                pressures.append(float(data[0]))
                n_ch4.append(float(data[1]))

    pressures = np.array(pressures)
    n_ch4 = np.array(n_ch4)

    # Sort by pressure
    idx = np.argsort(pressures)
    pressures = pressures[idx]
    n_ch4 = n_ch4[idx]

    # Convert to mmol/g
    mmol_g = []
    for n in n_ch4:
        n_mol = n / AVOGADRO            # mol
        loading = (n_mol * 1000.0) / COAL_MASS_G   # mmol/g
        mmol_g.append(loading)

    return pressures, np.array(mmol_g)

# -----------------------------
# Langmuir model
# -----------------------------
def langmuir(P, qmax, K):
    return qmax * K * P / (1 + K * P)

# -----------------------------
# Fit Langmuir
# -----------------------------
def fit_langmuir(P, q):
    popt, _ = curve_fit(langmuir, P, q, p0=[np.max(q), 1], maxfev=10000)
    q_fit = langmuir(P, *popt)

    # R²
    ss_res = np.sum((q - q_fit)**2)
    ss_tot = np.sum((q - np.mean(q))**2)
    r2 = 1 - ss_res/ss_tot

    return popt, q_fit, r2

# -----------------------------
# Plot
# -----------------------------
def plot_langmuir_fit(P, q, q_fit, outfile="absolute_mmol_langmuir.png"):
    plt.figure(figsize=(8,6))
    plt.scatter(P, q, s=120, edgecolors="black", label="Absolute (mmol/g)")
    plt.plot(P, q_fit, 'r-', label="Langmuir Fit", linewidth=2)
    plt.xlabel("Pressure (bar)")
    plt.ylabel("Absolute Adsorption (mmol/g)")
    plt.title("Absolute CH₄ Adsorption with Langmuir Fit")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    print(f"Plot saved: {outfile}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    P, q = read_absolute_mmol()
    popt, q_fit, r2 = fit_langmuir(P, q)

    print("\n===== Langmuir Fit Results (Absolute mmol/g) =====")
    print(f"qmax = {popt[0]:.4f} mmol/g")
    print(f"K    = {popt[1]:.4f} 1/bar")
    print(f"R²   = {r2:.4f}")

    plot_langmuir_fit(P, q, q_fit)
