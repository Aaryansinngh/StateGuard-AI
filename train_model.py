from sklearn.tree import DecisionTreeClassifier
import joblib

X = [
    [50000, 700, 30],
    [20000, 500, 22],
    [80000, 750, 45],
    [30000, 600, 25]
]

y = [1, 0, 1, 0]  # 1=approved, 0=rejected

model = DecisionTreeClassifier()
model.fit(X, y)

joblib.dump(model, "loan_model.pkl")
