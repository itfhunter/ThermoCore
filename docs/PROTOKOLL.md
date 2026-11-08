# ThermoCore – Entwicklungsprotokoll / Übergabe

Stand: 2026-11-08 (Nachtrag 12:30) · Repo: github.com/itfhunter/ThermoCore (leer, NICHTS gepusht)

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

## Nachtrag 2026-11-08 (Vorgaben Hunter)
- **Sprachen:** alles Englisch + Deutsch (Integration UND Karten). Karten-Texte nach HA-Sprache des Nutzers.
- **Raumtypen:** Fußbodenheizung und Heizkörper verhalten sich gleich (nur andere Hardware) → ein Typ `heating`. Zweiter Typ `ac` (geplant). Umgesetzt in const/config_flow/Übersetzungen.
- **Betriebsart** (global): Winter (regelt) / Sommer (regelt nicht, Anti-Blockierlauf) / Manuell (ThermoCore schaltet nicht). Konstanten angelegt, Entität (select) noch offen.

### Dashboard-Karten (Lovelace, im Integrations-Paket ausgeliefert)
Auslieferung: JS-Datei unter `custom_components/thermocore/frontend/`, von der Integration selbst registriert
(statischer Pfad + `frontend.add_extra_js_url`) → nur EIN HACS-Download, keine separate Plugin-Installation.
Vorlage-Optik: dunkles Kartendesign laut Screenshot von Hunter (blaue Akzente, abgerundete Kacheln).

1. **`thermocore-control-card` – Heizungssteuerung**
   - Rundes Drehrad „Basis-Solltemperatur“ mit −/+ (globaler Sollwert)
   - Hysterese −/+ (global)
   - Schalter „Heizung“ an/aus (globale Freigabe)
   - Betriebsart: Winter / Sommer / Manuell (Handbetrieb)
   - Pumpenstatus: Name, Leistung (W, wenn Leistungssensor vorhanden), Standby/Läuft – bei mehreren Pumpen je Zeile
2. **`thermocore-room-card` – Raumthermostat** (pro Raum)
   - Kopf: Icon, Raumname, Status (Standby/Heizt/Fehler), Ist | Soll
   - Zeile „Soll überschreiben“ Ja/Nein + Wert; Zeile „Hysterese überschreiben“ Ja/Nein + Wert
   - Leiste „Aktiv | Stopp“ (Raum ein-/ausschalten)
   - **Karten-Optionen:** `show_overrides: true/false`, `show_start_stop: true/false`
3. **`thermocore-overview-card` – Gesamtübersicht**
   - Enthält Karte 1 links + automatisch ein Raumthermostat (Karte 2) für JEDEN ThermoCore-Raum im Raster rechts (neue Räume erscheinen ohne Kartenänderung)
   - Optionen `show_overrides` / `show_start_stop` gelten **für alle Räume gemeinsam** (nicht pro Raum)

Dafür benötigte Entitäten pro Raum (noch zu bauen): `climate` (Ist/Soll/Ein-Aus), `switch` Soll-Override, `number` Override-Soll, `switch` Hysterese-Override, `number` Override-Hysterese. Global: `number` Basis-Soll, `number` Hysterese, `switch` Heizung, `select` Betriebsart, `binary_sensor` je Pumpe.

### Icons
Von Hunter geliefert, liegen in `assets/icons/` (PNG): radiator_red/white, minus(_circle_blue), plus(_circle_blue), power_blue/white, pump_grey/yellow, summer, winter, thermometer_blue, manual, home.
Hinweis: Viele sind weiß auf transparent. Für die Karten besser die passenden MDI-Icons nehmen (färben sich mit dem Theme, scharf in jeder Größe):
radiator→`mdi:radiator`, power→`mdi:power`, plus/minus→`mdi:plus-circle-outline`/`mdi:minus-circle-outline`, pump→`mdi:pump` oder `mdi:fan`, summer→`mdi:white-balance-sunny`, winter→`mdi:snowflake`, manual→`mdi:hand-back-right-outline`, thermometer→`mdi:thermometer`, home→`mdi:home-outline`.
Das rote Heizkörper-Icon ist Kandidat fürs Integrations-Logo. Entscheidung PNG vs. MDI: offen, bei Hunter nachfragen.

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
- [x] Raumtypen zusammengelegt (heating/ac), Betriebsarten-Konstanten, Icons abgelegt
- [ ] `climate.py` – Raum-Thermostat mit Hysterese-Regelung
- [ ] Entitäten für Karten: number/switch/select (siehe Abschnitt Karten)
- [ ] Karten 1–3 (`frontend/thermocore-cards.js`), de/en
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
