import re
import subprocess
import time
import os
import csv

# === User settings ===
input_file = "ch4.inp"
results_file = "ch4_results_summary.txt"
data_file = "ch4_gcmc_data.dat"
csv_log = "mu_pressure_log.csv"

host_dir = os.path.abspath(os.getcwd())
lammps_command = [
    "docker", "run", "-it", "--rm",
    "-v", f"{host_dir}:/data",
    "-w", "/data",
    "lammps/lammps",
    "mpirun", "-np", "8", "lmp_mpi", "-in", os.path.basename(input_file)
]

mu_start = -15.0     # starting chemical potential
mu_step = 0.5        # increment per step
max_pressure = 700   # bar target
sleep_time = 2       # seconds to wait before checking file after run
max_iterations = 30  # safety limit


def update_mu_in_inp(filename, mu_value):
    """Update the mu variable line in the LAMMPS input file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in lines:
            if line.strip().startswith("variable") and "mu equal" in line:
                f.write(f"variable        mu equal {mu_value:.2f} # <-- SET CHEMICAL POTENTIAL HERE (kcal/mol)\n")
            else:
                f.write(line)

def compute_avg_pressure_from_datafile(filename):
    """Compute the average of c_thermo_press column from ch4_gcmc_data.dat."""
    if not os.path.exists(filename):
        print(f"⚠️ Warning: Data file '{filename}' not found.")
        return None

    pressures = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    pressures.append(float(parts[2]))  # column index 2 → c_thermo_press
                except ValueError:
                    continue

    if not pressures:
        print("⚠️ No valid pressure values found in data file.")
        return None

    avg_press = sum(pressures) / len(pressures)
    return avg_press


def append_to_csv(mu_value, avg_pressure, csv_filename):
    """Append mu and pressure to CSV log."""
    file_exists = os.path.exists(csv_filename)
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["mu (kcal/mol)", "Average Pressure (bar)"])
        writer.writerow([mu_value, avg_pressure])


# === Main loop ===
mu = mu_start
iteration = 0

while iteration < max_iterations:
    iteration += 1
    print(f"\n=== Iteration {iteration}: Running with mu = {mu:.2f} kcal/mol ===")

    # 1. Update input file
    update_mu_in_inp(input_file, mu)

    # 2. Run LAMMPS
    print("Running LAMMPS simulation...")
    subprocess.run(lammps_command, check=True)

    # 3. Wait for results file
    time.sleep(sleep_time)

    # 5. Extract average pressure from data file
    avg_press = compute_avg_pressure_from_datafile(data_file)
    if avg_press is not None:
        print(f"→ Average pressure from data file: {avg_press:.2f} bar")
        append_to_csv(mu, avg_press, csv_log)
        print(f"Logged (mu={mu:.2f}, avg_press={avg_press:.2f}) to {csv_log}")
    else:
        print("⚠️ Skipping CSV logging (no valid data).")

    # 6. Check stop condition
    if avg_press >= max_pressure:
        print(f"✅ Target reached: Pressure = {avg_press:.2f} bar at mu = {mu:.2f}")
        break

    # 7. Adjust mu for next run
    mu += mu_step

else:
    print("⚠️ Reached maximum number of iterations without hitting target pressure.")

print("Simulation series complete.")
