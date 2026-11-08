"""Konstanten für ThermoCore."""

DOMAIN = "thermocore"
API_VERSION = 1  # Schnittstelle für gekoppelte Integrationen (z. B. spätere Klima-Integration)

SUBENTRY_PUMP = "pump"
SUBENTRY_ROOM = "room"

# Hub (global)
CONF_TARGET_TEMP = "target_temp"
CONF_HYSTERESIS = "hysteresis"
CONF_OBSERVE_ONLY = "observe_only"

# Pumpe
CONF_PUMP_SWITCH = "pump_switch"
CONF_PUMP_LEAD = "lead_time"  # Sekunden: Ventile öffnen, bevor Pumpe startet
CONF_PUMP_FOLLOW = "follow_time"  # Sekunden: Nachlauf nach letztem Bedarf

# Raum
CONF_AREA = "area_id"
CONF_ROOM_TYPE = "room_type"
CONF_TEMP_SENSOR = "temp_sensor"
CONF_HEAT_SWITCH = "heat_switch"
CONF_PUMP = "pump_subentry_id"
CONF_OVERRIDE_TARGET = "override_target"
CONF_OVERRIDE_HYST = "override_hysteresis"
CONF_LINKED_CLIMATE = "linked_climate"  # Kopplung an externe Klima-Integration

# Fußbodenheizung und Heizkörper verhalten sich gleich (träge, Relais + Hysterese) -> ein Typ.
ROOM_TYPE_HEATING = "heating"
ROOM_TYPE_AC = "ac"  # geplant: schneller, braucht Mindestlauf/-pause, Bewegung + Mindesttemp
ROOM_TYPES = [ROOM_TYPE_HEATING, ROOM_TYPE_AC]

# Betriebsart (Karte 1)
CONF_OPERATING_MODE = "operating_mode"
MODE_WINTER = "winter"  # Regelung aktiv
MODE_SUMMER = "summer"  # Regelung aus, Anti-Blockierlauf
MODE_MANUAL = "manual"  # Handbetrieb, ThermoCore schaltet nicht
OPERATING_MODES = [MODE_WINTER, MODE_SUMMER, MODE_MANUAL]

DEFAULT_TARGET_TEMP = 21.0
DEFAULT_HYSTERESIS = 0.2
DEFAULT_PUMP_LEAD = 180
DEFAULT_PUMP_FOLLOW = 60

EVENT_ROOM_DEMAND = f"{DOMAIN}_room_demand"
