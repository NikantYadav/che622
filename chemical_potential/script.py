import numpy as np
import pandas as pd

def calculate_pr_properties(pressure_bar, T_K, Pc_bar, Tc_K, omega):
    """
    Calculates fugacity and chemical potential using the Peng-Robinson EOS.
    
    All inputs must be in consistent units (bar, K).
    Returns:
    - fugacity (bar)
    - phi (fugacity_coefficient)
    - mu_residual (kJ/mol)
    - mu_input (kJ/mol, relative to 1 bar)
    """
    
    # 1. Constants
    R_gas_const = 83.14  # cm^3*bar/(mol*K)
    R_energy = 0.008314  # kJ/(mol*K)
    P_ref = 1.0  # Reference pressure in bar
    
    # Handle P=0 case
    if pressure_bar == 0:
        return 0.0, 1.0, 0.0, -np.inf

    # 2. Calculate P-R parameters
    Tr = T_K / Tc_K
    ac = 0.45724 * (R_gas_const**2 * Tc_K**2) / Pc_bar
    b = 0.07780 * (R_gas_const * Tc_K) / Pc_bar
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
    a = ac * alpha

    # 3. Solve Cubic EOS for Z
    A = a * pressure_bar / (R_gas_const * T_K)**2
    B = b * pressure_bar / (R_gas_const * T_K)
    
    coeffs = [1, -(1 - B), (A - 3*B**2 - 2*B), -(A*B - B**2 - B**3)]
    roots = np.roots(coeffs)
    Z_real = roots[np.isreal(roots)].real
    Z = max(Z_real)

    # 4. Calculate Fugacity Coefficient (phi)
    term1 = Z - 1
    term2 = -np.log(Z - B)
    term3 = -(A / (2 * np.sqrt(2) * B)) * np.log((Z + 2.414 * B) / (Z - 0.414 * B))
    log_phi = term1 + term2 + term3
    phi = np.exp(log_phi)
    
    # 5. Calculate Fugacity
    fugacity = phi * pressure_bar
    
    # 6. Calculate Chemical Potentials (in kJ/mol)
    mu_residual = R_energy * T_K * log_phi
    mu_input = R_energy * T_K * np.log(fugacity / P_ref)
    
    return fugacity, phi, mu_residual, mu_input


# Define conditions
T_TARGET = 313.15  # K 

# Pressure range: 0.5 to 60 bar with 30 points for GCMC simulations
pressures_bar = np.linspace(0.5, 60, 17)

# Gas properties
params = {
    "CH4": {"Tc_K": 190.56, "Pc_bar": 45.992, "omega": 0.012},
    "CO2": {"Tc_K": 304.13, "Pc_bar": 73.773, "omega": 0.224}
}

# --- Calculate for CH4 ---
print(f"=== Methane (CH4) at {T_TARGET} K ===")
print("P (bar) |  f (bar) |   Phi   | mu_res (kJ/mol) | mu_input (kJ/mol)")
print("--------------------------------------------------------------------")

ch4_data = []
for P in pressures_bar:
    f, phi, mu_res, mu_in = calculate_pr_properties(P, T_TARGET, **params["CH4"])
    print(f"{P:7.2f} | {f:8.3f} | {phi:7.4f} | {mu_res:15.3f} | {mu_in:17.3f}")
    ch4_data.append({
        'Pressure_bar': P,
        'Fugacity_bar': f,
        'Phi': phi,
        'mu_residual_kJ_mol': mu_res,
        'mu_input_kJ_mol': mu_in
    })

print(f"\n=== Carbon Dioxide (CO2) at {T_TARGET} K ===")
print("P (bar) |  f (bar) |   Phi   | mu_res (kJ/mol) | mu_input (kJ/mol)")
print("--------------------------------------------------------------------")

co2_data = []
for P in pressures_bar:
    f, phi, mu_res, mu_in = calculate_pr_properties(P, T_TARGET, **params["CO2"])
    print(f"{P:7.2f} | {f:8.3f} | {phi:7.4f} | {mu_res:15.3f} | {mu_in:17.3f}")
    co2_data.append({
        'Pressure_bar': P,
        'Fugacity_bar': f,
        'Phi': phi,
        'mu_residual_kJ_mol': mu_res,
        'mu_input_kJ_mol': mu_in
    })

# Create DataFrames and save to CSV files
df_ch4 = pd.DataFrame(ch4_data)
df_co2 = pd.DataFrame(co2_data)

df_ch4.to_csv('CH4_chemical_potential_GCMC.csv', index=False)
df_co2.to_csv('CO2_chemical_potential_GCMC.csv', index=False)

print("\n✓ Data saved to CSV files:")
print("  - CH4_chemical_potential_GCMC.csv")
print("  - CO2_chemical_potential_GCMC.csv")

# --- Summary Table ---
print("\n" + "="*70)
print(f"Temperature: {T_TARGET} K")
print(f"Pressure range: {pressures_bar[0]:.1f} - {pressures_bar[-1]:.1f} bar")
print(f"Number of points: {len(pressures_bar)}")
print("="*70)
