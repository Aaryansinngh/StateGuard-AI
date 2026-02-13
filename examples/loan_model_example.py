# examples/loan_model_example.py

from model.ai_model import LoanModel

model = LoanModel()

print("Example Predictions:")
print(model.predict(50000, 780, 30))  # Expected: approved
print(model.predict(25000, 720, 25))  # Expected: rejected
