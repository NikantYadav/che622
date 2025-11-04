#!/usr/bin/env python3
"""Compute average pressure from a LAMMPS-style thermo data file.

Usage:
	python3 script.py [path/to/step10_thermo_data.txt]

If no path is given, the script will look for
`step10_thermo_data.txt` in the same directory as this script.
"""
import argparse
import os
import sys
from statistics import mean


def parse_pressures(path):
	pressures = []
	with open(path, "r") as fh:
		for line in fh:
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			parts = line.split()
			# Expecting columns: TimeStep c_thermo_temp c_thermo_press v_density v_vol
			if len(parts) < 3:
				continue
			try:
				p = float(parts[2])
				print(f"Parsed pressure: {p}")
			except ValueError:
				# skip lines that don't parse
				continue
			pressures.append(p)
	return pressures


def main():
	default_path = os.path.join(os.path.dirname(__file__), "step10_thermo_data.txt")
	parser = argparse.ArgumentParser(description="Average pressure from thermo data file")
	parser.add_argument("file", nargs="?", default=default_path,
						help="Path to thermo data file (default: %(default)s)")
	args = parser.parse_args()

	if not os.path.isfile(args.file):
		print(f"File not found: {args.file}", file=sys.stderr)
		sys.exit(2)

	pressures = parse_pressures(args.file)
	if not pressures:
		print("No pressure values found in file.")
		sys.exit(1)

	avg = mean(pressures)
	print(f"Count: {len(pressures)}")
	print(f"Average pressure: {avg:.6f}")


if __name__ == "__main__":
	main()

