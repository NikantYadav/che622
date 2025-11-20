#!/usr/bin/env python3
"""Plot timestep vs v_density from step10_thermo_data.txt

Creates `step10_thermo_plot.png` next to the data file.
"""
import sys
from pathlib import Path

DATA_PATH = Path(__file__).with_name('step10_thermo_data.txt')
OUT_PATH = Path(__file__).with_name('step10_thermo_plot.png')


def read_data(path):
    try:
        import pandas as pd
        df = pd.read_csv(path, comment='#', delim_whitespace=True, header=None)
        # file header comment shows column names: TimeStep c_thermo_temp c_thermo_press v_density v_vol
        df.columns = ['timestep', 'temp', 'bs', 'v_density', 'v_vol']
        return df
    except Exception:
        # fallback to numpy/text parsing
        import numpy as np
        data = []
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) < 4:
                    continue
                # we only need timestep and v_density (index 0 and 3)
                data.append([float(parts[0]), float(parts[3])])
        arr = np.array(data)
        return {
            'timestep': arr[:, 0],
            'v_density': arr[:, 1],
        }


def plot(df, out_path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # handle pandas DataFrame or dict-like from numpy fallback
    if hasattr(df, 'columns'):
        t = df['timestep']
        vd = df['v_density']
    else:
        t = df['timestep']
        vd = df['v_density']

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, vd, color='tab:orange', label='Density')
    ax.set_xlabel('Timestep')
    ax.set_ylabel('Density')
    ax.legend(loc='best')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f'Wrote plot to: {out_path}')


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not path.exists():
        print(f'Error: data file not found: {path}', file=sys.stderr)
        sys.exit(2)
    df = read_data(path)
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_PATH
    plot(df, out)


if __name__ == '__main__':
    main()
