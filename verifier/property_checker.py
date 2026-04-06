def property_high_income_should_not_be_rejected(state, output):
    return not (state["income"] > 70000 and output == "rejected")


def property_min_age(state, output):
    return state["age"] >= 18


def property_credit_consistency(state, output):
    if state["credit_score"] > 750:
        return output == "approved"
    return True


def check_all_properties(state, output):
    properties = [
        property_high_income_should_not_be_rejected,
        property_min_age,
        property_credit_consistency
    ]

    violated = []

    for prop in properties:
        if not prop(state, output):
            violated.append(prop.__name__)

    return violated