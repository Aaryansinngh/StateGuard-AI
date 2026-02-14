# main.py

from verifier.state_space import generate_states
from verifier.property_checker import check_property
from model.ai_model import LoanModel
import json
import os


def run_verification():

    model = LoanModel()
    states = list(generate_states())
    violations = []

    for state in states:

        output = model.predict(
            state["income"],
            state["credit_score"],
            state["age"]
        )

        if not check_property(state, output):
            violations.append({
                "state": state,
                "output": output
            })

    result = {
        "status": "completed",
        "total_states_checked": len(states),
        "violations": len(violations),
        "counterexamples": violations
    }

    os.makedirs("results", exist_ok=True)
    with open("results/counterexamples.json", "w") as f:
        json.dump(result, f, indent=4)

    return result


if __name__ == "__main__":
    output = run_verification()
    print(json.dumps(output, indent=4))
