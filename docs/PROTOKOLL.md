# ThermoCore – Entwicklungsprotokoll / Übergabe

Stand: 2026-11-08 (auf GitHub, Auto-Release aktiv) · Repo: github.com/itfhunter/ThermoCore (leer, NICHTS gepusht)

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

### Entitäts-Schnittstelle der Karten (VERBINDLICH für die Plattformen)
Karten finden alles über `hass.entities` mit `platform == "thermocore"` + `translation_key`; Raum-Entitäten über gleiche `device_id`.
- Hub-Gerät: `number` key `base_target` (min/max/step) · `number` `hysteresis` · `switch` `heating` · `select` `operating_mode` (Optionen `winter|summer|manual`)
- Je Pumpe ein Gerät: `binary_sensor` `pump_running` (Attribut `power` in W optional, aus verknüpftem Leistungssensor)
- Je Raum ein Gerät: `climate` `room` (current_temperature, temperature, hvac_mode `heat|off`, hvac_action `heating|idle|off`) · `switch` `override_target` · `number` `target_override` · `switch` `override_hysteresis` · `number` `hysteresis_override`
- Aktiv/Stopp = `climate.set_hvac_mode` heat/off
- Karten-Konfig: Karte 1 `{theme}` · Karte 2 `{entity, show_overrides, show_start_stop, theme}` · Karte 3 `{show_overrides, show_start_stop, theme}` · `theme`: dark|light|auto · optional `language`: de|en

### Icons
Von Hunter geliefert, liegen in `assets/icons/` (PNG): radiator_red/white, minus(_circle_blue), plus(_circle_blue), power_blue/white, pump_grey/yellow, summer, winter, thermometer_blue, manual, home.
Hinweis: Viele sind weiß auf transparent. Für die Karten besser die passenden MDI-Icons nehmen (färben sich mit dem Theme, scharf in jeder Größe):
radiator→`mdi:radiator`, power→`mdi:power`, plus/minus→`mdi:plus-circle-outline`/`mdi:minus-circle-outline`, pump→`mdi:pump` oder `mdi:fan`, summer→`mdi:white-balance-sunny`, winter→`mdi:snowflake`, manual→`mdi:hand-back-right-outline`, thermometer→`mdi:thermometer`, home→`mdi:home-outline`.
Entscheidung Hunter: SEINE Icons verwenden. Umgesetzt als CSS-Masken (Form aus PNG, Farbe aus Design) → funktionieren dunkel und hell. Rotes Heizkörper-Icon = Kandidat Integrations-Logo.

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
- [x] Regelung gebaut (2026-11-08 nachmittags):
  - `logic.py` Regelkern ohne HA (Hysterese, Pumpen-Vorlauf/Nachlauf) – 7 Unit-Tests
  - `controller.py` verbindet Kern mit HA: lauscht auf Temperatur/Relais/Pumpe, Failsafe alle 5 Min (Soll-Zustände erneut durchsetzen), Ereignis `thermocore_room_demand` (mit `api_version`), Reparaturmeldung wenn Sensor/Relais > 5 Min weg
  - Entitäten exakt nach Karten-Schnittstelle: climate, number, switch, select, binary_sensor (+ `entity.py` Basis, Geräte: Hub / je Raum / je Pumpe)
  - Pumpe: optionaler Leistungssensor (W) im Pumpen-Dialog; bei nur einer Pumpe wird sie im Raum vorbelegt
- [x] Tests in echter HA-Testumgebung (pytest-homeassistant-custom-component, HA 2026.2): **23/23 grün** – Einrichtung inkl. Bereichs-Vorauswahl, Heizen/Stoppen, Hysterese-Band, Overrides, Beobachtungsmodus schaltet nie, Sommer/Manuell, Raum Stopp, Sensor-Ausfall = Ventil zu, Pumpen-Vorlauf, Raum ohne Pumpe, Werte überleben Neustart, Bedarfs-Ereignis
- [x] Karten-Registrierung hängt nicht mehr hart am Frontend (`after_dependencies`), damit Tests/Headless laufen
- [ ] Karten-Editor (UI-Konfiguration statt YAML)
- [ ] Anti-Blockierlauf (Sommer, 1. des Monats – wie bisherige Anlage)
- [ ] README (de/en) mit Screenshots aus der Vorschau
- [ ] Lokaler Test-Install in Hunters HA (Datei-Kopie, NICHT über GitHub), Beobachtungsmodus parallel zu alten Automationen
- [ ] Klima-Typ `ac` (Mindestlauf/-pause, Bewegung, Mindesttemp)

### Verhalten (wichtig für Weiterarbeit)
- Hysterese: Heizen ab Ist < Soll − Hysterese, Stopp ab Ist ≥ Soll, dazwischen bleibt Zustand.
- Heizen nur wenn: Betriebsart Winter UND Heizung an UND Raum aktiv UND Messwert gültig.
- Sommer / Heizung aus: Ventile und Pumpen werden aus­geschaltet. Manuell: ThermoCore schaltet gar nichts. Beobachtungsmodus: rechnet alles, schaltet nichts.
- Soll am Thermostat setzen = Raum-Override einschalten mit diesem Wert.
- Globale Werte/Overrides liegen im HA-Store `.storage/thermocore.<entry_id>`. Ändert man Soll/Hysterese im Konfigurationsdialog, gewinnt der Dialog; sonst der zuletzt per Entität/Karte gesetzte Wert.
- Relais werden über `<domain>.turn_on/off` der jeweiligen Entität geschaltet (nicht nur `switch`).
- Tests: `python -m pytest tests` in venv mit `pytest-homeassistant-custom-component`; Relais dort als `input_boolean` simuliert (ThermoCore lädt selbst die switch-Domäne).

## Veröffentlichung (2026-11-08)
- Release-Befehl von Hunter erhalten → Code auf `main` gepusht (Commit 2f2a7ce). Repo öffentlich.
- GitHub-Prüfungen: hassfest ✅, Tests ✅ (23), HACS ✅ bis auf „Topics“ (nur für HACS-Standardliste nötig, nicht für benutzerdefiniertes Repo).
- **Auto-Release:** Jeder Push auf `main` liest `version` aus `manifest.json`; existiert dazu kein Release, laufen Tests, dann Tag + Release + `thermocore.zip` (HACS lädt diese ZIP).
  → Neue Version = Version im Manifest erhöhen + pushen (nur nach Release-Befehl von Hunter!). Tags müssen NICHT gepusht werden (aus Claude-Sitzung ohnehin per Proxy gesperrt).
- Erste HACS-Installation scheiterte (404 auf `releases/download/main/thermocore.zip`), weil noch kein Release existierte → Grund für Auto-Release.
- Logo: `custom_components/thermocore/brand/icon.png` (+@2x) aus Hunters rotem Heizkörper-Icon.
- Nach Installation in Hunters HA: HA-Playbook (`playbooks/HA/PLAYBOOK.md`) um ThermoCore ergänzen (Regeln in `_REGELN.md`).

## Weitermachen
Code liegt lokal im Klon (lokaler Commit, nicht gepusht) und als Bundle im Claude-Projekt
„HA INTEGRATION Heizungssteuerung“ unter `claude/thermocore/`. Nächster Schritt: lokaler Test-Install in Hunters HA im Beobachtungsmodus, danach Karten-Editor und Anti-Blockierlauf.
