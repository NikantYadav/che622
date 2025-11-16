import numpy as np

# Function from your script
def calculate_pr_properties(pressure_bar, T_K, Pc_bar, Tc_K, omega):
    R_gas_const = 83.14  # cm^3*bar/(mol*K)
    R_energy = 0.008314  # kJ/(mol*K)
    P_ref = 1.0  # bar

    if pressure_bar == 0:
        return 0.0, 1.0, 0.0, -np.inf

    Tr = T_K / Tc_K
    ac = 0.45724 * (R_gas_const**2 * Tc_K**2) / Pc_bar
    b = 0.07780 * (R_gas_const * Tc_K) / Pc_bar
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
    a = ac * alpha

    A = a * pressure_bar / (R_gas_const * T_K)**2
    B = b * pressure_bar / (R_gas_const * T_K)
    
    coeffs = [1, -(1 - B), (A - 3*B**2 - 2*B), -(A*B - B**2 - B**3)]
    roots = np.roots(coeffs)
    Z_real = roots[np.isreal(roots)].real
    Z = max(Z_real)

    term1 = Z - 1
    term2 = -np.log(Z - B)
    term3 = -(A / (2 * np.sqrt(2) * B)) * np.log((Z + 2.414 * B) / (Z - 0.414 * B))
    log_phi = term1 + term2 + term3
    phi = np.exp(log_phi)
    
    fugacity = phi * pressure_bar
    mu_residual = R_energy * T_K * log_phi
    mu_input = R_energy * T_K * np.log(fugacity / P_ref)
    
    return fugacity, phi, mu_residual, mu_input

# Gas properties
params = {
    "CH4": {"Tc_K": 190.56, "Pc_bar": 45.992, "omega": 0.012},
    "CO2": {"Tc_K": 304.13, "Pc_bar": 73.773, "omega": 0.224}
}

# Target temperature
T_TARGET = 313.15  # K

# --- Ask for user input ---
P_input = float(input("Enter pressure (bar): "))

# Calculate chemical potentials
f_ch4, phi_ch4, mu_res_ch4, mu_in_ch4 = calculate_pr_properties(P_input, T_TARGET, **params["CH4"])
f_co2, phi_co2, mu_res_co2, mu_in_co2 = calculate_pr_properties(P_input, T_TARGET, **params["CO2"])

# Print results
print(f"\nAt P = {P_input} bar and T = {T_TARGET} K:")
print(f"CH4: mu_input = {mu_in_ch4:.3f} kJ/mol, mu_residual = {mu_res_ch4:.3f} kJ/mol")
print(f"CO2: mu_input = {mu_in_co2:.3f} kJ/mol, mu_residual = {mu_res_co2:.3f} kJ/mol")
