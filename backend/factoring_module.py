import time

def classical_factor(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 2:
        raise ValueError("The number to factor must be an integer of at least 2.")
    start = time.perf_counter()
    for i in range(2, n):
        if n % i == 0:
            end = time.perf_counter()
            return (i, n//i), end - start
    end = time.perf_counter()
    return None, end - start
