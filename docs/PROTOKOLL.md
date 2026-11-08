# ThermoCore – Entwicklungsprotokoll / Übergabe

Stand: 2026-11-08 · Repo: github.com/itfhunter/ThermoCore (leer, NICHTS gepusht)

## Harte Regeln (vom Nutzer)
- **Nie pushen/releasen ohne ausdrücklichen Release-Befehl von Hunter.** Release erfolgt dann automatisch über `.github/workflows/release.yml` (workflow_dispatch mit Version → Tag + GitHub-Release + ZIP für HACS).
- **Keine echten Werte/Entity-IDs/Raumnamen ins Repo.** Tests und Doku nur mit erfundenen IDs (`switch.example_room_valve` …).
- Installation über HACS (in HA 2026.11 „Marketplace“) → Repo muss öffentlich sein.

## Entscheidungen
| Thema | Entscheidung |
|---|---|
| Name / Domain | ThermoCore / `thermocore` |
| Aufbau | 1 Haupteintrag (Hub) + Untereinträge (Config Subentries): `pump`, `room` |
| Solltemperatur | global, pro Raum überschreibbar |
| Hysterese | global, pro Raum überschreibbar (kein Mindestlauf/-pause – Heizung träge; erst bei Klima nötig) |
| Pumpenvorlauf / -nachlauf | pro Pumpe einstellbar |
| Pumpenzuordnung | Raum → optional eine Pumpe (mehrere Pumpen möglich) |
| Raum-Auswahl | HA-Bereich wählen → Sensoren/Schalter dieses Bereichs werden vorgeschlagen |
| Raumtypen | `floor` (FBH, Relais) jetzt; `radiator`, `ac` später |
| Schaltweg | nur über HA-Entitäten (`switch.turn_on/off`), keine Shelly-API |
| Sicherheit | Sensor/Relais `unavailable` → Raum aus + Repair-Issue |
| Umstieg | Beobachtungsmodus (rechnet, schaltet nicht) parallel zu alten Automationen |

## Kopplung mit späterer Klima-Integration
- ThermoCore bleibt Hub für **Bedarf pro Raum**. Jeder Raum veröffentlicht:
  - Attribute an `climate.thermocore_<raum>`: `heat_demand`, `target`, `current`, `mode`
  - Event `thermocore_room_demand` (room_id, demand, target, current)
  - Dispatcher-Signal `thermocore_room_update_<entry>_<room>` (intern)
- Geplant: Raumtyp `ac` bzw. Feld „Verknüpfte Klima-Entität“ – ThermoCore gibt dann nur Sollwert/Freigabe an eine externe Klima-Integration weiter (Bewegungssensor + Mindesttemp dort oder hier, offen).
- API-Version in `const.py` (`API_VERSION`), damit eine zweite Integration kompatibel prüfen kann.

## Bestehende Anlage (nur Referenz, gehört NICHT ins Repo)
Liegt in HA: 8 Raum-Automationen per Blueprint `claude/heizung.yaml`, min_max-Schwellen, 1 Pumpe, Failsafe alle 5 Min, Anti-Blockierlauf am 1. des Monats (nur außerhalb Heizperiode). Details nur aus HA lesen.

## Status
- [x] Gerüst: manifest, hacs.json, const, __init__, config_flow (Hub + Pumpe + Raum), Übersetzungen de/en
- [x] Release-Workflow (manuell) + Validierungs-Workflow (hassfest, HACS)
- [ ] `climate.py` – Raum-Thermostat mit Hysterese-Regelung
- [ ] `coordinator.py` – Pumpenlogik (Vorlauf/Nachlauf, Bedarf aus zugeordneten Räumen)
- [ ] `binary_sensor.py` – Pumpenbedarf, `switch.py` – Heizperiode/Beobachtungsmodus
- [ ] Repair-Issues bei Ausfall
- [ ] Tests (pytest-homeassistant-custom-component), erfundene IDs
- [ ] Anti-Blockierlauf
- [ ] README mit Screenshots
- [ ] Lokaler Test-Install in HA (per Datei-Kopie, NICHT über GitHub)

## Weitermachen
Code liegt lokal im Klon (lokaler Commit, nicht gepusht) und als Bundle im Claude-Projekt
„HA INTEGRATION Heizungssteuerung“ unter `claude/thermocore/`. Nächster Schritt: `climate.py`.
