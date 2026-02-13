# verifier/explorer.py

from model.ai_model import LoanModel
from verifier.state_space import generate_states
from verifier.property_checker import check_property

def explore():

    model = LoanModel()
    violations = []

    for state in generate_states():

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

    return violations
