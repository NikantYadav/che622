#!/usr/bin/env python3
import numpy as np
import pandas as pd
import subprocess
import os
import time
from pathlib import Path

def create_lammps_input(mu_value, input_filename="co2_gcmc.inp"):


    lammps_template = f"""units real
dimension 3
boundary p p p
atom_style full

region box block 0 50 0 50 0 50

create_box 3 box &
bond/types 1 &
angle/types 1 &
extra/bond/per/atom 5 &
extra/angle/per/atom 5 &
extra/special/per/atom 10

mass 1 1.0      # Unused type
mass 2 12.011   # C_CO2 (carbon in CO2)
mass 3 15.999   # O_CO2 (oxygen in CO2)

molecule co2template molecule_co2.dat

pair_style lj/cut 14.0
pair_coeff 1 1 0.0 1.0         # Unused type
pair_coeff 2 2 0.053655 2.80   # C_CO2-C_CO2  # epsilon (kcal/mol), sigma (Angstrom)
pair_coeff 3 3 0.156989 3.05   # O_CO2-O_CO2  # epsilon (kcal/mol), sigma (Angstrom)

pair_modify mix arithmetic tail no

bond_style harmonic
bond_coeff 1 1000.0 1.16  

angle_style harmonic
angle_coeff 1 1000.0 180.0

variable T equal 313.15  
variable mu equal {mu_value}

timestep 0.5 
fix thermostat all nvt temp ${{T}} ${{T}} 50.0

fix gcmc all gcmc 2000 500 50 0 49284 ${{T}} ${{mu}} 0.5 mol co2template

thermo_style custom step temp press atoms density
thermo 100

compute_modify thermo_temp dynamic/dof yes

run 200000

fix avg_press all ave/time 10 100 1000 c_thermo_press file pressure_avg_mu{mu_value}.txt

run 500000
"""

    with open(input_filename, 'w') as f:
        f.write(lammps_template)

    print(f"✅ Created input file: {input_filename} (μ = {mu_value} kcal/mol)")

def run_lammps_simulation(input_filename, lammps_command):

    try:
        # Run LAMMPS
        full_command = f"{lammps_command} -in {input_filename}"
        result = subprocess.run(full_command, shell=True)

        if result.returncode == 0:
            print(f"Simulation completed successfully ")
            return True
        else:
            print(f"Simulation failed!")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error running simulation: {e}")
        return False

def analyze_pressure_results(mu_value):

    pressure_file = f"pressure_avg_mu{mu_value}.txt"

    try:
        # Read pressure data using pandas (skip comments)
        data = pd.read_csv(pressure_file, sep=r"\s+", comment="#", names=["TimeStep", "Pressure"])

        # Calculate mean pressure
        mean_pressure = np.mean(data["Pressure"])

        return mean_pressure

    except Exception as e:
        print(f"Error analyzing pressure for μ = {mu_value}: {e}")
        return None, None

def run_parameter_sweep():
    """
    Main function to run complete parameter sweep
    """

    # Configuration
    mu_values = np.arange(-10.0, -4.5, 0.1) 
    lammps_command = "/scratch/nikant22/openmpi/bin/mpirun -np 40 /scratch/nikant22/lammps-22Jul2025/src/lmp_mpi"

    # Results storage
    results = []

    print(f"Chemical potential range: {mu_values[0]} to {mu_values[-1]} kcal/mol")
    print(f"Number of simulations: {len(mu_values)}")

    total_start_time = time.time()

    for i, mu in enumerate(mu_values):
        print(f"\n[{i+1}/{len(mu_values)}] Processing μ = {mu} kcal/mol")
        print("-" * 40)

        # Create input file
        input_file = f"co2_gcmc_mu{mu}.inp"
        create_lammps_input(mu, input_file)

        # Run simulation
        success = run_lammps_simulation(input_file, lammps_command)

        if success:
            # Analyze results
            mean_pressure = analyze_pressure_results(mu)

            if mean_pressure is not None:
                results.append({
                    'mu_kcal_mol': mu,
                    'pressure_atm': mean_pressure,
                })
            else:
                results.append({
                    'mu_kcal_mol': mu,
                    'pressure_atm': np.nan,
                })
        else:
            results.append({
                'mu_kcal_mol': mu,
                'pressure_atm': np.nan,
            })

        # Clean up intermediate files 
        os.remove(input_file)  # Uncomment to clean up

    # Save results to CSV
    df_results = pd.DataFrame(results)
    csv_filename = "co2_gcmc_equation_of_state.csv"
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

    print("\n Script completed! Check 'co2_gcmc_equation_of_state.csv' for results.")
