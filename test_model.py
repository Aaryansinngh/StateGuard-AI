def predict(income, credit_score, age):
    if age < 25:
        return "rejected"
    if income > 40000 and credit_score > 650:
        return "approved"
    return "rejected"