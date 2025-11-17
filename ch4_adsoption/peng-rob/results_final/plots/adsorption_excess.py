#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob

# CONSTANTS
R_GAS = 0.083144626                 # L·bar/(mol·K)
AVOGADRO = 6.02214076e23            # molecules/mol
MW_CH4 = 16.04                      # g/mol
COAL_MASS_MG = 28603.9              # mg (corrected)
COAL_MASS_G = COAL_MASS_MG / 1000.0 # g
T = 298.15                           # K (simulation temp)

# INSERT YOUR SYSTEM VOLUME HERE
SYSTEM_VOLUME_A3 = 2349.095   # Å³  <--- REPLACE IF NEEDED

# Bulk density (ideal gas)
def bulk_density_molec_A3(P_bar):
    rho_mol_L = P_bar / (R_GAS * T)              # mol/L
    rho_molec_A3 = rho_mol_L * AVOGADRO / 1e27   # molec/Å³
    return rho_molec_A3

# Extract data & compute excess adsorption
def extract_excess_loading(file_pattern='isotherm_P*.dat'):
    files = sorted(glob.glob(file_pattern))
    if not files:
        print("No isotherm files found!")
        return None, None

    pressures = []
    n_ch4 = []

    # Read pressure and N_CH4 molecules
    for filename in files:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    continue
                data = line.strip().split()
                if len(data) >= 2:
                    pressures.append(float(data[0]))
                    n_ch4.append(float(data[1]))

    pressures = np.array(pressures)
    n_ch4 = np.array(n_ch4)

    # Sort by pressure
    idx = np.argsort(pressures)
    pressures = pressures[idx]
    n_ch4 = n_ch4[idx]

    # Calculate EXCESS adsorption
    loading_excess_mg = []

    for P, n_abs in zip(pressures, n_ch4):
        # Bulk gas molecules
        rho_bulk = bulk_density_molec_A3(P)
        n_bulk = rho_bulk * SYSTEM_VOLUME_A3

        # Excess molecules
        n_excess = n_abs - n_bulk

        # Convert to mg/g
        n_excess_mol = n_excess / AVOGADRO
        loading_mg = (n_excess_mol * MW_CH4 * 1000.0) / COAL_MASS_G
        loading_excess_mg.append(loading_mg)

    return pressures, np.array(loading_excess_mg)

# Plot excess adsorption mg/g
def plot_excess_adsorption(pressures, loading, outfile="excess_adsorption_mg_per_g.png"):
    plt.figure(figsize=(8,6))

    plt.scatter(pressures, loading, s=120, edgecolors='black')
    plt.plot(pressures, loading, linewidth=1.5)

    plt.xlabel("Pressure (bar)", fontsize=13)
    plt.ylabel("Excess Adsorption (mg/g)", fontsize=13)
    plt.title("CH₄ Excess Adsorption Isotherm (mg/g)", fontsize=15)
    plt.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    print(f"Plot saved: {outfile}")

# MAIN
if __name__ == "__main__":
    pressures, loading_excess_mg = extract_excess_loading()

    if pressures is not None:
        plot_excess_adsorption(pressures, loading_excess_mg)
