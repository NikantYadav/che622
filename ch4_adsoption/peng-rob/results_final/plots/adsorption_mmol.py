#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob

# CONSTANTS
AVOGADRO = 6.02214076e23         # molecules/mol
COAL_MASS_MG = 28603.9           # mg
COAL_MASS_G = COAL_MASS_MG / 1000.0   # g

# Extract data and calculate mmol/g
def extract_absolute_loading_mmol(file_pattern='isotherm_P*.dat'):
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

    # Sort by pressure
    idx = np.argsort(pressures)
    pressures = pressures[idx]
    n_ch4_list = n_ch4_list[idx]

    # Recalculate absolute loading (mmol/g)
    loading_mmol_g = []
    for n in n_ch4_list:
        n_mol = n / AVOGADRO                 # moles
        loading = (n_mol * 1000.0) / COAL_MASS_G   # mmol/g
        loading_mmol_g.append(loading)

    return pressures, np.array(loading_mmol_g)

# Plot absolute adsorption in mmol/g
def plot_absolute_adsorption_mmol(pressures, loading_mmol_g, outfile="absolute_adsorption_mmol.png"):
    plt.figure(figsize=(8,6))

    plt.scatter(pressures, loading_mmol_g, s=120, edgecolors='black')
    plt.plot(pressures, loading_mmol_g, linewidth=1.5)

    plt.xlabel("Pressure (bar)", fontsize=13)
    plt.ylabel("Absolute Adsorption (mmol/g)", fontsize=13)
    plt.title("CH₄ Absolute Adsorption Isotherm (mmol/g)", fontsize=15)
    plt.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    print(f"Plot saved: {outfile}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    pressures, loading_mmol_g = extract_absolute_loading_mmol()

    if pressures is not None:
        plot_absolute_adsorption_mmol(pressures, loading_mmol_g)
