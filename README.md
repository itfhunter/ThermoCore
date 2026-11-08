# ThermoCore

**DE** · Raumweise Heizungssteuerung für Home Assistant – Fußbodenheizung und Heizkörper über beliebige Schalt-Relais (z. B. Shelly), mehrere Umwälzpumpen mit Vorlauf/Nachlauf, globale Soll- und Hysteresewerte mit Überschreibung pro Raum. Inklusive drei Dashboard-Karten (dunkel/hell, Deutsch/Englisch).

**EN** · Room-by-room heating control for Home Assistant – underfloor heating and radiators via any relay switch (e.g. Shelly), multiple circulation pumps with lead/follow-up time, global target and hysteresis with per-room overrides. Ships with three dashboard cards (dark/light, German/English).

> Status: 0.1.0 – early release. Start with **observe mode** (calculates, never switches) and compare with your existing setup.

## Installation (HACS)

1. HACS → ⋮ → *Custom repositories* → `https://github.com/itfhunter/ThermoCore`, type **Integration**
2. Install **ThermoCore**, restart Home Assistant
3. *Settings → Devices & services → Add integration → ThermoCore*
4. On the ThermoCore entry: **Add pump** (optional), then **Add room** for each room

## How it regulates / Regelung

- Heat when `current < target − hysteresis`, stop when `current ≥ target`, keep state in between.
- Operating mode:
  - **Winter** – automatic regulation.
  - **Manual** – no temperature regulation; each room is switched by hand (room card status button or the room's *Manual heating* switch). The pump follows: on with lead time, off after follow-up time once no room needs it. Rooms heating when you switch from Winter stay on.
  - **Summer** / **Heating off** – everything is switched off once, then ThermoCore is completely passive (no regulation, no failsafe) so relays can be used freely.
- Pump starts after its lead time (valves open first) and keeps running for its follow-up time.
- Sensor or relay unavailable → valve closed, repair issue after 5 minutes.
- Every 5 minutes the desired states are enforced again (failsafe).

## Dashboard cards

The cards are registered automatically – no separate download.

```yaml
type: custom:thermocore-overview-card   # control + all rooms
show_overrides: true
show_start_stop: true
theme: dark          # dark | light | auto
```

```yaml
type: custom:thermocore-control-card    # base target, hysteresis, heating, mode, pumps
```

```yaml
type: custom:thermocore-room-card       # one room thermostat
entity: climate.example_room
show_overrides: true
show_start_stop: true
```

## For other integrations

Each room fires `thermocore_room_demand` (`room_id`, `name`, `demand`, `target`, `current`, `api_version`) when its heat demand changes, and the room `climate` entity exposes `heat_demand` as attribute.

## License

MIT
