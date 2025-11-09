import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------
# Configuration
# -----------------------
INPUT_FILENAME = "cavity_radius.txt"
OUT_PNG = "psd_voronoi.png"
OUT_CSV = "psd_voronoi_hist.csv"
DEFAULT_BINS = 50
RANGE = (0.0, 10.0)
MIN_RADIUS = 1.0  # filter cavities smaller than this

# -----------------------
# Functions
# -----------------------
def load_cavity_radii(path):
    """Load cavity radii from a text file (single column or first column)."""
    data = np.loadtxt(path, comments='#')
    if data.ndim == 1:
        radii = data
    else:
        radii = data[:, 0]
    return np.asarray(radii, dtype=float)

def make_histogram(radii, bins=DEFAULT_BINS, range_=RANGE):
    """Compute histogram counts and bin centers for given radii."""
    counts, edges = np.histogram(radii, bins=bins, range=range_)
    centers = (edges[:-1] + edges[1:]) / 2.0
    return counts, edges, centers

# -----------------------
# Main Script
# -----------------------
def main():
    # Determine input path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_FILENAME)

    if not os.path.exists(input_path):
        raise SystemExit(f"Input file not found: {input_path}")

    # Load data
    radii = load_cavity_radii(input_path)

    # Filter out very small cavities
    pore_radii = radii[radii > MIN_RADIUS]
    if pore_radii.size == 0:
        raise SystemExit(f"No cavities with radius > {MIN_RADIUS} Å found.")

    # Compute histogram
    counts, edges, centers = make_histogram(pore_radii)

    # Save CSV with bin centers and counts
    np.savetxt(
        os.path.join(script_dir, OUT_CSV),
        np.column_stack((centers, counts)),
        header='radius_center,counts',
        delimiter=',',
        fmt=['%.6f', '%d'],
    )

    # -----------------------
    # Plotting
    # -----------------------
    sns.set(style="whitegrid", context="talk", palette="muted")
    width = edges[1] - edges[0]

    plt.figure(figsize=(8, 5))
    plt.bar(
        centers,
        counts,
        width=width,
        align='center',
        edgecolor='k',
        alpha=0.7,
        color='skyblue'
    )

    # Labels and title
    plt.xlabel('Cavity Radius (Å)', fontsize=14)
    plt.ylabel('Counts', fontsize=14)
    plt.title('Pore Size Distribution', fontsize=16)
    plt.xlim(RANGE)

    # Grid
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Annotate mean and median
    mean_radius = pore_radii.mean()
    median_radius = np.median(pore_radii)
    plt.axvline(mean_radius, color='red', linestyle='--', linewidth=2, label=f'Mean = {mean_radius:.2f} Å')
    plt.axvline(median_radius, color='green', linestyle='-.', linewidth=2, label=f'Median = {median_radius:.2f} Å')
    plt.legend(fontsize=12)

    # Save figure
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, OUT_PNG), dpi=300)
    plt.close()

    # -----------------------
    # Print statistics
    # -----------------------
    print(f"Histogram saved: {os.path.join(script_dir, OUT_PNG)}")
    print(f"Bin counts CSV saved: {os.path.join(script_dir, OUT_CSV)}")
    print(f"Number of cavities (> {MIN_RADIUS} Å): {pore_radii.size}")
    print(f"Mean radius: {mean_radius:.4f} Å")
    print(f"Median radius: {median_radius:.4f} Å")
    print(f"Min/Max radius: {pore_radii.min():.4f} / {pore_radii.max():.4f} Å")

# -----------------------
# Run Script
# -----------------------
if __name__ == '__main__':
    main()
