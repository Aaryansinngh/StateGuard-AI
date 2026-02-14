def predict(income, credit_score, age):
    if income > 70000 and credit_score > 750:
        return "approved"
    return "rejected"
