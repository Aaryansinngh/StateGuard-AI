# main.py

import json
import os
import joblib

from verifier.state_space import generate_states
from verifier.property_checker import check_all_properties


def run_verification():

    # ✅ Load trained ML model
    model = joblib.load("loan_model.pkl")

    states = list(generate_states())
    violations = []

    # ✅ Fairness tracking
    age_stats = {}

    for state in states:

        income = state["income"]
        credit_score = state["credit_score"]
        age = state["age"]

        # ✅ ML prediction
        prediction = model.predict([[income, credit_score, age]])[0]
        output = "approved" if prediction == 1 else "rejected"

        # ✅ Property verification
        violated_props = check_all_properties(state, output)

        if violated_props:
            violations.append({
                "state": state,
                "output": output,
                "violated_properties": violated_props
            })

        # ✅ Fairness tracking
        if age not in age_stats:
            age_stats[age] = {"approved": 0, "rejected": 0}

        if output == "approved":
            age_stats[age]["approved"] += 1
        else:
            age_stats[age]["rejected"] += 1

    # ✅ Compute fairness (bias score)
    approval_rates = {}

    for age, stats in age_stats.items():
        total = stats["approved"] + stats["rejected"]
        approval_rates[age] = stats["approved"] / total if total > 0 else 0

    max_rate = max(approval_rates.values())
    min_rate = min(approval_rates.values())
    bias_score = round(max_rate - min_rate, 3)

    # ✅ Final result
    result = {
        "status": "completed",
        "total_states_checked": len(states),
        "violations": len(violations),
        "bias_score": bias_score,
        "approval_rates_by_age": approval_rates,
        "counterexamples": violations
    }

    # ✅ Save results
    os.makedirs("results", exist_ok=True)
    with open("results/counterexamples.json", "w") as f:
        json.dump(result, f, indent=4)

    return result


if __name__ == "__main__":
    output = run_verification()
    print(json.dumps(output, indent=4))