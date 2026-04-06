# StateGuard-AI 🚀

**Formal Verification Framework for AI Models using State-Space Exploration**

---

## 🔍 Overview

StateGuard-AI is a modular AI verification framework designed to validate decision-making systems using **formal verification techniques**.

Unlike traditional evaluation methods that rely only on accuracy metrics, this system models AI behavior as a **deterministic function over a bounded input domain** and performs **exhaustive state-space exploration** to verify correctness, safety, and fairness properties.

---

## 🎯 Key Objectives

* Verify **logical correctness** of AI models
* Detect **unsafe or inconsistent behavior**
* Generate **counterexamples for debugging**
* Evaluate **fairness and bias across inputs**

---

## ⚙️ Core Features

* ✅ Exhaustive state-space exploration
* ✅ Formal safety property verification
* ✅ Multi-property validation framework
* ✅ Counterexample generation
* ✅ Fairness & bias analysis (age-based)
* ✅ Support for:

  * Rule-based models
  * Python models (`predict()` function)
  * Scikit-learn models (`.pkl`)

---

## 🧠 System Architecture

```
Input Model
     ↓
State Space Generator
     ↓
Model Execution Engine
     ↓
Property Checker
     ↓
Violation Detector
     ↓
Counterexample Generator
     ↓
Results & Fairness Analysis
```

---

## 🔬 Methodology

1. Define AI model as a function:
   → `f(income, credit_score, age) → decision`

2. Generate all possible states within a bounded domain

3. Execute model on each state

4. Verify predefined **formal properties**, such as:

   * High income applicants should not be rejected
   * Minimum age constraints
   * Credit-score consistency

5. Store violations as **counterexamples**

6. Compute fairness metrics (e.g., **bias score**)

---

## 📊 Example Output

```json
{
  "total_states_checked": 1000,
  "violations": 42,
  "bias_score": 0.23,
  "counterexamples": [
    {
      "state": {"income": 80000, "credit_score": 760, "age": 25},
      "output": "rejected",
      "violated_properties": ["property_high_income_should_not_be_rejected"]
    }
  ]
}
```

---

## 📈 Why This Matters

Traditional ML testing checks performance on datasets.
StateGuard-AI goes further by providing:

* 🔒 **Formal guarantees within bounded domains**
* ⚠️ **Detection of hidden unsafe behaviors**
* 🧾 **Explainable counterexamples**
* ⚖️ **Fairness verification**

---

## 🛠️ Tech Stack

* Python
* FastAPI
* Scikit-learn
* Joblib
* Jinja2
* State-space exploration techniques

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run verification

```bash
python main.py
```

### 3. Run web interface

```bash
uvicorn app:app --reload
```

---

