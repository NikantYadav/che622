import numpy as np

def calculate_fugacity_coeffs(P_bar, y_ch4, y_co2, T_K=313.15, kij=0.0919):
    """
    Calculates fugacity coefficients for a CH4-CO2 binary mixture
    using the Peng-Robinson Equation of State (PR-EOS).
    
    Args:
        P_bar (float): Pressure in bar.
        y_ch4 (float): Mole fraction of CH4 (component 1).
        y_co2 (float): Mole fraction of CO2 (component 2).
        T_K (float): Temperature in Kelvin (default 313.15 K).
        kij (float): Binary Interaction Parameter (BIP) (default 0.0919).

    Returns:
        tuple: (phi_ch4, phi_co2) Fugacity coefficients for CH4 and CO2.
               Returns (np.nan, np.nan) on calculation failure (e.g., liquid phase).
    """

    # --- 1. Constants and Component Properties ---
    R = 0.0831446  # L·bar / (mol·K)
    
    # Component properties [Tc(K), Pc(bar), acentric_factor(omega)]
    props = {
        'ch4': [190.56, 45.99, 0.0114],
        'co2': [304.13, 73.77, 0.2239]
    }
    
    T = T_K
    P = P_bar
    
    Tc1, Pc1, w1 = props['ch4']
    Tc2, Pc2, w2 = props['co2']
    
    # --- 2. Calculate Pure Component Parameters (a_i, b_i) ---
    
    # b_i = 0.07780 * R * Tc / Pc
    b1 = 0.07780 * R * Tc1 / Pc1
    b2 = 0.07780 * R * Tc2 / Pc2
    
    # a_c_i = 0.45724 * (R * Tc)^2 / Pc
    ac1 = 0.45724 * (R * Tc1)**2 / Pc1
    ac2 = 0.45724 * (R * Tc2)**2 / Pc2
    
    # kappa_i = 0.37464 + 1.54226 * w - 0.26992 * w^2
    k1 = 0.37464 + 1.54226 * w1 - 0.26992 * w1**2
    k2 = 0.37464 + 1.54226 * w2 - 0.26992 * w2**2
    
    # Tr_i = T / Tc
    Tr1 = T / Tc1
    Tr2 = T / Tc2
    
    # alpha_i = (1 + kappa_i * (1 - sqrt(Tr_i)))^2
    alpha1 = (1 + k1 * (1 - np.sqrt(Tr1)))**2
    alpha2 = (1 + k2 * (1 - np.sqrt(Tr2)))**2
    
    # a_i(T) = a_c_i * alpha_i
    a1 = ac1 * alpha1
    a2 = ac2 * alpha2
    
    # --- 3. Apply Mixing Rules (van der Waals one-fluid) ---
    
    # a_ij = sqrt(a_i * a_j) * (1 - k_ij)
    a11 = a1
    a22 = a2
    a12 = np.sqrt(a1 * a2) * (1 - kij)
    a21 = a12 # Symmetric
    
    # a_mix = sum(sum(y_i * y_j * a_ij))
    amix = y_ch4**2 * a11 + 2 * y_ch4 * y_co2 * a12 + y_co2**2 * a22
    
    # b_mix = sum(y_i * b_i)
    bmix = y_ch4 * b1 + y_co2 * b2
    
    # --- 4. Calculate Mixture EOS Parameters (A, B) ---
    A = amix * P / (R * T)**2
    B = bmix * P / (R * T)
    
    # --- 5. Solve Cubic EOS for Z (Compressibility Factor) ---
    # Z^3 - (1-B)Z^2 + (A - 3B^2 - 2B)Z - (AB - B^2 - B^3) = 0
    c3 = 1.0
    c2 = -(1 - B)
    c1 = (A - 3*B**2 - 2*B)
    c0 = -(A*B - B**2 - B**3)
    
    roots = np.roots([c3, c2, c1, c0])
    
    # Find real roots and select the largest positive one (gas phase)
    real_roots = roots[np.isreal(roots)].real
    Z_gas = np.max(real_roots)
    
    # Stability check: Z must be greater than B for log(Z-B)
    if Z_gas <= B:
        # This typically indicates the state is liquid or supercritical
        return np.nan, np.nan
        
    # --- 6. Calculate Fugacity Coefficients (phi_i) ---
    
    # This is the full equation for ln(phi_i) derived from PR-EOS
    # ln(phi_i) = (b_i/b_mix)(Z-1) - ln(Z-B) 
    #            - (A / (2*sqrt(2)*B)) * [2*sum(y_j*a_ij) / a_mix - b_i/b_mix] 
    #            * ln((Z + (1+sqrt(2))B) / (Z + (1-sqrt(2))B))
    
    # Pre-calculate common terms
    term_Z_minus_1 = Z_gas - 1
    term_ln_Z_B = np.log(Z_gas - B)
    
    # Note: 1+sqrt(2) = 2.414... and 1-sqrt(2) = -0.414...
    term_log_Z = np.log((Z_gas + (1 + np.sqrt(2)) * B) / (Z_gas + (1 - np.sqrt(2)) * B))
    term_A_B = A / (2 * np.sqrt(2) * B)
    
    # For CH4 (i=1)
    b_ratio_1 = b1 / bmix
    sum_a1 = y_ch4 * a11 + y_co2 * a12  # sum(y_j * a_1j)
    term_bracket_1 = (2 * sum_a1 / amix) - b_ratio_1
    
    ln_phi_1 = b_ratio_1 * term_Z_minus_1 - term_ln_Z_B - term_A_B * term_bracket_1 * term_log_Z
    phi_1 = np.exp(ln_phi_1)
    
    # For CO2 (i=2)
    b_ratio_2 = b2 / bmix
    sum_a2 = y_ch4 * a21 + y_co2 * a22  # sum(y_j * a_2j)
    term_bracket_2 = (2 * sum_a2 / amix) - b_ratio_2
    
    ln_phi_2 = b_ratio_2 * term_Z_minus_1 - term_ln_Z_B - term_A_B * term_bracket_2 * term_log_Z
    phi_2 = np.exp(ln_phi_2)
    
    return phi_1, phi_2

# --- Main execution ---
if __name__ == "__main__":
    
    # Define the mole fractions for CH4 (Component 1)
    ch4_mole_fractions = [0.90, 0.70, 0.50, 0.30, 0.10]
    
    # Define the pressures to calculate
    # Using 21 points from 1 bar to 101 bar (steps of 5)
    pressures = np.linspace(1, 101, 21)
    
    T_TARGET = 313.15  # K
    KIJ_TARGET = 0.0919  # CH4-CO2 BIP
    
    print(f"--- Fugacity Calculation for CH4-CO2 Mixture ---")
    print(f"--- T = {T_TARGET} K, k_ij = {KIJ_TARGET} ---")
    print("-" * 65)

    # Loop over each composition
    for y1 in ch4_mole_fractions:
        y2 = 1.0 - y1
        
        print(f"\nCOMPOSITION: {y1*100:.0f}% CH4 / {y2*100:.0f}% CO2")
        print("=" * 65)
        print(f"{'Pressure (bar)':<15} | {'Phi_CH4':<10} | {'Phi_CO2':<10} | {'f_CH4 (bar)':<12} | {'f_CO2 (bar)':<12}")
        print("-" * 65)
        
        # Loop over each pressure for this composition
        for P in pressures:
            phi_ch4, phi_co2 = calculate_fugacity_coeffs(P, y1, y2, T_K=T_TARGET, kij=KIJ_TARGET)
            
            if np.isnan(phi_ch4):
                print(f"{P:<15.2f} | {'Liquid Phase or Invalid':<49}")
                continue
                
            # Fugacity (f_i) = phi_i * y_i * P
            f_ch4 = phi_ch4 * y1 * P
            f_co2 = phi_co2 * y2 * P
            
            print(f"{P:<15.2f} | {phi_ch4:<10.4f} | {phi_co2:<10.4f} | {f_ch4:<12.4f} | {f_co2:<12.4f}")