# model/ai_model.py

class LoanModel:

    def predict(self, income, credit_score, age):

        if credit_score > 700 and income > 30000:
            return "approved"

        return "rejected"
