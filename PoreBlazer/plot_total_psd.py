#!/usr/bin/env python3
"""
Simple script to plot `PoreBlazer/Total_psd.txt` as a smooth curve.
Reads the file next to this script (same folder), treats the first column
as y and the second column as x, and writes `total_psd.png` in the same folder.
"""

import os
import sys
import numpy as np

base_dir = os.path.dirname(__file__) or '.'
INPUT = os.path.join(base_dir, 'Total_psd.txt')
OUTPUT = os.path.join(base_dir, 'total_psd.png')


def read_two_columns(path):
    xs = []
    ys = []
    with open(path, 'r') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            parts = s.split()
            if len(parts) < 2:
                continue
            try:
                y = float(parts[0])
                x = float(parts[1])
            except ValueError:
                continue
            xs.append(x)
            ys.append(y)
    return xs, ys


def main():
    if not os.path.isfile(INPUT):
        print(f'Input file not found: {INPUT}', file=sys.stderr)
        sys.exit(1)

    xs, ys = read_two_columns(INPUT)
    if not xs:
        print('No numeric data found in the input file.', file=sys.stderr)
        sys.exit(2)

    try:
        import matplotlib.pyplot as plt
        from scipy.interpolate import make_interp_spline
    except ImportError:
        print('matplotlib and scipy are required; install with: pip install matplotlib scipy', file=sys.stderr)
        sys.exit(3)

    # Convert to numpy arrays
    x_np = np.array(ys)
    y_np = np.array(xs)

    # Create smooth spline interpolation
    x_smooth = np.linspace(x_np.min(), x_np.max(), 500)  # 500 points for smoothness
    spl = make_interp_spline(x_np, y_np, k=3)  # cubic spline
    y_smooth = spl(x_smooth)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(x_smooth, y_smooth, color='blue')
    plt.xlabel('Second column (x)')
    plt.ylabel('First column (y)')
    plt.title(os.path.basename(INPUT))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=200)
    print(f'Saved smooth plot to: {OUTPUT}')


if __name__ == '__main__':
    main()
