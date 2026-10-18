"""Run test cases for the appliance knowledge base."""
from engine import load_kb, forward_chain, backward_chain

kb = load_kb("kb.json")
rules = kb["rules"]
all_diagnoses = [d for a in kb["appliances"].values() for d in a["diagnoses"]]

# (name, facts the user answers 'yes' to, expected diagnosis or None)
TESTS = [
    ("Fridge: dusty coils",      {"fridge_not_cooling", "fridge_compressor_running", "condenser_coils_dusty"}, "condenser_coils_dirty"),
    ("Fridge: light off",        {"fridge_not_cooling", "fridge_light_off"}, "fridge_no_power"),
    ("Fridge: door seal",        {"fridge_not_cooling", "door_gap_or_frost"}, "door_seal_faulty"),
    ("Washer: dirty filter",     {"ws_water_not_draining", "drain_filter_dirty"}, "drain_filter_clogged"),
    ("Washer: door latch",       {"ws_wont_start", "door_not_latching"}, "door_lock_issue"),
    ("Washer: overloaded",       {"ws_not_spinning", "ws_overloaded"}, "washer_overloaded"),
    ("Microwave: no heating",    {"mw_not_heating", "mw_display_works"}, "heating_circuit_fault"),
    ("Microwave: dead",          {"mw_no_display", "socket_ok"}, "mw_fuse_or_board_fault"),
    ("Microwave: turntable",     {"turntable_not_rotating", "turntable_ring_dirty_or_missing"}, "turntable_support_issue"),
    ("Fan: slow and humming",    {"fan_slow_or_not_starting", "fan_humming"}, "fan_capacitor_weak"),
    ("Fan: regulator no effect", {"fan_slow_or_not_starting", "regulator_no_effect"}, "fan_regulator_fault"),
    ("Fan: noisy and wobbling",  {"fan_noisy", "fan_wobbling"}, "fan_blades_unbalanced"),
    ("AC: dirty filter",         {"ac_poor_cooling", "ac_filter_dirty"}, "ac_filter_clogged"),
    ("AC: ice on pipes",         {"ac_poor_cooling", "ac_ice_on_pipes"}, "ac_low_refrigerant"),
    ("AC: remote batteries",     {"ac_not_responding_remote", "remote_battery_weak"}, "ac_remote_battery_issue"),
    ("TV: no standby light",     {"tv_no_standby_light", "socket_ok"}, "tv_power_supply_fault"),
    ("TV: black, sound works",   {"tv_screen_black", "tv_has_sound"}, "tv_display_or_backlight_fault"),
    ("TV: remote not working",   {"tv_not_responding_remote", "tv_panel_buttons_work"}, "tv_remote_fault"),
    # Cases where NO diagnosis is the correct answer
    ("No symptoms at all",       set(), None),
    ("Fridge: only 'not cooling'", {"fridge_not_cooling"}, None),
    ("TV dead, socket dead too", {"tv_no_standby_light"}, None),
]

print(f"{'Test case':28} {'Fwd ok':7} {'Bwd ok':7} {'Fwd chk':8} {'Bwd chk':8}")
passed = 0
for name, facts, expected in TESTS:
    all_facts, fired, f_checks = forward_chain(rules, facts)
    if expected is None:
        ok_f = not any(d in all_facts for d in all_diagnoses)
        ok_b, b_checks = "n/a", "-"
    else:
        ok_f = expected in all_facts
        ok_b, stats = backward_chain(expected, rules, set(facts))
        b_checks = stats["checks"]
    passed += bool(ok_f) and ok_b in (True, "n/a")
    print(f"{name:28} {str(ok_f):7} {str(ok_b):7} {f_checks:<8} {b_checks:<8}")

print(f"\nPassed {passed}/{len(TESTS)} test cases")
