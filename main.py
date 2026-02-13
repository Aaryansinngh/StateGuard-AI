# main.py

import json
from verifier.explorer import explore

def main():

    print("Starting AI Model Verification...")
    print("-----------------------------------")

    violations = explore()

    if violations:
        print("Property Violations Found!")
        print(f"Total Violations: {len(violations)}")

        with open("results/counterexamples.json", "w") as f:
            json.dump(violations, f, indent=4)

        print("Counterexamples saved to results/counterexamples.json")

    else:
        print("Model Verified Successfully. No Violations Found.")

if __name__ == "__main__":
    main()
