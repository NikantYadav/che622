import numpy as np
import matplotlib.pyplot as plt

def calculate_fugacity_coeffs(P_bar, y_co2, y_co, T_K=313.15, kij=-0.01):
    import numpy as np
    R = 0.0831446

    # Critical properties: Tc(K), Pc(bar), omega
    props = {
        'co2': [304.13, 73.77, 0.2239],
        'co':  [132.92, 34.99, 0.0480]
    }

    T = T_K
    P = P_bar
    Tc1, Pc1, w1 = props['co2']
    Tc2, Pc2, w2 = props['co']

    # PR parameters
    b1 = 0.07780 * R * Tc1 / Pc1
    b2 = 0.07780 * R * Tc2 / Pc2
    ac1 = 0.45724 * (R * Tc1)**2 / Pc1
    ac2 = 0.45724 * (R * Tc2)**2 / Pc2

    k1 = 0.37464 + 1.54226*w1 - 0.26992*w1**2
    k2 = 0.37464 + 1.54226*w2 - 0.26992*w2**2

    Tr1 = T/Tc1
    Tr2 = T/Tc2

    alpha1 = (1 + k1*(1 - np.sqrt(Tr1)))**2
    alpha2 = (1 + k2*(1 - np.sqrt(Tr2)))**2

    a1 = ac1*alpha1
    a2 = ac2*alpha2
    a11 = a1
    a22 = a2
    a12 = np.sqrt(a1*a2)*(1 - kij)

    amix = y_co2**2*a11 + 2*y_co2*y_co*a12 + y_co**2*a22
    bmix = y_co2*b1 + y_co*b2

    A = amix * P / (R*T)**2
    B = bmix * P / (R*T)

    # Cubic coefficients
    c3 = 1
    c2 = -(1 - B)
    c1 = A - 3*B**2 - 2*B
    c0 = -(A*B - B**2 - B**3)

    roots = np.roots([c3, c2, c1, c0])
    real_roots = roots[np.isreal(roots)].real
    Z = np.max(real_roots)

    if Z <= B:
        return np.nan, np.nan

    lnZB = np.log(Z - B)
    term_log = np.log((Z + (1+np.sqrt(2))*B)/(Z + (1-np.sqrt(2))*B))
    term_A_B = A/(2*np.sqrt(2)*B)

    # CO2 fugacity coefficient
    b_ratio1 = b1/bmix
    sum_a1 = y_co2*a11 + y_co*a12
    bracket1 = 2*sum_a1/amix - b_ratio1
    ln_phi1 = b_ratio1*(Z-1) - lnZB - term_A_B * bracket1 * term_log

    # CO fugacity coefficient
    b_ratio2 = b2/bmix
    sum_a2 = y_co2*a12 + y_co*a22
    bracket2 = 2*sum_a2/amix - b_ratio2
    ln_phi2 = b_ratio2*(Z-1) - lnZB - term_A_B * bracket2 * term_log

    return np.exp(ln_phi1), np.exp(ln_phi2)


# ------------------------------------------------------------
# MAIN SCRIPT — SINGLE PLOT WITH BOTH SPECIES
# ------------------------------------------------------------
co2_fracs = [0.9, 0.7, 0.5, 0.3, 0.1]
pressures = np.linspace(1, 101, 21)

T = 313.15
kij = -0.01

markers = ["s", "o", "^", "D", "v"]  # marker shapes for different compositions

plt.figure(figsize=(8, 6))

for (y1, m) in zip(co2_fracs, markers):
    y2 = 1 - y1

    Ps_MPa = []
    phi_CO = []
    phi_CO2 = []

    for P in pressures:
        phi1, phi2 = calculate_fugacity_coeffs(P, y1, y2, T, kij)
        if not np.isnan(phi1):
            Ps_MPa.append(P/10)   # bar → MPa
            phi_CO2.append(phi1)
            phi_CO.append(phi2)

    # CO fugacity
    plt.plot(Ps_MPa, phi_CO, marker=m, linewidth=1.8,
             label=f"y_CO={y2:.1f}(CO)")

    # CO₂ fugacity
    plt.plot(Ps_MPa, phi_CO2, marker=m, linestyle='--', linewidth=1.8,
             label=f"y_CO₂={y1:.1f}(CO₂)")


plt.xlabel("Pressure / MPa")
plt.ylabel("Fugacity coefficient")
plt.title("Fugacity Coefficients of CO and CO₂ vs Pressure")
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=9, ncol=2)
plt.tight_layout()
plt.show()
