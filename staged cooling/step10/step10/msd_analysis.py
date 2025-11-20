import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

class CoalMSDAnalyzer:
    """Analyze MSD data for diffusion and stability validation"""
    
    def __init__(self, msd_file, timestep=1.0, units='real'):
        """
        Parameters:
        - msd_file: Path to LAMMPS MSD output file
        - timestep: Simulation timestep (fs for 'real' units)
        - units: LAMMPS units system ('real', 'metal', etc.)
        """
        self.timestep = timestep
        self.units = units
        self.load_msd(msd_file)
    
    def load_msd(self, filename):
        """Load MSD data from LAMMPS output"""
        data = []
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#') or line.strip() == '':
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        # Column 0: timestep, Column 1: MSD
                        data.append([float(parts[0]), float(parts[1])])
                    except ValueError:
                        continue
        
        data = np.array(data)
        self.timesteps = data[:, 0]
        self.msd = data[:, 1]  # Å²
        
        # Convert timesteps to time (ps for 'real' units)
        if self.units == 'real':
            self.time = self.timesteps * self.timestep / 1000.0  # ps
        else:
            self.time = self.timesteps * self.timestep
        
        print(f"Loaded MSD: {len(self.time)} data points")
        print(f"Time range: {self.time[0]:.2f} - {self.time[-1]:.2f} ps")
        print(f"MSD range: {self.msd[0]:.4f} - {self.msd[-1]:.4f} Å²")
    
    def calculate_diffusion_coefficient(self, start_frac=0.5):
        """
        Calculate diffusion coefficient from MSD slope
        D = slope / 6 (for 3D)
        
        Parameters:
        - start_frac: Fraction of data to skip (use linear region)
        """
        # Use second half of data for linear fit (after equilibration)
        start_idx = int(len(self.time) * start_frac)
        time_fit = self.time[start_idx:]
        msd_fit = self.msd[start_idx:]
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = linregress(time_fit, msd_fit)
        
        # Diffusion coefficient: D = slope / 6 (3D)
        # Convert from Å²/ps to m²/s: multiply by 1e-8
        D_ang2_ps = slope / 6.0
        D_m2_s = D_ang2_ps * 1e-8
        
        print("\n=== Diffusion Coefficient Analysis ===")
        print(f"MSD slope: {slope:.6f} Å²/ps")
        print(f"Diffusion coefficient (D): {D_ang2_ps:.6e} Å²/ps")
        print(f"Diffusion coefficient (D): {D_m2_s:.6e} m²/s")
        print(f"R² value: {r_value**2:.4f}")
        print(f"Standard error: {std_err:.6e}")
        
        return D_ang2_ps, D_m2_s, slope, intercept, r_value**2
    
    def validate_coal_stability(self, D_m2_s):
        """Validate that structure represents solid coal"""
        print("\n=== Coal Structure Stability Validation ===")
        
        # Expected diffusion for solid coal: < 1e-15 m²/s
        # Gas molecules in coal: ~1e-9 to 1e-11 m²/s
        
        if D_m2_s < 1e-15:
            print(f"✓ STABLE COAL STRUCTURE")
            print(f"  D = {D_m2_s:.2e} m²/s < 1e-15 m²/s")
            print(f"  Structure represents rigid coal framework")
        elif 1e-15 <= D_m2_s < 1e-12:
            print(f"⚠ PARTIALLY MOBILE STRUCTURE")
            print(f"  D = {D_m2_s:.2e} m²/s")
            print(f"  May indicate: incomplete relaxation or amorphous regions")
        else:
            print(f"✗ MOBILE STRUCTURE - NOT SOLID COAL")
            print(f"  D = {D_m2_s:.2e} m²/s > 1e-12 m²/s")
            print(f"  Structure is too mobile for solid coal")
        
        # Check MSD magnitude
        msd_total = self.msd[-1] - self.msd[0]
        print(f"\nTotal MSD change: {msd_total:.4f} Å²")
        
        if msd_total < 1.0:
            print("✓ Low MSD indicates thermal vibrations only")
        elif 1.0 <= msd_total < 5.0:
            print("⚠ Moderate MSD - check equilibration")
        else:
            print("✗ Large MSD indicates structural instability")
    
    def plot_msd(self, D_params=None, save_file='msd_analysis.png'):
        """Plot MSD vs time with linear fit"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Full MSD
        ax1.plot(self.time, self.msd, 'b-', linewidth=2, label='MSD data')
        
        if D_params is not None:
            D_ang2_ps, D_m2_s, slope, intercept, r2 = D_params
            fit_line = slope * self.time + intercept
            ax1.plot(self.time, fit_line, 'r--', linewidth=2, 
                    label=f'Linear fit (R²={r2:.4f})')
            ax1.text(0.05, 0.95, f'D = {D_m2_s:.2e} m²/s', 
                    transform=ax1.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round', 
                    facecolor='wheat', alpha=0.8))
        
        ax1.set_xlabel('Time (ps)', fontsize=12)
        ax1.set_ylabel('MSD (Å²)', fontsize=12)
        ax1.set_title('Mean Square Displacement', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: MSD derivative (instantaneous diffusion)
        if len(self.time) > 10:
            msd_deriv = np.gradient(self.msd, self.time)
            ax2.plot(self.time, msd_deriv, 'g-', linewidth=2)
            ax2.axhline(y=6*D_params[0] if D_params else 0, 
                       color='r', linestyle='--', label='Average slope')
            ax2.set_xlabel('Time (ps)', fontsize=12)
            ax2.set_ylabel('dMSD/dt (Å²/ps)', fontsize=12)
            ax2.set_title('MSD Time Derivative', fontsize=14)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_file, dpi=300)
        print(f"\nPlot saved as: {save_file}")
        plt.show()

# Usage example
if __name__ == "__main__":
    # Analyze MSD
    msd_analyzer = CoalMSDAnalyzer('step10_msd_data.txt', timestep=1.0, units='real')
    
    # Calculate diffusion coefficient
    D_params = msd_analyzer.calculate_diffusion_coefficient(start_frac=0.3)
    
    # Validate stability
    msd_analyzer.validate_coal_stability(D_params[1])
    
    # Plot results
    msd_analyzer.plot_msd(D_params, save_file='coal_msd_validation.png')
