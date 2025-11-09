import math

def mu_ch4(P):
    """
    Calculate the chemical potential (mu) for CH4 given pressure P.
    
    Equation:
        mu = -9.074 + 0.534 * ln(P) + 0.001 * P
    """
    if P <= 0:
        raise ValueError("Pressure P must be greater than zero.")
    
    mu = -9.074 + 0.534 * math.log(P) + 0.001 * P
    return mu

# Example usage:
if __name__ == "__main__":
    P = float(input("Enter pressure P: "))
    mu_value = mu_ch4(P)
    print(f"μ_CH4 = {mu_value:.5f}")
