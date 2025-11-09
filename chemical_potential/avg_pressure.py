import numpy as np
import pandas as pd

# Read pressure data (skip comments)
data = pd.read_csv("pressure_avg.txt", sep=r"\s+", comment="#", names=["TimeStep", "Pressure"])

# Calculate and print mean pressure
mean_pressure = np.mean(data["Pressure"])
print(f"Average Pressure: {mean_pressure} ")