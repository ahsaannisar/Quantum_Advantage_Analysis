import time

def classical_factor(n):
    start = time.time()
    for i in range(2, n):
        if n % i == 0:
            end = time.time()
            return (i, n//i), end - start
    end = time.time()
    return None, end - start
