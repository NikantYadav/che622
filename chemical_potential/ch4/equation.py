import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import os

# === Load your data ===
csv_path = os.path.join(os.path.dirname(__file__), 'ch4.csv')

def load_mu_p(path):
    mu_list, p_list = [], []
    with open(path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue
            try:
                mu_val = float(parts[0])
                p_val = float(parts[1])
            except ValueError:
                continue
            mu_list.append(mu_val)
            p_list.append(p_val)
    if not mu_list:
        raise RuntimeError(f"No valid data rows found in {path}")
    return np.array(mu_list), np.array(p_list)

mu, P = load_mu_p(csv_path)

# === Model definitions ===
def rational(P, a, b, c, d):
    return (a + b * P) / (1 + c * P + d * P**2)

def rational2(P, a, b, e, c, d):
    return (a + b * P + e * P**2) / (1 + c * P + d * P**2)

def model_log_poly(P, A, B, C, D):
    return A + B * np.log(P) + C * P + D * P**2

def rational_exp(P, a, b, c, d):
    return (a + b * P) / (1 + np.exp(c * P + d))

# === Model dictionary ===
models = {
    "Rational (deg 2)": (rational, [-8.9, -0.4, 0.06, 2e-5]),
    "Rational (deg 3 numerator)": (rational2, [-8.9, -0.4, 0.05, 0.06, 2e-5]),
    "Log + Poly": (model_log_poly, [-9, 1, 0.1, 0.001]),
    "Rational-Exp": (rational_exp, [-8.9, -0.4, -0.1, 0]),
}

# === Fit all models ===
results = []
for name, (func, p0) in models.items():
    try:
        popt, _ = curve_fit(func, P, mu, p0=p0, maxfev=50000)
        mu_pred = func(P, *popt)
        r2 = r2_score(mu, mu_pred)
        results.append((name, r2, func, popt))
    except Exception as e:
        print(f"{name}: fitting failed ({e})")

# === Polynomial (deg 5) ===
deg = 5
coeffs = np.polyfit(P, mu, deg)
poly = np.poly1d(coeffs)
mu_poly = poly(P)
r2_poly = r2_score(mu, mu_poly)
results.append((f"Polynomial (deg {deg})", r2_poly, poly, None))

# === Print summary ===
print("\nModel Performance Summary:")
print("="*45)
for name, r2, _, _ in results:
    print(f"{name:<35s} R² = {r2:.6f}")

# === Find best model ===
best_model = max(results, key=lambda x: x[1])
best_name, best_r2, best_func, best_params = best_model
print(f"\nBest model: {best_name} (R² = {best_r2:.6f})")

# === Reference model ===
def reference_model(P):
    return (-8.87674 - 0.39316 * P) / (1 + 0.06257 * P + 0.00002 * P**2)

# === Plot ===
P_range = np.linspace(P.min(), P.max(), 500)
plt.figure(figsize=(10,7))
plt.scatter(P, mu, color='black', s=25, label="Data")

colors = plt.cm.tab10(np.linspace(0, 1, len(results)))

for (name, r2, func, params), color in zip(results, colors):
    if params is None:
        mu_fit = func(P_range)
    else:
        mu_fit = func(P_range, *params)
    plt.plot(P_range, mu_fit, lw=2, color=color, label=f"{name} (R²={r2:.4f})")

plt.plot(P_range, reference_model(P_range), 'k--', lw=2, label="Reference model")

# === Display best-fit equation on plot ===
if best_params is not None:
    eq_text = f"{best_name}\nμ = "
    if "Rational" in best_name:
        if len(best_params) == 4:
            a, b, c, d = best_params
            eq_text += f"({a:.3f} + {b:.3f}P) / (1 + {c:.3f}P + {d:.5f}P²)"
        elif len(best_params) == 5:
            a, b, e, c, d = best_params
            eq_text += f"({a:.3f} + {b:.3f}P + {e:.3f}P²) / (1 + {c:.3f}P + {d:.5f}P²)"
    elif "Log" in best_name:
        A, B, C, D = best_params
        eq_text += f"{A:.3f} + {B:.3f}ln(P) + {C:.3f}P + {D:.5f}P²"
    elif "Exp" in best_name:
        a, b, c, d = best_params
        eq_text += f"({a:.3f} + {b:.3f}P) / (1 + exp({c:.3f}P + {d:.3f}))"
else:
    eq_text = f"{best_name}\nμ = " + " + ".join([f"{c:.3e}P^{i}" for i, c in enumerate(best_func.coefficients[::-1])])

plt.text(0.05, 0.05, f"Best Model: {eq_text}\nR²={best_r2:.5f}",
         transform=plt.gca().transAxes, fontsize=9, bbox=dict(facecolor='white', alpha=0.7))

# === Final styling ===
plt.xlabel("Pressure (bar)")
plt.ylabel("Chemical potential (kcal/mol)")
plt.title("μ–P Curve Comparison (Best Model Highlighted)")
plt.legend(fontsize=9)
plt.grid(True)
plt.tight_layout()
plt.show()
