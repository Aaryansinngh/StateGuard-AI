from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import importlib.util
import joblib
import os

from verifier.state_space import generate_states
from verifier.property_checker import check_property
from model.ai_model import LoanModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploaded_models"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/verify_model")
async def verify_model(
    request: Request,
    model_type: str = Form(...),
    rule: str = Form(None),
    file: UploadFile = File(None)
):

    violations = []
    states = list(generate_states())

    model = None

    # ================= BUILT-IN MODEL =================
    if model_type == "loan":
        model = LoanModel()

    # ================= PYTHON MODEL =================
    elif model_type == "python":

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        spec = importlib.util.spec_from_file_location("uploaded_model", file_path)
        uploaded_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(uploaded_module)

        if not hasattr(uploaded_module, "predict"):
            return {"error": "Python file must contain predict(income, credit_score, age)"}

        model = uploaded_module

    # ================= SKLEARN MODEL =================
    elif model_type == "sklearn":

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        model = joblib.load(file_path)

    # ================= RULE MODEL =================
    elif model_type == "rule":
        pass

    else:
        return {"error": "Invalid model type"}

    # ================= VERIFICATION LOOP =================

    age_stats = {}

    for state in states:

        income = state["income"]
        credit_score = state["credit_score"]
        age = state["age"]

        # Get output
        if model_type == "loan":
            output = model.predict(income, credit_score, age)

        elif model_type == "rule":
            try:
                output = "approved" if eval(rule) else "rejected"
            except:
                return {"error": "Invalid rule syntax"}

        elif model_type == "python":
            output = model.predict(income, credit_score, age)

        elif model_type == "sklearn":
            prediction = model.predict([[income, credit_score, age]])[0]
            output = "approved" if prediction == 1 else "rejected"

        # Property check
        if not check_property(state, output):
            violations.append({"state": state, "output": output})

        # Fairness tracking
        if age not in age_stats:
            age_stats[age] = {"approved": 0, "rejected": 0}

        if output == "approved":
            age_stats[age]["approved"] += 1
        else:
            age_stats[age]["rejected"] += 1

    # ================= FAIRNESS METRICS =================

    approval_rates = {}

    for age, stats in age_stats.items():
        total = stats["approved"] + stats["rejected"]
        approval_rates[age] = stats["approved"] / total if total > 0 else 0

    max_rate = max(approval_rates.values())
    min_rate = min(approval_rates.values())
    bias_score = round(max_rate - min_rate, 3)

    return {
        "model_type": model_type,
        "total_states_checked": len(states),
        "violations": len(violations),
        "counterexamples": violations,
        "approval_rates_by_age": approval_rates,
        "bias_score": bias_score
    }
