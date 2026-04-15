def exponential_growth(N0, r, steps):
    results = []
    N = N0

    for t in range(steps):
        results.append({"time": t, "population": N})
        N = N + r * N

    return results


def logistic_growth(N0, r, K, steps):
    results = []
    N = N0

    for t in range(steps):
        results.append({"time": t, "population": N})
        N = N + r * N * (1 - N / K)

    return results