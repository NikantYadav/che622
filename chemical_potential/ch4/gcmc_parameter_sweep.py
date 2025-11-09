#!/usr/bin/env python3

import numpy as np
import pandas as pd
import subprocess
import os
import time
from pathlib import Path

def create_lammps_input(mu_value, input_filename="ch4_gcmc.inp"):


    lammps_template = f"""# Pure CH4 bulk system setup
units real
dimension 3
boundary p p p
atom_style atomic

# Create simulation box (adjust size as needed)
region box block 0 50 0 50 0 50
create_box 1 box

# Define CH4 mass and interactions using TraPPE-UA model
mass 1 16.04  # CH4 molecular weight

# TraPPE-UA Lennard-Jones parameters for CH4
pair_style lj/cut 14.0
pair_coeff 1 1 0.294106 3.73   # CH4-CH4  # epsilon (kcal/mol), sigma (Angstrom)

# Use Lorentz-Berthelot mixing rules
pair_modify mix arithmetic tail yes

# Temperature and chemical potential settings
variable T equal 313.15  # Temperature in K
variable mu equal {mu_value}  # Chemical potential (kcal/mol)

# Timestep and thermostat
timestep 1.0  # fs
fix thermostat all nvt temp ${{T}} ${{T}} 100.0

# GCMC fix - insertion/deletion of CH4 molecules
fix gcmc all gcmc 2000 500 50 1 49284 ${{T}} ${{mu}} 0.5

# Output thermodynamic properties
thermo_style custom step temp press atoms density
thermo 100

compute_modify thermo_temp dynamic/dof yes


# Run hybrid GCMC/MD simulation
run 200000 

delete_atoms overlap 0.8 all all 
# Fix the ave/time parameters to satisfy constraint
fix avg_press all ave/time 100 10 1000 c_thermo_press file pressure_avg_mu{mu_value}.txt

run 500000 
"""

    with open(input_filename, 'w') as f:
        f.write(lammps_template)

    print(f"✅ Created input file: {input_filename} (μ = {mu_value} kcal/mol)")

def run_lammps_simulation(input_filename, lammps_command):
    """
    Run LAMMPS simulation and wait for completion

    Parameters:
    input_filename (str): LAMMPS input file
    lammps_command (str): Full LAMMPS command

    Returns:
    bool: True if successful, False otherwise
    """

    print(f"🚀 Starting LAMMPS simulation: {input_filename}")
    start_time = time.time()

    try:
        # Run LAMMPS
        full_command = f"{lammps_command} -in {input_filename}"
        result = subprocess.run(full_command, shell=True)

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Simulation completed successfully in {elapsed_time:.1f}s")
            return True
        else:
            print(f"❌ Simulation failed!")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        return False

def analyze_pressure_results(mu_value):
    """
    Analyze pressure results from LAMMPS output

    Parameters:
    mu_value (float): Chemical potential used in simulation

    Returns:
    float: Mean equilibrium pressure or None if failed
    """

    pressure_file = f"pressure_avg_mu{mu_value}.txt"

    try:
        # Read pressure data using pandas (skip comments)
        data = pd.read_csv(pressure_file, sep=r"\s+", comment="#", names=["TimeStep", "Pressure"])

        # Calculate mean pressure
        mean_pressure = np.mean(data["Pressure"])
        std_pressure = np.std(data["Pressure"])
        n_points = len(data)
        std_error = std_pressure / np.sqrt(n_points)

        print(f"📊 μ = {mu_value}: P_eq = {mean_pressure:.3f} ± {std_error:.3f} atm ({n_points} points)")

        return mean_pressure, std_error

    except Exception as e:
        print(f"❌ Error analyzing pressure for μ = {mu_value}: {e}")
        return None, None

def run_parameter_sweep():
    """
    Main function to run complete parameter sweep
    """

    # Configuration
    mu_values = np.arange(-10.0, -4.5, 0.2)  # -10 to -5 in steps of 0.5
    lammps_command = "/scratch/nikant22/openmpi/bin/mpirun -np 40 /scratch/nikant22/lammps-22Jul2025/src/lmp_mpi"

    # Results storage
    results = []

    print("🎯 LAMMPS GCMC Parameter Sweep Started")
    print("=" * 60)
    print(f"Chemical potential range: {mu_values[0]} to {mu_values[-1]} kcal/mol")
    print(f"Number of simulations: {len(mu_values)}")
    print(f"LAMMPS command: {lammps_command}")
    print("=" * 60)

    total_start_time = time.time()

    for i, mu in enumerate(mu_values):
        print(f"\n[{i+1}/{len(mu_values)}] Processing μ = {mu} kcal/mol")
        print("-" * 40)

        # Create input file
        input_file = f"ch4_gcmc_mu{mu}.inp"
        create_lammps_input(mu, input_file)

        # Run simulation
        success = run_lammps_simulation(input_file, lammps_command)

        if success:
            # Analyze results
            mean_pressure, std_error = analyze_pressure_results(mu)

            if mean_pressure is not None:
                results.append({
                    'mu_kcal_mol': mu,
                    'pressure_atm': mean_pressure,
                    'pressure_error_atm': std_error,
                    'status': 'success'
                })
            else:
                results.append({
                    'mu_kcal_mol': mu,
                    'pressure_atm': np.nan,
                    'pressure_error_atm': np.nan,
                    'status': 'analysis_failed'
                })
        else:
            results.append({
                'mu_kcal_mol': mu,
                'pressure_atm': np.nan,
                'pressure_error_atm': np.nan,
                'status': 'simulation_failed'
            })

        # Clean up intermediate files (optional)
        # os.remove(input_file)  # Uncomment to clean up

    # Save results to CSV
    df_results = pd.DataFrame(results)
    csv_filename = "ch4_gcmc_equation_of_state.csv"
    df_results.to_csv(csv_filename, index=False)

    total_time = time.time() - total_start_time

    # Print summary
    print("\n" + "=" * 60)
    print("🏆 PARAMETER SWEEP COMPLETED")
    print("=" * 60)
    print(f"Total time: {total_time/3600:.1f} hours")
    print(f"Results saved to: {csv_filename}")
    print(f"Successful simulations: {df_results['status'].eq('success').sum()}/{len(mu_values)}")

    # Display results table
    successful_results = df_results[df_results['status'] == 'success']
    if not successful_results.empty:
        print("\n📊 EQUATION OF STATE DATA:")
        print(successful_results[['mu_kcal_mol', 'pressure_atm', 'pressure_error_atm']].to_string(index=False))

    return df_results

if __name__ == "__main__":
    # Check if running in correct directory
    if not Path(".").exists():
        print("❌ Please run this script in your simulation directory")
        exit(1)

    # Run the parameter sweep
    results_df = run_parameter_sweep()

    print("\n🎉 Script completed! Check 'ch4_gcmc_equation_of_state.csv' for results.")
