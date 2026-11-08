"""Tests für den Regelkern (ohne Home Assistant)."""

import importlib.util
import pathlib
import sys

_spec = importlib.util.spec_from_file_location(
    "tc_logic", pathlib.Path(__file__).parent.parent / "custom_components/thermocore/logic.py"
)
logic = importlib.util.module_from_spec(_spec)
sys.modules["tc_logic"] = logic  # nötig für dataclasses
_spec.loader.exec_module(logic)


def test_effective_uses_override_only_when_enabled():
    assert logic.effective(21.0, False, 23.0) == 21.0
    assert logic.effective(21.0, True, 23.0) == 23.0
    assert logic.effective(21.0, True, None) == 21.0


def test_room_demand_hysteresis_band():
    # Soll 21, Hysterese 0,2 -> an unter 20,8, aus ab 21,0
    assert logic.room_demand(20.7, 21.0, 0.2, False) is True
    assert logic.room_demand(20.9, 21.0, 0.2, False) is False  # im Band: bleibt aus
    assert logic.room_demand(20.9, 21.0, 0.2, True) is True  # im Band: bleibt an
    assert logic.room_demand(21.0, 21.0, 0.2, True) is False
    assert logic.room_demand(None, 21.0, 0.2, True) is False  # kein Messwert -> sicher aus


def test_room_demand_no_flapping_on_noise():
    prev = False
    seq = [20.75, 20.85, 20.95, 20.85, 20.99, 21.0, 20.9, 20.85, 20.79]
    out = []
    for t in seq:
        prev = logic.room_demand(t, 21.0, 0.2, prev)
        out.append(prev)
    assert out == [True, True, True, True, True, False, False, False, True]


def test_pump_waits_for_lead_time():
    st = logic.PumpState()
    assert logic.pump_step(st, 0, True, 180, 60) is False
    assert logic.pump_next_wakeup(st, 0, 180, 60) == 180
    assert logic.pump_step(st, 179, True, 180, 60) is False
    assert logic.pump_step(st, 180, True, 180, 60) is True


def test_pump_follow_time_and_short_dip():
    st = logic.PumpState(on=True)
    assert logic.pump_step(st, 0, False, 180, 60) is True  # Nachlauf beginnt
    assert logic.pump_next_wakeup(st, 10, 180, 60) == 50
    assert logic.pump_step(st, 30, True, 180, 60) is True  # Bedarf kommt zurück: kein neuer Vorlauf
    assert logic.pump_step(st, 40, False, 180, 60) is True
    assert logic.pump_step(st, 100, False, 180, 60) is False


def test_pump_demand_gone_before_lead_never_starts():
    st = logic.PumpState()
    logic.pump_step(st, 0, True, 180, 60)
    assert logic.pump_step(st, 100, False, 180, 60) is False
    assert logic.pump_next_wakeup(st, 100, 180, 60) is None


def test_zero_lead_starts_immediately():
    st = logic.PumpState()
    assert logic.pump_step(st, 0, True, 0, 0) is True
    assert logic.pump_step(st, 0, False, 0, 0) is False
