# verifier/property_checker.py

def check_property(state, output):
    """
    Safety Property:
    If credit_score > 750,
    decision must be 'approved'
    """

    if state["credit_score"] > 750 and output != "approved":
        return False

    return True
