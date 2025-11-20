import numpy as np
import matplotlib.pyplot as plt

# Read data
data = np.loadtxt('adsorption_data.txt', skiprows=1)
steps = data[:, 0]
n_ch4 = data[:, 1]
n_co2 = data[:, 2]

# Plot time series
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

axes[0].plot(steps, n_ch4, label='CH4')
axes[0].set_ylabel('Number of CH4 molecules')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(steps, n_co2, label='CO2', color='red')
axes[1].set_ylabel('Number of CO2 molecules')
axes[1].set_xlabel('Steps')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('convergence_check.png')

# Calculate running average (last 50%)
production_start = len(n_ch4) // 2
print(f"Production average CH4: {np.mean(n_ch4[production_start:])} ± {np.std(n_ch4[production_start:])}")
print(f"Production average CO2: {np.mean(n_co2[production_start:])} ± {np.std(n_co2[production_start:])}")

# Check if stable (compare first and second halves of production)
mid = production_start + (len(n_ch4) - production_start) // 2
first_half_mean = np.mean(n_ch4[production_start:mid])
second_half_mean = np.mean(n_ch4[mid:])
relative_diff = abs(first_half_mean - second_half_mean) / first_half_mean * 100

print(f"Relative difference between production halves: {relative_diff:.2f}%")
if relative_diff < 5:
    print("✓ Simulation appears converged")
else:
    print("✗ May need longer simulation")
