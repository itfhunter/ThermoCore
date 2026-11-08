/* ThermoCore Dashboard-Karten (de/en, Design dark/light/auto). Icons werden beim Build eingesetzt (__ICONS__). */
const TC_VERSION = "0.1.3";
const ICONS = __ICONS__;

const I18N = {
  de: {
    control: "Heizungssteuerung", rooms: "Räume", base: "Basis-Solltemperatur", hyst: "Hysterese",
    heating: "Heizung", mode: "Betriebsart", winter: "Winter", summer: "Sommer", manual: "Manuell / Handbetrieb",
    pump: "Pumpe", running: "Läuft", standby: "Standby", heats: "Heizt", stopped: "Gestoppt", error: "Fehler",
    actual: "Ist", target: "Soll", ovTarget: "Soll überschreiben", ovHyst: "Hysterese überschreiben",
    yes: "Ja", no: "Nein", active: "Aktiv", stop: "Stopp", notFound: "ThermoCore nicht gefunden",
    noEntity: "Entität nicht gefunden", observe: "Beobachtungsmodus", manualHint: "Klicken: Raum manuell heizen / stoppen",
  },
  en: {
    control: "Heating control", rooms: "Rooms", base: "Base target temperature", hyst: "Hysteresis",
    heating: "Heating", mode: "Operating mode", winter: "Winter", summer: "Summer", manual: "Manual",
    pump: "Pump", running: "Running", standby: "Standby", heats: "Heating", stopped: "Stopped", error: "Error",
    actual: "Current", target: "Target", ovTarget: "Override target", ovHyst: "Override hysteresis",
    yes: "Yes", no: "No", active: "Active", stop: "Stop", notFound: "ThermoCore not found",
    noEntity: "Entity not found", observe: "Observe mode", manualHint: "Click: heat room manually / stop",
  },
};

const CSS = `
:host{display:block;container-type:inline-size}
:host{--tc-bg:#0f1a26;--tc-card:#15212f;--tc-tile:#1b2a3b;--tc-border:#26384c;--tc-text:#f2f6fa;
 --tc-muted:#9fb0c2;--tc-accent:#13a3ff;--tc-accent-text:#ffffff;--tc-track:#2c3d50;--tc-seg:#24364a;
 --tc-heat:#ff6b3d;--tc-ok:#35c27a;--tc-warn:#f2b73c;--tc-err:#ff5252;--tc-pump:#f6c445}
:host([data-theme=light]){--tc-bg:#eef3f8;--tc-card:#ffffff;--tc-tile:#f5f8fb;--tc-border:#d6e0ea;--tc-text:#14212e;
 --tc-muted:#5c6f82;--tc-accent:#0b8de0;--tc-accent-text:#ffffff;--tc-track:#d9e3ed;--tc-seg:#e6edf4;
 --tc-heat:#e2551f;--tc-ok:#1e9a5a;--tc-warn:#c98a00;--tc-err:#d93636;--tc-pump:#d49b00}
*{box-sizing:border-box}
ha-card,.card{background:var(--tc-card);color:var(--tc-text);border:1px solid var(--tc-border);border-radius:16px;padding:16px;
 font-family:var(--paper-font-body1_-_font-family,system-ui,sans-serif)}
.ic{display:inline-block;width:22px;height:22px;flex:none;background:currentColor;
 -webkit-mask:var(--m) center/contain no-repeat;mask:var(--m) center/contain no-repeat}
.title{display:flex;align-items:center;gap:10px;font-size:22px;font-weight:600;margin:0 0 12px}
.title .ic{width:28px;height:28px;color:var(--tc-text)}
.tile{background:var(--tc-tile);border:1px solid var(--tc-border);border-radius:14px;padding:14px;margin-top:12px}
.row{display:flex;align-items:center;gap:10px}
.lbl{font-size:16px;font-weight:600}
.muted{color:var(--tc-muted)}
.badge{margin-left:auto;font-size:13px;padding:4px 12px;border-radius:999px;background:var(--tc-seg);color:var(--tc-muted);white-space:nowrap}
.badge.heat{background:color-mix(in srgb,var(--tc-heat) 22%,transparent);color:var(--tc-heat)}
.badge.err{background:color-mix(in srgb,var(--tc-err) 22%,transparent);color:var(--tc-err)}
.badge.click{cursor:pointer;display:inline-flex;align-items:center;gap:6px;border:1px solid var(--tc-accent);color:var(--tc-text)}
.badge.click .ic{width:14px;height:14px}
.badge.click.heat{border-color:var(--tc-heat)}
.badge.run{background:color-mix(in srgb,var(--tc-ok) 22%,transparent);color:var(--tc-ok)}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;padding:0}
.rbtn{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;color:var(--tc-accent)}
.rbtn .ic{width:40px;height:40px}
.rbtn:active{transform:scale(.94)}
.val{min-width:90px;text-align:center;border:1px solid var(--tc-border);border-radius:10px;padding:6px 10px;font-size:18px;font-weight:600;background:var(--tc-card)}
input.val{color:var(--tc-text);width:96px;-moz-appearance:textfield}
input.val::-webkit-inner-spin-button{opacity:.4}
.seg{display:flex;background:var(--tc-seg);border-radius:999px;padding:3px;gap:2px}
.seg button{flex:1;padding:7px 12px;border-radius:999px;color:var(--tc-muted);font-size:15px;display:flex;align-items:center;justify-content:center;gap:8px}
.seg button.on{background:var(--tc-accent);color:var(--tc-accent-text)}
.seg.sm button{padding:4px 12px;font-size:14px}
.seg.wide button{padding:9px 12px;font-size:16px}
.toggle{margin-left:auto;width:56px;height:32px;border-radius:999px;background:var(--tc-track);position:relative;transition:background .2s}
.toggle::after{content:"";position:absolute;top:4px;left:4px;width:24px;height:24px;border-radius:50%;background:#fff;transition:left .2s}
.toggle.on{background:var(--tc-accent)}.toggle.on::after{left:28px}
.mbtn{width:100%;margin-top:8px;padding:9px;border:1px solid var(--tc-border);border-radius:12px;display:flex;justify-content:center;gap:10px;align-items:center;font-size:16px;color:var(--tc-text)}
.mbtn.on{background:var(--tc-accent);border-color:var(--tc-accent);color:var(--tc-accent-text)}
.dialwrap{position:relative;display:flex;align-items:center;justify-content:center;gap:4px}
.dial{width:230px;height:230px;touch-action:none;cursor:pointer}
.dial .bg{stroke:var(--tc-track)}.dial .fg{stroke:var(--tc-accent)}
.dial .tick{stroke:var(--tc-muted);opacity:.6}
.dial .knob{fill:var(--tc-accent);stroke:#fff;stroke-width:3}
.dval{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none}
.dval .ic{width:30px;height:46px;color:var(--tc-accent);margin-bottom:4px}
.dval b{font-size:46px;font-weight:700;letter-spacing:-1px}
.pump .ic{width:40px;height:40px;color:var(--tc-muted)}
.pump.on .ic{color:var(--tc-pump);animation:spin 2s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.room-head{display:flex;align-items:center;gap:10px}
.room-head .ic{width:26px;height:26px}
.room-head .name{font-size:20px;font-weight:600}
.temps{display:flex;justify-content:space-around;font-size:17px;padding:4px 0 10px;border-bottom:1px solid var(--tc-border);margin-bottom:8px}
.temps b{font-weight:600}
.ovr{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:6px;align-items:center;padding:4px 0;font-size:14px;line-height:1.25}
.ovr .seg button{padding:4px 10px}
.unit{display:flex;align-items:center;border:1px solid var(--tc-border);border-radius:10px;background:var(--tc-card);padding:0 8px 0 0;font-weight:600}
.unit.dim{opacity:.45}
.unit input{width:52px;border:0;background:none;color:var(--tc-text);font:inherit;font-size:15px;text-align:right;padding:5px 4px;-moz-appearance:textfield}
.unit input::-webkit-inner-spin-button,.unit input::-webkit-outer-spin-button{-webkit-appearance:none;margin:0}
.unit input:focus{outline:none}
.startstop{margin-top:10px}
button.unit{cursor:pointer;padding:5px 8px;font-size:15px;color:var(--tc-text);min-width:70px;justify-content:center}
button.unit.open{border-color:var(--tc-accent);box-shadow:0 0 0 1px var(--tc-accent)}
.sl{background:var(--tc-tile);border:1px solid var(--tc-accent);border-radius:12px;padding:6px 10px 10px;margin:2px 0 8px}
.slh{display:flex;align-items:center;justify-content:center;position:relative;margin-bottom:4px}
.slh .x{position:absolute;right:0}
.slr{display:flex;align-items:center;gap:8px}
.sl .rbtn{width:34px;height:34px}.sl .rbtn .ic{width:34px;height:34px}
.sl b{font-size:24px;font-weight:700}
.sl .x{width:28px;height:28px;border-radius:50%;color:var(--tc-muted);font-size:20px;line-height:1}
.range{flex:1;min-width:60px;-webkit-appearance:none;appearance:none;height:8px;border-radius:999px;outline:none;margin:0;
 background:linear-gradient(to right,var(--tc-accent) 0,var(--tc-accent) var(--p),var(--tc-track) var(--p),var(--tc-track) 100%)}
.range::-webkit-slider-thumb{-webkit-appearance:none;width:24px;height:24px;border-radius:50%;background:var(--tc-accent);border:3px solid #fff;cursor:pointer}
.range::-moz-range-thumb{width:20px;height:20px;border-radius:50%;background:var(--tc-accent);border:3px solid #fff;cursor:pointer}
.selected{border-color:var(--tc-accent);box-shadow:0 0 0 1px var(--tc-accent)}
.overview{display:grid;grid-template-columns:minmax(260px,1fr) 2fr;gap:16px;background:var(--tc-bg);border-radius:18px;padding:16px;color:var(--tc-text)}
.ogrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}
@container (max-width:760px){.overview{grid-template-columns:1fr}}
.warn{color:var(--tc-warn);font-size:13px;margin-top:6px}
`;

const ic = (name) => `<span class="ic" style="--m:url('${ICONS[name]}')"></span>`;
const fmt = (v, d = 1) => (v === undefined || v === null || isNaN(v) ? "–" : Number(v).toFixed(d).replace(".", ","));

class TCBase extends HTMLElement {
  constructor() { super(); this.attachShadow({ mode: "open" }); this._cfg = {}; }
  setConfig(cfg) { this._cfg = { theme: "dark", show_overrides: true, show_start_stop: true, ...cfg }; this._render(); }
  set hass(h) { this._hass = h; this._render(); }
  get t() {
    const lang = (this._cfg.language || this._hass?.locale?.language || this._hass?.language || "en").slice(0, 2);
    return I18N[lang] || I18N.en;
  }
  _theme() {
    let th = this._cfg.theme;
    if (th === "auto") th = this._hass?.themes?.darkMode === false ? "light" : "dark";
    this.setAttribute("data-theme", th);
  }
  _st(id) { return id ? this._hass?.states?.[id] : undefined; }
  /* Wert setzen; Override wird dabei automatisch eingeschaltet */
  _commit(numId, swId, value) {
    const v = Math.round(parseFloat(String(value).replace(",", ".")) * 10) / 10;
    if (isNaN(v)) return;
    this._call("number", "set_value", { entity_id: numId, value: v });
    if (swId && this._st(swId)?.state !== "on") this._call("homeassistant", "turn_on", { entity_id: swId });
  }
  _call(domain, service, data) { return this._hass.callService(domain, service, data); }
  /* ThermoCore-Entitäten über Registry finden: platform + translation_key */
  _tc() { return Object.values(this._hass?.entities || {}).filter((e) => e.platform === "thermocore"); }
  _byKey(key, deviceId) {
    const e = this._tc().find((x) => x.translation_key === key && (!deviceId || x.device_id === deviceId));
    return e?.entity_id;
  }
  _rooms() {
    return this._tc().filter((e) => e.translation_key === "room" && e.entity_id.startsWith("climate."))
      .map((e) => e.entity_id).sort((a, b) => (this._st(a)?.attributes?.friendly_name || a).localeCompare(this._st(b)?.attributes?.friendly_name || b));
  }
  _bind(root) {
    root.querySelectorAll("input.range").forEach((el) => {
      const lbl = el.closest(".sl")?.querySelector(".slv");
      const show = () => {
        const p = ((el.value - el.min) / (el.max - el.min)) * 100;
        el.style.setProperty("--p", `${p}%`); if (lbl) lbl.textContent = `${fmt(el.value)} °C`;
      };
      el.addEventListener("pointerdown", () => { this._dragging = true; });
      el.addEventListener("input", (e) => { e.stopPropagation(); this._dragging = true; show(); });
      el.addEventListener("change", (e) => { e.stopPropagation(); this._dragging = false; this._commit(el.dataset.id, el.dataset.sw, el.value); });
    });
    root.querySelectorAll("[data-act]").forEach((el) => {
      const ev = el.tagName === "INPUT" ? "change" : "click";
      el.addEventListener(ev, (e) => { e.stopPropagation(); this._act(el.dataset.act, el.dataset.id, el, e); });
    });
  }
  _act(act, id, el) {
    const st = this._st(id);
    switch (act) {
      case "toggle": return this._call("homeassistant", st?.state === "on" ? "turn_off" : "turn_on", { entity_id: id });
      case "on": return st?.state !== "on" && this._call("homeassistant", "turn_on", { entity_id: id });
      case "off": return st?.state !== "off" && this._call("homeassistant", "turn_off", { entity_id: id });
      case "step": {
        const a = st?.attributes || {}; const step = Number(a.step || 0.1) * Number(el.dataset.dir);
        const v = Math.min(Number(a.max ?? 99), Math.max(Number(a.min ?? -99), Math.round((Number(st.state) + step) * 100) / 100));
        return this._call("number", "set_value", { entity_id: id, value: v });
      }
      case "set": { const v = parseFloat(String(el.value).replace(",", ".")); if (!isNaN(v)) this._call("number", "set_value", { entity_id: id, value: v }); return; }
      case "slider": this._open = this._open === id ? null : id; this._dragging = false; return this._render();
      case "sstep": {
        const r = el.closest(".sl").querySelector("input.range");
        const v = Math.min(+r.max, Math.max(+r.min, Math.round((+r.value + Number(r.step) * Number(el.dataset.dir)) * 10) / 10));
        r.value = v; r.dispatchEvent(new Event("input")); return this._commit(id, el.dataset.sw, v);
      }
      case "mode": return this._call("select", "select_option", { entity_id: id, option: el.dataset.opt });
      case "hvac": return this._call("climate", "set_hvac_mode", { entity_id: id, hvac_mode: el.dataset.opt });
    }
  }
}

/* ---------- Karte 1: Heizungssteuerung ---------- */
class ThermoCoreControlCard extends TCBase {
  static getStubConfig() { return { theme: "dark" }; }
  getCardSize() { return 8; }
  _render() {
    if (!this._hass) return;
    this._theme();
    if (this._dragging) return;
    this.shadowRoot.innerHTML = `<style>${CSS}</style><ha-card>${this.body()}</ha-card>`;
    this._bind(this.shadowRoot); this._bindDial();
  }
  body() {
    const t = this.t;
    const base = this._byKey("base_target"), hyst = this._byKey("hysteresis"), heat = this._byKey("heating"), mode = this._byKey("operating_mode");
    if (!base) return `<div class="title">${ic("radiator")}${t.control}</div><div class="muted">${t.notFound}</div>`;
    const bs = this._st(base), hs = this._st(hyst), mo = this._st(mode)?.state, on = this._st(heat)?.state === "on";
    const a = bs?.attributes || {}, min = Number(a.min ?? 15), max = Number(a.max ?? 28), v = Number(bs?.state);
    const frac = Math.max(0, Math.min(1, (v - min) / (max - min)));
    const R = 95, C = 115, sweep = 270, start = 135, ang = start + sweep * frac;
    const pt = (deg, r = R) => [C + r * Math.cos((deg * Math.PI) / 180), C + r * Math.sin((deg * Math.PI) / 180)];
    const arc = (a0, a1) => { const [x0, y0] = pt(a0), [x1, y1] = pt(a1); return `M${x0} ${y0} A${R} ${R} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1} ${y1}`; };
    const ticks = Array.from({ length: 7 }, (_, i) => { const d = start + (sweep / 6) * i, [x0, y0] = pt(d, R + 14), [x1, y1] = pt(d, R + 22); return `<line class="tick" x1="${x0}" y1="${y0}" x2="${x1}" y2="${y1}" stroke-width="2" stroke-linecap="round"/>`; }).join("");
    const [kx, ky] = pt(ang);
    const pumps = this._tc().filter((e) => e.translation_key === "pump_running");
    return `
      <div class="title">${ic("radiator")}${t.control}</div>
      <div class="tile">
        <div class="lbl" style="text-align:center;font-size:20px">${t.base}</div>
        <div class="dialwrap">
          <button class="rbtn" data-act="step" data-dir="-1" data-id="${base}" aria-label="-">${ic("minus_circle")}</button>
          <div style="position:relative">
            <svg class="dial" viewBox="0 0 230 230" data-min="${min}" data-max="${max}" data-step="${a.step || 0.1}">
              ${ticks}
              <path class="bg" d="${arc(start, start + sweep)}" fill="none" stroke-width="14" stroke-linecap="round"/>
              ${frac > 0.001 ? `<path class="fg" d="${arc(start, ang)}" fill="none" stroke-width="14" stroke-linecap="round"/>` : ""}
              <circle class="knob" cx="${kx}" cy="${ky}" r="12"/>
            </svg>
            <div class="dval">${ic("thermometer")}<b>${fmt(v)} °C</b></div>
          </div>
          <button class="rbtn" data-act="step" data-dir="1" data-id="${base}" aria-label="+">${ic("plus_circle")}</button>
        </div>
      </div>
      <div class="tile row"><span class="lbl">${t.hyst}</span>
        <span style="margin-left:auto" class="row">
          <button class="rbtn" data-act="step" data-dir="-1" data-id="${hyst}">${ic("minus_circle")}</button>
          <span class="val">${fmt(hs?.state)} °C</span>
          <button class="rbtn" data-act="step" data-dir="1" data-id="${hyst}">${ic("plus_circle")}</button>
        </span></div>
      <div class="tile row"><span style="color:var(--tc-accent)">${ic("power")}</span><span class="lbl">${t.heating}</span>
        <button class="toggle ${on ? "on" : ""}" data-act="toggle" data-id="${heat}" aria-label="${t.heating}"></button></div>
      <div class="tile">
        <div class="row" style="margin-bottom:10px">${ic("winter")}<span class="lbl">${t.mode}</span></div>
        <div class="seg wide">
          <button class="${mo === "winter" ? "on" : ""}" data-act="mode" data-opt="winter" data-id="${mode}">${ic("winter")}${t.winter}</button>
          <button class="${mo === "summer" ? "on" : ""}" data-act="mode" data-opt="summer" data-id="${mode}">${ic("summer")}${t.summer}</button>
        </div>
        <button class="mbtn ${mo === "manual" ? "on" : ""}" data-act="mode" data-opt="manual" data-id="${mode}">${ic("manual")}${t.manual}</button>
      </div>
      ${pumps.map((p) => { const s = this._st(p.entity_id), run = s?.state === "on", w = s?.attributes?.power;
        return `<div class="tile row pump ${run ? "on" : ""}">${ic("pump")}<div><div class="lbl">${s?.attributes?.friendly_name || t.pump}</div>
        <div class="muted">${w !== undefined ? `${Math.round(w)} W` : ""}</div></div>
        <span class="badge ${run ? "run" : ""}">${s?.state === "unavailable" ? t.error : run ? t.running : t.standby}</span></div>`; }).join("")}`;
  }
  _bindDial() {
    const svg = this.shadowRoot.querySelector(".dial"); if (!svg) return;
    const id = this._byKey("base_target");
    const calc = (e) => {
      const r = svg.getBoundingClientRect(); const x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2;
      let d = (Math.atan2(y, x) * 180) / Math.PI; d = (d - 135 + 360) % 360; if (d > 270) d = d > 315 ? 0 : 270;
      const min = +svg.dataset.min, max = +svg.dataset.max, step = +svg.dataset.step;
      return Math.round((min + (d / 270) * (max - min)) / step) * step;
    };
    const val = this.shadowRoot.querySelector(".dval b"); let last;
    svg.addEventListener("pointerdown", (e) => { this._dragging = true; svg.setPointerCapture(e.pointerId); last = calc(e); val.textContent = `${fmt(last)} °C`; });
    svg.addEventListener("pointermove", (e) => { if (!this._dragging) return; last = calc(e); val.textContent = `${fmt(last)} °C`; });
    svg.addEventListener("pointerup", () => { this._dragging = false; if (last !== undefined) this._call("number", "set_value", { entity_id: id, value: Number(last.toFixed(2)) }); });
  }
}

/* ---------- Karte 2: Raumthermostat ---------- */
function roomHTML(card, climateId, cfg) {
  const t = card.t, s = card._st(climateId);
  if (!s) return `<div class="card">${t.noEntity}: ${climateId || "–"}</div>`;
  const dev = card._hass.entities?.[climateId]?.device_id;
  const k = (key) => card._byKey(key, dev);
  const a = s.attributes || {}, off = s.state === "off", unav = s.state === "unavailable";
  const status = unav ? ["err", t.error] : off ? ["", t.stopped] : a.hvac_action === "heating" ? ["heat", t.heats] : ["", t.standby];
  /* Handbetrieb: Status-Feld wird zum Knopf (Raum an/aus inkl. Pumpe) */
  const manSw = k("manual_heat"), manSt = card._st(manSw);
  const manual = manSt && manSt.state !== "unavailable" && !off && !unav;
  const badge = manual
    ? `<button class="badge click ${status[0]}" data-act="toggle" data-id="${manSw}" title="${t.manualHint}">${ic("manual")}${status[1]}</button>`
    : `<span class="badge ${status[0]}">${status[1]}</span>`;
  const ovRow = (label, swKey, numKey) => {
    const sw = k(swKey), num = k(numKey), on = card._st(sw)?.state === "on", ns = card._st(num);
    if (!sw || !num) return "";
    return `<div class="ovr"><span>${label}</span>
      <div class="seg sm"><button class="${on ? "on" : ""}" data-act="on" data-id="${sw}">${t.yes}</button><button class="${on ? "" : "on"}" data-act="off" data-id="${sw}">${t.no}</button></div>
      <button class="unit ${on ? "" : "dim"} ${card._open === num ? "open" : ""}" data-act="slider" data-id="${num}">${fmt(ns?.state)} °C</button></div>
      ${card._open === num ? sliderHTML(card, num, sw) : ""}`;
  };
  return `<div class="card ${a.hvac_action === "heating" && !off ? "selected" : ""}">
    <div class="room-head" style="color:${a.hvac_action === "heating" && !off ? "var(--tc-heat)" : "var(--tc-text)"}">${ic("radiator")}
      <span class="name" style="color:var(--tc-text)">${a.friendly_name || climateId}</span>${badge}</div>
    <div class="temps"><span>${t.actual}: <b>${fmt(a.current_temperature)} °C</b></span><span class="muted">|</span><span>${t.target}: <b>${fmt(a.temperature)} °C</b></span></div>
    ${cfg.show_overrides ? ovRow(t.ovTarget, "override_target", "target_override") + ovRow(t.ovHyst, "override_hysteresis", "hysteresis_override") : ""}
    ${cfg.show_start_stop ? `<div class="seg wide startstop"><button class="${off ? "" : "on"}" data-act="hvac" data-opt="heat" data-id="${climateId}">${t.active}</button><button class="${off ? "on" : ""}" data-act="hvac" data-opt="off" data-id="${climateId}">${t.stop}</button></div>` : ""}
  </div>`;
}

function sliderHTML(card, num, sw) {
  const a = card._st(num)?.attributes || {}, min = Number(a.min ?? 5), max = Number(a.max ?? 30), step = Number(a.step || 0.1);
  const v = Number(card._st(num)?.state), p = ((v - min) / (max - min)) * 100;
  return `<div class="sl">
    <div class="slh"><b class="slv">${fmt(v)} °C</b><button class="x" data-act="slider" data-id="${num}" aria-label="close">×</button></div>
    <div class="slr">
      <button class="rbtn" data-act="sstep" data-dir="-1" data-id="${num}" data-sw="${sw}" aria-label="-">${ic("minus_circle")}</button>
      <input class="range" type="range" min="${min}" max="${max}" step="${step}" value="${v}" style="--p:${p}%" data-id="${num}" data-sw="${sw}">
      <button class="rbtn" data-act="sstep" data-dir="1" data-id="${num}" data-sw="${sw}" aria-label="+">${ic("plus_circle")}</button>
    </div></div>`;
}

class ThermoCoreRoomCard extends TCBase {
  static getStubConfig(hass) {
    const e = Object.values(hass?.entities || {}).find((x) => x.platform === "thermocore" && x.translation_key === "room");
    return { entity: e?.entity_id || "", show_overrides: true, show_start_stop: true, theme: "dark" };
  }
  getCardSize() { return 4; }
  _render() {
    if (!this._hass) return;
    this._theme();
    if (this._dragging) return;
    this.shadowRoot.innerHTML = `<style>${CSS}</style>${roomHTML(this, this._cfg.entity, this._cfg)}`;
    this._bind(this.shadowRoot);
  }
}

/* ---------- Karte 3: Gesamtübersicht ---------- */
class ThermoCoreOverviewCard extends TCBase {
  static getStubConfig() { return { show_overrides: true, show_start_stop: true, theme: "dark" }; }
  getCardSize() { return 12; }
  _render() {
    if (!this._hass) return;
    this._theme();
    if (this._dragging) return;
    const t = this.t, ctrl = ThermoCoreControlCard.prototype.body.call(this);
    this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="overview">
      <div>${ctrl}</div>
      <div><div class="title">${ic("home")}${t.rooms}</div><div class="ogrid">${this._rooms().map((r) => roomHTML(this, r, this._cfg)).join("")}</div></div></div>`;
    this._bind(this.shadowRoot); ThermoCoreControlCard.prototype._bindDial.call(this);
  }
}

/* ---------- Visuelle Editoren (ha-form) ---------- */
const ED_I18N = {
  de: { entity: "Raum (ThermoCore-Thermostat)", show_overrides: "Overrides anzeigen (Soll / Hysterese)",
        show_start_stop: "Aktiv / Stopp anzeigen", theme: "Design", language: "Sprache",
        dark: "Dunkel", light: "Hell", auto: "Automatisch (HA-Design)", lang_auto: "Automatisch (HA-Sprache)" },
  en: { entity: "Room (ThermoCore thermostat)", show_overrides: "Show overrides (target / hysteresis)",
        show_start_stop: "Show active / stop", theme: "Theme", language: "Language",
        dark: "Dark", light: "Light", auto: "Automatic (HA theme)", lang_auto: "Automatic (HA language)" },
};

async function ensureHaForm() {
  if (customElements.get("ha-form")) return;
  try { /* lädt ha-form über einen eingebauten Karten-Editor */
    const helpers = await window.loadCardHelpers?.();
    const c = await helpers?.createCardElement({ type: "entities", entities: [] });
    await c?.constructor?.getConfigElement?.();
  } catch (e) { /* ignorieren – Fallback unten */ }
  await Promise.race([customElements.whenDefined("ha-form"), new Promise((r) => setTimeout(r, 3000))]);
}

class TCEditor extends HTMLElement {
  setConfig(cfg) { this._cfg = { ...cfg }; this._render(); }
  set hass(h) { this._hass = h; this._render(); }
  get _t() { const l = (this._hass?.locale?.language || this._hass?.language || "en").slice(0, 2); return ED_I18N[l] || ED_I18N.en; }
  _schema() {
    const t = this._t, fields = this.constructor.fields;
    const all = {
      entity: { name: "entity", required: true, selector: { entity: { domain: "climate", integration: "thermocore" } } },
      show_overrides: { name: "show_overrides", selector: { boolean: {} } },
      show_start_stop: { name: "show_start_stop", selector: { boolean: {} } },
      theme: { name: "theme", selector: { select: { mode: "dropdown", options: [
        { value: "dark", label: t.dark }, { value: "light", label: t.light }, { value: "auto", label: t.auto }] } } },
      language: { name: "language", selector: { select: { mode: "dropdown", options: [
        { value: "auto", label: t.lang_auto }, { value: "de", label: "Deutsch" }, { value: "en", label: "English" }] } } },
    };
    return fields.map((f) => all[f]);
  }
  async _render() {
    if (!this._hass || !this._cfg) return;
    if (!this._form) {
      await ensureHaForm();
      if (this._form) return;
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (e) => {
        e.stopPropagation();
        const fields = this.constructor.fields, v = e.detail.value || {};
        const cfg = { ...this._cfg };
        for (const f of fields) if (v[f] !== undefined) cfg[f] = v[f];
        if (!cfg.language || cfg.language === "auto") delete cfg.language;
        this._cfg = cfg;
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: cfg }, bubbles: true, composed: true }));
      });
      this.appendChild(this._form);
    }
    const defaults = { theme: "dark", show_overrides: true, show_start_stop: true, language: "auto" };
    const d = {};
    for (const f of this.constructor.fields) d[f] = this._cfg[f] ?? defaults[f];
    this._form.hass = this._hass;
    this._form.data = d;
    this._form.schema = this._schema();
    this._form.computeLabel = (sch) => this._t[sch.name] || sch.name;
  }
}
class TCControlEditor extends TCEditor { static fields = ["theme", "language"]; }
class TCRoomEditor extends TCEditor { static fields = ["entity", "show_overrides", "show_start_stop", "theme", "language"]; }
class TCOverviewEditor extends TCEditor { static fields = ["show_overrides", "show_start_stop", "theme", "language"]; }
for (const [tag, cls] of [["thermocore-control-card-editor", TCControlEditor], ["thermocore-room-card-editor", TCRoomEditor], ["thermocore-overview-card-editor", TCOverviewEditor]]) {
  customElements.get(tag) || customElements.define(tag, cls);
}
ThermoCoreControlCard.getConfigElement = () => document.createElement("thermocore-control-card-editor");
ThermoCoreRoomCard.getConfigElement = () => document.createElement("thermocore-room-card-editor");
ThermoCoreOverviewCard.getConfigElement = () => document.createElement("thermocore-overview-card-editor");

customElements.get("thermocore-control-card") || customElements.define("thermocore-control-card", ThermoCoreControlCard);
customElements.get("thermocore-room-card") || customElements.define("thermocore-room-card", ThermoCoreRoomCard);
customElements.get("thermocore-overview-card") || customElements.define("thermocore-overview-card", ThermoCoreOverviewCard);

window.customCards = window.customCards || [];
window.customCards.push(
  { type: "thermocore-control-card", name: "ThermoCore – Heizungssteuerung / Heating control", preview: true },
  { type: "thermocore-room-card", name: "ThermoCore – Raumthermostat / Room thermostat", preview: true },
  { type: "thermocore-overview-card", name: "ThermoCore – Übersicht / Overview", preview: true },
);
console.info(`%cThermoCore cards ${TC_VERSION}`, "color:#13a3ff;font-weight:bold");
