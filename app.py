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

# ✅ FIXED (important for Render)
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "/tmp/uploaded_models"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request}
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

    # ================= PYTHON MODEL =================
    if model_type == "python":

        if file is None:
            return {"error": "No file uploaded"}

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

        if file is None:
            return {"error": "No file uploaded"}

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        model = joblib.load(file_path)

    # ================= RULE MODEL =================
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
            violations.append({
                "state": state,
                "output": output,
                "violated_properties": violated_props
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
        max_rate = max(approval_rates.values())
        min_rate = min(approval_rates.values())
        bias_score = round(max_rate - min_rate, 3)
    else:
        bias_score = 0

    # ================= RISK SCORE =================
    risk_score = round(len(violations) / len(states), 3) if len(states) > 0 else 0

    # ================= SEVERITY ANALYSIS =================
    severity_count = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0
    }

    for v in violations:
        if "violated_properties" in v:
            for prop in v["violated_properties"]:
                if "age" in prop:
                    severity_count["CRITICAL"] += 1
                elif "income" in prop:
                    severity_count["HIGH"] += 1
                else:
                    severity_count["MEDIUM"] += 1

    # ================= FINAL RESPONSE =================
    return {
        "model_type": model_type,
        "total_states_checked": len(states),

        # Core metrics
        "violations": len(violations),
        "risk_score": risk_score,
        "bias_score": bias_score,

        # Fairness
        "approval_rates_by_age": approval_rates,

        # Advanced analysis
        "severity_breakdown": severity_count,

        # Debugging
        "counterexamples": violations[:20]
    }