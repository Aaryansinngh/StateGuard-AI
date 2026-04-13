from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import importlib.util
import joblib
import os

from verifier.state_space import generate_states
from verifier.property_checker import check_all_properties

app = FastAPI()

templates = Jinja2Templates(directory="./templates")
templates.env.auto_reload = True

UPLOAD_DIR = "/tmp/uploaded_models"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ================= VERIFY MODEL =================
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

    # ===== LOAD MODEL =====
    if model_type == "python":

        if file is None:
            return {"error": "No file uploaded"}

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        spec = importlib.util.spec_from_file_location("uploaded_model", file_path)

        if spec is None or spec.loader is None:
            return {"error": "Invalid Python file uploaded"}

        uploaded_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(uploaded_module)

        if not hasattr(uploaded_module, "predict"):
            return {"error": "Python file must contain predict(income, credit_score, age)"}

        model = uploaded_module

    elif model_type == "sklearn":

        if file is None:
            return {"error": "No file uploaded"}

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        model = joblib.load(file_path)

    elif model_type == "rule":

        if not rule:
            return {"error": "Rule cannot be empty"}

    else:
        return {"error": "Invalid model type"}

    # ================= VERIFICATION LOOP =================
    age_stats = {}

    for state in states:

        income = state["income"]
        credit_score = state["credit_score"]
        age = state["age"]

        # ===== MODEL EXECUTION =====
        if model_type == "rule":
            try:
                output = "approved" if eval(rule) else "rejected"
            except Exception:
                return {"error": "Invalid rule syntax"}

        elif model_type == "python":
            output = model.predict(income, credit_score, age)

        elif model_type == "sklearn":
            prediction = model.predict([[income, credit_score, age]])[0]
            output = "approved" if prediction == 1 else "rejected"

        # ===== PROPERTY CHECK =====
        violated_props = check_all_properties(state, output)

        if violated_props:

            reason = ""

            if state["income"] < 40000:
                reason = "Low income"
            elif state["credit_score"] < 650:
                reason = "Low credit score"
            elif state["age"] < 25:
                reason = "Young age (possible bias)"
            else:
                reason = "Model inconsistency"

            violations.append({
                "state": state,
                "output": output,
                "violated_properties": violated_props,
                "reason": reason
            })

        # ===== FAIRNESS TRACKING =====
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
        approval_rates[str(age)] = stats["approved"] / total if total > 0 else 0

    if approval_rates:
        bias_score = round(max(approval_rates.values()) - min(approval_rates.values()), 3)
    else:
        bias_score = 0

    # ================= RISK =================
    risk_score = round(len(violations) / len(states), 3) if states else 0

    # ================= SEVERITY =================
    severity_count = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0
    }

    for v in violations:
        for prop in v.get("violated_properties", []):
            if "age" in prop:
                severity_count["CRITICAL"] += 1
            elif "income" in prop:
                severity_count["HIGH"] += 1
            else:
                severity_count["MEDIUM"] += 1

    # ================= RESPONSE =================
    return {
        "total_states_checked": len(states),
        "violations": len(violations),
        "risk_score": risk_score,
        "bias_score": bias_score,
        "approval_rates_by_age": approval_rates,
        "severity_breakdown": {
            "critical": severity_count["CRITICAL"],
            "high": severity_count["HIGH"],
            "medium": severity_count["MEDIUM"]
        },
        "counterexamples": violations[:20]
    }