import numpy as np
import csv

def calculate_fugacity_coeffs(P_bar, y_ch4, y_co2, T_K=313.15, kij=0.0919):
    R = 0.0831446  # L·bar / (mol·K)
    
    props = {
        'ch4': [190.56, 45.99, 0.0114],
        'co2': [304.13, 73.77, 0.2239]
    }

    Tc1, Pc1, w1 = props['ch4']
    Tc2, Pc2, w2 = props['co2']

    b1 = 0.07780 * R * Tc1 / Pc1
    b2 = 0.07780 * R * Tc2 / Pc2

    ac1 = 0.45724 * (R * Tc1)**2 / Pc1
    ac2 = 0.45724 * (R * Tc2)**2 / Pc2

    k1 = 0.37464 + 1.54226 * w1 - 0.26992 * w1**2
    k2 = 0.37464 + 1.54226 * w2 - 0.26992 * w2**2

    Tr1 = T_K / Tc1
    Tr2 = T_K / Tc2

    alpha1 = (1 + k1 * (1 - np.sqrt(Tr1)))**2
    alpha2 = (1 + k2 * (1 - np.sqrt(Tr2)))**2

    a1 = ac1 * alpha1
    a2 = ac2 * alpha2

    a12 = np.sqrt(a1 * a2) * (1 - kij)

    amix = y_ch4**2 * a1 + 2 * y_ch4 * y_co2 * a12 + y_co2**2 * a2
    bmix = y_ch4 * b1 + y_co2 * b2

    A = amix * P_bar / (R * T_K)**2
    B = bmix * P_bar / (R * T_K)

    c3 = 1
    c2 = -(1 - B)
    c1 = A - 3*B**2 - 2*B
    c0 = -(A*B - B**2 - B**3)

    roots = np.roots([c3, c2, c1, c0])
    Z_real = roots[np.isreal(roots)].real
    Z = np.max(Z_real)

    if Z <= B:
        return np.nan, np.nan

    ln_Z_minus_B = np.log(Z - B)
    log_term = np.log((Z + (1 + np.sqrt(2))*B) / (Z + (1 - np.sqrt(2))*B))
    A_over = A / (2 * np.sqrt(2) * B)

    sum_a1 = y_ch4 * a1 + y_co2 * a12
    term1 = (b1 / bmix) * (Z - 1)
    term2 = ln_Z_minus_B
    term3 = A_over * ((2 * sum_a1 / amix) - (b1 / bmix)) * log_term
    phi1 = np.exp(term1 - term2 - term3)

    sum_a2 = y_ch4 * a12 + y_co2 * a2
    term1 = (b2 / bmix) * (Z - 1)
    term3 = A_over * ((2 * sum_a2 / amix) - (b2 / bmix)) * log_term
    phi2 = np.exp(term1 - term2 - term3)

    return phi1, phi2


# ---------------- PRESSURE SWEEP + CSV EXPORT ---------------- #

if __name__ == "__main__":

    y_ch4 = 0.1
    y_co2 = 0.9
    T = 313.15
    kij = 0.0919

    pressures = np.arange(0.5, 150.5, 0.5)  # 0.5 → 150 bar, step = 0.5
    BAR_TO_ATM = 0.986923

    with open("fugacity_table.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Pressure (bar)",
            "Pressure (atm)",
            "phi_CH4",
            "phi_CO2",
            "f_CH4 (bar)",
            "f_CO2 (bar)"
        ])

        for P in pressures:
            P_atm = P * BAR_TO_ATM
            phi_ch4, phi_co2 = calculate_fugacity_coeffs(P, y_ch4, y_co2, T_K=T, kij=kij)

            if np.isnan(phi_ch4):
                writer.writerow([P, P_atm, "nan", "nan", "nan", "nan"])
            else:
                f_ch4 = phi_ch4 * y_ch4 * P
                f_co2 = phi_co2 * y_co2 * P

                writer.writerow([
                    round(P, 2),
                    round(P_atm, 2),
                    round(phi_ch4, 5),
                    round(phi_co2, 5),
                    round(f_ch4, 2),
                    round(f_co2, 2)
                ])


    print("CSV file 'fugacity_table.csv' created successfully!")
