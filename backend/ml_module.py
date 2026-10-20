import time
import random
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

def classical_ml():
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3)

    model = LogisticRegression(max_iter=200)

    start = time.perf_counter()
    model.fit(X_train, y_train)
    end = time.perf_counter()

    accuracy = model.score(X_test, y_test)
    return accuracy, end - start


def quantum_ml_simulated():
    """
    Simulated quantum ML with overhead delay
    to demonstrate practical limitations.
    """
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3)

    start = time.perf_counter()

    # simulate quantum overhead
    time.sleep(0.3)

    # simulated slightly noisy accuracy
    accuracy = 0.85 + random.uniform(-0.05, 0.05)

    end = time.perf_counter()

    return accuracy, end - start
