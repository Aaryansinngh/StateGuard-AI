# model/model_factory.py

from model.ai_model import LoanModel


def get_model(model_type: str, rule: str = None):

    if model_type == "loan":
        return LoanModel()

    elif model_type == "rule":
        return rule  # return rule string directly

    else:
        raise ValueError("Unsupported model type")
