def mu_from_P(P):
    """Calculate chemical potential (μ) given pressure (P) in bar."""
    mu = (-8.87674 - 0.39316 * P) / (1 + 0.06257 * P + 0.00002 * P**2)
    return mu

if __name__ == "__main__":
    P_input = float(input("Enter the pressure (bar): "))
    mu_result = mu_from_P(P_input)
    print(f"Chemical potential (μ): {mu_result:.5f} kcal/mol")
