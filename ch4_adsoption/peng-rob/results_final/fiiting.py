#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import glob

# Constants
AVOGADRO = 6.02214076e23
COAL_MASS_MG = 28603.9           # mg
COAL_MASS_G = COAL_MASS_MG / 1000.0   # g


# ---------------------------------------------------------
# Load adsorption data (mmol/g)
# ---------------------------------------------------------
def read_absolute_mmol(pattern="isotherm_P*.dat"):
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError("No isotherm files found.")

    P, n = [], []
    for fname in files:
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                cols = line.split()
                if len(cols) < 2:
                    continue  # skip malformed lines

                pressure = float(cols[0])
                n_ch4 = float(cols[1])  # <-- molecules

                P.append(pressure)
                n.append(n_ch4)

    P = np.array(P)
    n = np.array(n)

    # Sort by pressure
    idx = np.argsort(P)
    P = P[idx]
    n = n[idx]

    # Convert molecules → mmol/g
    mmol_g = (n / AVOGADRO) * 1000 / COAL_MASS_G
    return P, mmol_g


# ---------------------------------------------------------
# Isotherm models
# ---------------------------------------------------------
def langmuir(P, qmax, K):
    return qmax * K * P / (1 + K * P)

def dual_site_langmuir(P, q1, K1, q2, K2):
    return (q1 * K1 * P) / (1 + K1 * P) + (q2 * K2 * P) / (1 + K2 * P)

def sips(P, qmax, K, n):
    return qmax * (K * P)**n / (1 + (K * P)**n)


# ---------------------------------------------------------
# R²
# ---------------------------------------------------------
def r2(y, yfit):
    ssr = np.sum((y - yfit)**2)
    sst = np.sum((y - np.mean(y))**2)
    return 1 - ssr/sst


# ---------------------------------------------------------
# Fit models
# ---------------------------------------------------------
def fit_models(P, q):
    results = {}

    # Langmuir
    try:
        popt, _ = curve_fit(langmuir, P, q, p0=[np.max(q), 0.1])
        fit = langmuir(P, *popt)
        results["Langmuir"] = (popt, fit, r2(q, fit))
    except:
        results["Langmuir"] = None

    # Dual-site Langmuir
    try:
        p0 = [np.max(q)*0.6, 0.1, np.max(q)*0.4, 0.01]
        popt, _ = curve_fit(dual_site_langmuir, P, q, p0=p0, maxfev=20000)
        fit = dual_site_langmuir(P, *popt)
        results["Dual-site Langmuir"] = (popt, fit, r2(q, fit))
    except:
        results["Dual-site Langmuir"] = None

    # Sips
    try:
        popt, _ = curve_fit(sips, P, q, p0=[np.max(q), 0.1, 1.0], maxfev=20000)
        fit = sips(P, *popt)
        results["Sips"] = (popt, fit, r2(q, fit))
    except:
        results["Sips"] = None

    return results


# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
def plot_models(P, q, results, outfile="isotherm_models.png"):
    plt.figure(figsize=(8, 6), dpi=300)

    # --- Global styling ---
    plt.rcParams.update({
        "font.size": 14,
        "axes.labelsize": 16,
        "axes.titlesize": 18,
        "legend.fontsize": 13,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "axes.linewidth": 1.2,
    })

    # --- Plot experimental data ---
    plt.scatter(
        P, q, 
        s=60, 
        edgecolor="black", 
        facecolor="white", 
        linewidth=1.2, 
        label="Data"
    )

    # --- Plot fitted curves ---
    for name, res in results.items():
        if res is None:
            continue
        params, fit, R2 = res
        plt.plot(
            P, fit, 
            linewidth=2.0, 
            label=f"{name} (R²={R2:.3f})"
        )

    # --- Labels / formatting ---
    plt.xlabel("Pressure (bar)")
    plt.ylabel("Adsorption (mmol g$^{-1}$)")

    # Remove top & right spines for a clean scientific style
    ax = plt.gca()
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.legend(frameon=False)
    plt.tight_layout()

    # Save high-resolution figure
    plt.savefig(outfile, dpi=600, bbox_inches="tight")
    plt.close()
    print("Saved publication-quality figure to:", outfile)






# ---------------------------------------------------------
# Print to console
# ---------------------------------------------------------
def print_results(results):
    for name, res in results.items():
        print("\n" + name)
        if res is None:
            print("  Fit failed.")
            continue
        params, _, R2 = res
        print(f"  R² = {R2:.4f}")
        for i, p in enumerate(params):
            print(f"  param{i+1} = {p:.6f}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    P, q = read_absolute_mmol()
    results = fit_models(P, q)
    print_results(results)
    plot_models(P, q, results)
