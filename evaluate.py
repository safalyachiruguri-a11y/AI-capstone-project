"""Run test cases and compare forward vs backward chaining (for the Results section)."""
import time
from engine import load_kb, forward_chain, backward_chain

kb = load_kb("kb.json")
rules = kb["rules"]

# (name, facts the user would answer 'yes' to, expected diagnosis)
TESTS = [
    ("Dead laptop, charger light off", {"no_power", "charger_light_off"}, "power_supply_issue"),
    ("Dead laptop, charger light on",  {"no_power", "charger_light_on"}, "battery_fault"),
    ("Black screen, monitor works",    {"screen_black_power_on", "external_monitor_works"}, "display_panel_fault"),
    ("Black screen, monitor black",    {"screen_black_power_on", "external_monitor_also_black"}, "graphics_or_motherboard_fault"),
    ("Slow, disk 100%",                {"slow_performance", "disk_usage_high"}, "storage_bottleneck"),
    ("Slow, RAM full",                 {"slow_performance", "ram_usage_high"}, "memory_shortage"),
    ("Slow, hot and loud",             {"slow_performance", "fan_loud_hot"}, "overheating_issue"),
    ("No WiFi, airplane mode",         {"wifi_not_connecting", "airplane_mode_on"}, "wifi_switched_off"),
    ("No WiFi, phone works",           {"wifi_not_connecting", "other_devices_wifi_ok"}, "wifi_adapter_or_driver_issue"),
    ("No WiFi, phone fails too",       {"wifi_not_connecting", "other_devices_also_fail"}, "router_or_isp_issue"),
    ("Battery old and draining",       {"battery_drains_fast", "battery_old"}, "battery_worn_out"),
    ("No sound, headphones work",      {"no_sound", "headphones_work"}, "speaker_fault"),
    ("No sound, volume muted",         {"no_sound", "muted_or_volume_zero"}, "volume_muted"),
]

print(f"{'Test case':32} {'Fwd ok':7} {'Bwd ok':7} {'Fwd chk':8} {'Bwd chk':8}")
passed = 0
for name, facts, expected in TESTS:
    t0 = time.perf_counter()
    all_facts, fired, f_checks = forward_chain(rules, facts)
    t_f = time.perf_counter() - t0

    t0 = time.perf_counter()
    ok_b, stats = backward_chain(expected, rules, set(facts))
    t_b = time.perf_counter() - t0

    ok_f = expected in all_facts
    passed += ok_f and ok_b
    print(f"{name:32} {str(ok_f):7} {str(ok_b):7} {f_checks:<8} {stats['checks']:<8}")

print(f"\nPassed {passed}/{len(TESTS)} test cases")
