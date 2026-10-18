"""Household Appliance Fault Diagnosis - knowledge-based agent (command-line)."""
from engine import load_kb, forward_chain, backward_chain


def yes_no(text):
    while True:
        a = input(text + " (y/n): ").strip().lower()
        if a in ("y", "n"):
            return a == "y"
        print("Please type y or n.")


def choose(title, options):
    """Show a numbered menu and return the chosen index."""
    print(title)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    while True:
        s = input("Number: ").strip()
        if s.isdigit() and 1 <= int(s) <= len(options):
            return int(s) - 1
        print("Please type a number from the list.")


def run_forward(kb, appliance):
    print(f"\n--- Forward chaining: answer the {appliance} questions, then I reason ---")
    asked = kb["appliances"][appliance]["questions"]
    facts = {f for f in asked if yes_no(kb["questions"][f])}
    all_facts, fired, checks = forward_chain(kb["rules"], facts)

    results = [f for f in all_facts if f in kb["descriptions"]]
    if not results:
        print("\nNo diagnosis found. The knowledge base has no rule for this case.")
        return
    print("\nConclusions:")
    for f in sorted(results):
        print("  *", kb["descriptions"][f])
    print("\nWhy (rules that fired):")
    by_id = {r["id"]: r for r in kb["rules"]}
    for rid in fired:
        r = by_id[rid]
        print(f"  {rid}: IF {' AND '.join(r['if'])} THEN {r['then']}")
    print(f"\nQuestions asked: {len(asked)} | Rules fired: {len(fired)} | Rule checks: {checks}")


def run_backward(kb, appliance):
    print(f"\n--- Backward chaining: pick a {appliance} problem, I check only what I need ---")
    goals = kb["appliances"][appliance]["diagnoses"]
    pick = choose("Which problem do you want to check?",
                  [kb["descriptions"][g] for g in goals])
    goal = goals[pick]

    facts, asked = set(), {}

    def ask(fact):
        if fact not in kb["questions"]:
            return False                 # derived facts are never asked
        if fact not in asked:
            asked[fact] = yes_no(kb["questions"][fact])
        return asked[fact]

    ok, stats = backward_chain(goal, kb["rules"], facts, ask)
    if ok:
        print("\nYes - likely:", kb["descriptions"][goal])
        print("Rules used:", ", ".join(stats["fired"]))
    else:
        print("\nThat problem is NOT supported by your answers.")
    print(f"Questions asked: {len(asked)} | Goal checks: {stats['checks']}")


def main():
    kb = load_kb("kb.json")
    print("=== Household Appliance Fault Diagnosis Agent ===")
    names = list(kb["appliances"])
    appliance = names[choose("\nWhich appliance has the problem?", names)]
    mode = choose("\nWhich reasoning method?",
                  ["Forward chaining", "Backward chaining"])
    if mode == 0:
        run_forward(kb, appliance)
    else:
        run_backward(kb, appliance)


if __name__ == "__main__":
    main()
