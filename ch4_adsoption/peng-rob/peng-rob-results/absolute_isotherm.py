#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob

# CONSTANTS
MW_CH4 = 16.04                   # g/mol
AVOGADRO = 6.02214076e23         # molecules/mol
COAL_MASS_MG = 28603.9           # mg
COAL_MASS_G = COAL_MASS_MG / 1000.0   # g

# Extract data and recalc absolute adsorption
def extract_absolute_loading(file_pattern='isotherm_P*.dat'):
    files = sorted(glob.glob(file_pattern))

    if not files:
        print("No isotherm files found!")
        return None, None

    pressures = []
    n_ch4_list = []

    for filename in files:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    continue
                data = line.strip().split()
                if len(data) >= 2:
                    pressures.append(float(data[0]))
                    n_ch4_list.append(float(data[1]))

    pressures = np.array(pressures)
    n_ch4_list = np.array(n_ch4_list)

    # Sort
    idx = np.argsort(pressures)
    pressures = pressures[idx]
    n_ch4_list = n_ch4_list[idx]

    # Recalculate absolute loading mg/g
    loading_mg_g = []
    for n in n_ch4_list:
        n_mol = n / AVOGADRO                     # moles of CH4
        mass_ch4_mg = n_mol * MW_CH4 * 1000.0    # mg of CH4
        loading = mass_ch4_mg / COAL_MASS_G      # mg/g
        loading_mg_g.append(loading)

    return pressures, np.array(loading_mg_g)

# Plot absolute adsorption
def plot_absolute_adsorption(pressures, loading_mg_g, outfile="absolute_adsorption.png"):
    plt.figure(figsize=(8,6))

    plt.scatter(pressures, loading_mg_g, s=120, edgecolors='black')
    plt.plot(pressures, loading_mg_g, linewidth=1.5)

    plt.xlabel("Pressure (bar)", fontsize=13)
    plt.ylabel("Absolute Adsorption (mg/g)", fontsize=13)
    plt.title("CH₄ Absolute Adsorption Isotherm", fontsize=15)
    plt.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    print(f"Plot saved: {outfile}")

# MAIN
if __name__ == "__main__":
    pressures, loading_mg_g = extract_absolute_loading()

    if pressures is not None:
        plot_absolute_adsorption(pressures, loading_mg_g)
