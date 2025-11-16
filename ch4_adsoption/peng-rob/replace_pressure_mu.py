import re

def replace_pressure_mu(lmp_content, new_pressure, new_mu):
    # Replace pressure values
    lmp_content = re.sub(r'(pressure\s+equal\s+)\d+\.?\d*', f'pressure equal {new_pressure}', lmp_content)
    lmp_content = re.sub(r'(mu\s+equal\s+)-?\d+\.?\d*', f'mu equal {new_mu}', lmp_content)
    lmp_content = re.sub(r'(Pressure:\s+)\d+\.?\d*(\s+bar)', f'Pressure: {new_pressure}\\2', lmp_content)
    lmp_content = re.sub(r'(Chemical Potential:\s+)-?\d+\.?\d*(\s+kcal/mol)', f'Chemical Potential: {new_mu}\\2', lmp_content)
    lmp_content = re.sub(r'(isotherm_P)\d+\.?\d*(bar\.dat)', f'isotherm_P{new_pressure}\\2', lmp_content)
    lmp_content = re.sub(r'(production_)\d+\.?\d*(bar\.dat)', f'production_{new_pressure}\\2', lmp_content)
    lmp_content = re.sub(r'(P=)\d+\.?\d*(\s+bar)', f'P={new_pressure}\\2', lmp_content)
    
    return lmp_content

def main():
    input_file = "gcmc_P0.5bar.lmp"
    new_pressure = 100.0
    new_mu = 11.557
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    modified_content = replace_pressure_mu(content, new_pressure, new_mu)
    
    output_file = f"gcmc_P{new_pressure}bar.lmp"
    with open(output_file, 'w') as f:
        f.write(modified_content)
    
    print(f"Created {output_file} with pressure={new_pressure} bar and mu={new_mu} kcal/mol")

if __name__ == "__main__":
    main()