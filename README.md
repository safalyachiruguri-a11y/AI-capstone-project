# Knowledge-Based Fault Diagnosis System for Household Appliances using Propositional Logic

AI Mini-Capstone | Artificial Intelligence (25CS301) | Batch 14 | Topic 3.2 Knowledge-Based Agents

**Team:** CH. Safalya (251FA04E78, Team Lead), B. Jai Sri Santosh (251FA04E35), V. Abhinay (251FA04D38), B. Sandeep Kumar Reddy (251FA04E54)

## What it does

A rule-based knowledge-based agent that diagnoses 18 common faults in 6 household appliances: refrigerator, washing machine, microwave oven, ceiling fan, air conditioner and television. The user answers yes/no questions about symptoms, and the agent returns the likely diagnosis, a fix or safety warning, and the chain of rules that led to it.

## How it works

- **Knowledge representation:** every symptom or diagnosis is a propositional symbol (true or false). Rules are implications, for example `tv_screen_black AND tv_has_sound -> tv_display_or_backlight_fault`.
- **Knowledge base:** `kb.json` holds 32 symptom questions, 18 diagnoses and 38 IF-THEN rules.
- **Inference engine (`engine.py`):**
  - *Forward chaining* starts from the confirmed facts and fires rules until nothing new can be derived.
  - *Backward chaining* starts from one suspected fault and asks only the questions needed to prove it.
- **Safety layer:** risky faults (microwave heating circuit, TV power supply, AC refrigerant and similar) also lead to a "call a qualified technician" warning.

## How to run

Requires Python 3 only. No packages to install.

```
py app.py        # browser interface with a reasoning diagram (opens http://localhost:8000)
py main.py       # command-line version
py evaluate.py   # runs the 21 test cases
py compare.py    # forward vs backward chaining comparison
```

On Mac or Linux use `python3` instead of `py`.

## Files

| File | Purpose |
|---|---|
| `kb.json` | Knowledge base (questions, appliances, diagnoses, descriptions, rules) |
| `engine.py` | Forward and backward chaining |
| `main.py` | Command-line agent |
| `app.py`, `index.html` | Browser interface that draws the reasoning as a diagram |
| `evaluate.py` | 21 test cases (18 diagnoses and 3 cases where no diagnosis is correct) |
| `compare.py` | Compares both reasoning methods over all 18 diagnoses |

## Results

All 21 test cases pass. Averages over the 18 diagnoses:

| Measure | Forward | Backward (problem known) | Backward (problem unknown) |
|---|---|---|---|
| Questions asked | 5.5 | 2.1 | 3.9 |
| Rule or goal checks | 76.0 | 3.1 | 7.6 |

## Limitations

- Knows only the 18 faults written into its rules and cannot learn new ones.
- Yes/no answers only, with no way to say "not sure".
- Rules were written by hand from common troubleshooting knowledge and should be checked against manufacturer guides before real use.

## Acknowledgements

Built with Python 3, Visual Studio Code, Git and GitHub. An AI assistant was used as a learning and development aid; all code was tested and is understood by the author.
