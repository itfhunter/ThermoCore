"""Regelkern von ThermoCore – bewusst ohne Home-Assistant-Abhängigkeit, damit er einzeln testbar ist.

Hysterese-Modell (wie die bisherige Anlage):
  - Heizen beginnt, wenn Ist  <  Soll − Hysterese
  - Heizen endet,   wenn Ist >=  Soll
  - dazwischen bleibt der letzte Zustand (kein Flattern)
"""

from __future__ import annotations

from dataclasses import dataclass


def effective(base: float, override_on: bool, override_value: float | None) -> float:
    """Globaler Wert, außer der Raum überschreibt ihn."""
    if override_on and override_value is not None:
        return override_value
    return base


def room_demand(current: float | None, target: float, hysteresis: float, previous: bool) -> bool:
    """Braucht der Raum Wärme? Ohne gültigen Messwert: nein (sicherer Zustand)."""
    if current is None:
        return False
    if current < target - hysteresis:
        return True
    if current >= target:
        return False
    return previous


@dataclass
class PumpState:
    """Merkt sich, seit wann Bedarf besteht bzw. weggefallen ist."""

    on: bool = False
    demand_since: float | None = None
    idle_since: float | None = None


def pump_step(st: PumpState, now: float, demand: bool, lead: float, follow: float) -> bool:
    """Pumpe mit Vorlauf (Ventile öffnen zuerst) und Nachlauf. Gibt den Soll-Zustand zurück."""
    if demand:
        st.idle_since = None
        if st.demand_since is None:
            st.demand_since = now
        if st.on or now - st.demand_since >= lead:
            st.on = True
    else:
        st.demand_since = None
        if st.on:
            if st.idle_since is None:
                st.idle_since = now
            if now - st.idle_since >= follow:
                st.on = False
                st.idle_since = None
    return st.on


def pump_next_wakeup(st: PumpState, now: float, lead: float, follow: float) -> float | None:
    """Sekunden bis zur nächsten fälligen Pumpen-Entscheidung (None = nichts geplant)."""
    if st.demand_since is not None and not st.on:
        return max(0.0, st.demand_since + lead - now)
    if st.idle_since is not None and st.on:
        return max(0.0, st.idle_since + follow - now)
    return None
