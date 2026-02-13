# verifier/state_space.py

from itertools import product

def generate_states():
    """
    Generates all possible input states for verification.
    """

    incomes = range(20000, 80000, 10000)
    credit_scores = range(650, 851, 50)
    ages = range(18, 61, 10)

    for income, credit_score, age in product(incomes, credit_scores, ages):
        yield {
            "income": income,
            "credit_score": credit_score,
            "age": age
        }
