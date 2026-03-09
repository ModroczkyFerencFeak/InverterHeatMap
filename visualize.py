# -*- coding: utf-8 -*-
"""
Gyors heatmap generátor: adat külön JSON, HTML minimalizált, chunked marker betöltés.
Futtatás: python visualize.py
Kimenet: data.json, heatmap.html (kis méret, gyors betöltés).
"""
import csv
import json
import html as html_module
from collections import Counter
from urllib.request import urlopen, Request
from urllib.error import URLError

def fetch_url(url, timeout=15):
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; HeatmapGenerator/1.0)"})
        with urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except (URLError, OSError, Exception) as e:
        print(f"  Figyelmeztetés: nem sikerült letölteni: {url} – {e}")
        return None

CSV_PATH = "geocoded_output.csv"
DATA_JSON = "data.json"
OUT_HTML = "heatmap.html"

# --- Adat betöltés (beépített csv, pandas nélkül) ---
heat_city = []
heat_addr = []
markers = []

with open(CSV_PATH, "r", encoding="utf-8") as f:
    r = csv.DictReader(f, delimiter=";")
    for row in r:
        try:
            lat = float(row.get("latitude", ""))
            lon = float(row.get("longitude", ""))
        except (ValueError, TypeError):
            continue
        city = (row.get("City") or "").strip()
        search_type = (row.get("search_type") or "").strip()
        zip_val = row.get("Zip_corrected") or row.get("Zip", "")  # Korrigált irányítószám ha volt 0000
        recd = (row.get("RecdAt") or "").strip()
        sn = (row.get("SN") or "").strip()
        brand = (row.get("Brand") or "").strip()
        model = (row.get("Model") or "").strip()
        installed = (row.get("Installed") or "").strip()
        street = (row.get("Street") or "").strip()
        street_type = (row.get("StreetType") or "").strip()
        street_no = (row.get("StreetNo") or "").strip()
        building = (row.get("Building") or "").strip()

        if search_type == "address":
            heat_addr.append([lat, lon])
        else:
            heat_city.append([lat, lon])

        # Cím összerakása: utca + házszám (StreetNo vagy Building), ha nincs akkor City első része
        address_short = ""
        num_part = street_no or building
        if street and street != city:
            address_short = f"{street} {num_part}".strip() if num_part else street
        elif num_part:
            address_short = f"{city.split(',')[0].strip()} {num_part}".strip() if city else num_part
        else:
            address_short = city.split(",")[0].strip() if city else ""

        popup_parts = []
        if address_short:
            popup_parts.append(f"<b>Cím / hely:</b> {html_module.escape(address_short)}")
        if city and city != address_short:
            popup_parts.append(f"<b>Részletes:</b> {html_module.escape(city)}")
        popup_parts.append(f"<b>Szint:</b> {'cím' if search_type == 'address' else 'város (középpont)'}")
        if zip_val and str(zip_val) != "0":
            popup_parts.append(f"<b>Irsz.:</b> {html_module.escape(str(zip_val))}")
        if brand:
            popup_parts.append(f"<b>Gyártó:</b> {html_module.escape(brand)}")
        if model:
            popup_parts.append(f"<b>Típus:</b> {html_module.escape(model)}")
        if sn:
            popup_parts.append(f"<b>Sorozatszám (SN):</b> {html_module.escape(sn)}")
        if installed:
            popup_parts.append(f"<b>Telepítve:</b> {html_module.escape(installed)}")
        popup_html = "<br>".join(popup_parts)

        markers.append({
            "lat": lat,
            "lng": lon,
            "city": city,
            "search_type": search_type,
            "zip": str(zip_val),
            "recdAt": recd,
            "address_short": address_short,
            "street": street,
            "street_no": street_no,
            "sn": sn,
            "brand": brand,
            "model": model,
            "installed": installed,
            "popup": popup_html,
        })

data = {
    "heat_city": heat_city,
    "heat_addr": heat_addr,
    "markers": markers,
}

with open(DATA_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

print(f"Adat mentve: {DATA_JSON} ({len(markers)} marker, {len(heat_city)} heat city, {len(heat_addr)} heat addr)")

# --- Gyors HTML sablon: 1 tile alapból, canvas, fetch + chunked markerek ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Heatmap</title>
  <link rel="icon" type="image/png" href="media/logo.png" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
  <style>
    html, body { height: 100%%; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; font-size: 14px; }
    #map { position: absolute; top: 0; left: 0; right: 0; bottom: 0; height: 100%%; min-height: 100vh; width: 100%%; z-index: 1; }
    #sidebar {
      position: fixed; top: 12px; left: 12px; width: 320px; max-width: calc(100vw - 24px); max-height: calc(100vh - 24px);
      background: #fff; z-index: 9999; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,.12);
      overflow: hidden; border: 1px solid rgba(0,0,0,.06);
      display: flex; flex-direction: column;
    }
    #sidebar-header {
      padding: 14px 16px; cursor: pointer; user-select: none; flex-shrink: 0;
      font-weight: 600; font-size: 16px; border-bottom: 1px solid #e5e7eb;
      display: flex; align-items: center; justify-content: space-between;
      background: linear-gradient(180deg, #f8fafc 0%%, #fff 100%%);
    }
    #sidebar-header:hover { background: #f1f5f9; }
    #sidebar-header .toggler { font-size: 11px; color: #64748b; }
    #sidebar-content { padding: 14px; flex-shrink: 0; overflow: visible; }
    #sidebar.collapsed #sidebar-content { display: none; }
    #sidebar.collapsed #data-panel { display: none; }
    .filter-section { margin-bottom: 14px; }
    .filter-section:last-of-type { margin-bottom: 0; }
    .filter-section.collapsible .filter-section-header {
      font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b;
      margin-bottom: 8px; cursor: pointer; user-select: none; display: flex; align-items: center; justify-content: space-between;
      padding: 4px 0;
    }
    .filter-section.collapsible .filter-section-header:hover { color: #1e293b; }
    .filter-section.collapsible .filter-section-header .section-toggler { font-size: 10px; }
    .filter-section.collapsible.collapsed .filter-section-content { display: none; }
    .filter-section.collapsible.collapsed .filter-section-header .section-toggler { transform: rotate(-90deg); }
    .filter-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; margin-bottom: 8px; }
    #sidebar-content label { display: block; margin-bottom: 4px; font-size: 12px; color: #475569; }
    #sidebar-content input[type="text"] {
      width: 100%%; min-width: 0; box-sizing: border-box; padding: 8px 10px;
      border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px;
    }
    #sidebar-content input[type="text"]:focus {
      outline: none; border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,.2);
    }
    .filter-section-content { display: flex; flex-direction: column; gap: 14px; padding-top: 2px; }
    .filter-field { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
    .filter-field label { margin-bottom: 0; }
    .filter-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .filter-row.full { grid-template-columns: 1fr; }
    .filter-row > div { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
    .filter-row > div label { margin-bottom: 0; }
    .filter-section-content > label:last-of-type { margin-top: 4px; margin-bottom: 0; flex-direction: row; align-items: center; display: flex; cursor: pointer; }
    #sidebar-content input[type="checkbox"] { margin-right: 8px; vertical-align: middle; }
    .btn-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
    #sidebar-content .btn { padding: 8px 12px; border-radius: 8px; font-size: 12px; font-weight: 500; cursor: pointer; border: none; }
    #sidebar-content .btn-primary { background: #2563eb; color: #fff; }
    #sidebar-content .btn-primary:hover { background: #1d4ed8; }
    #sidebar-content .btn-secondary { background: #f1f5f9; color: #475569; }
    #sidebar-content .btn-secondary:hover { background: #e2e8f0; }
    #data-panel {
      flex: 1; min-height: 0; overflow: auto; padding: 12px; font-size: 12px;
      border-top: 1px solid #e5e7eb; background: #f8fafc;
    }
    .panel-section { margin-bottom: 14px; }
    .panel-section:last-child { margin-bottom: 0; }
    .panel-section:has(#cities-wrap) { flex: 0 1 auto; min-height: 0; }
    .panel-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; margin-bottom: 6px; }
    .panel-section-title.with-btn { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
    .panel-section.collapsible .panel-section-header {
      display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;
      font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b;
      margin-bottom: 6px; cursor: pointer; user-select: none; padding: 4px 0;
    }
    .panel-section.collapsible .panel-section-header:hover { color: #1e293b; }
    .panel-section.collapsible .panel-section-header .section-toggler { font-size: 10px; transition: transform 0.2s; }
    .panel-section.collapsible.collapsed .panel-section-body { display: none; }
    .panel-section.collapsible.collapsed .panel-section-header .section-toggler { transform: rotate(-90deg); }
    .btn-open-table { font-size: 11px; padding: 4px 8px; border-radius: 6px; border: 1px solid #e2e8f0; background: #fff; color: #475569; cursor: pointer; white-space: nowrap; }
    .btn-open-table:hover { background: #f1f5f9; color: #1e293b; }
    .stats-grid { margin-bottom: 12px; }
    .stat-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; }
    .stat-box .label { font-size: 11px; color: #64748b; }
    .stat-box .value { font-size: 16px; font-weight: 700; color: #1e293b; }
    .stat-box .value span { font-weight: 400; color: #64748b; font-size: 13px; }
    #data-panel table { width: 100%%; border-collapse: collapse; }
    #data-panel th, #data-panel td { text-align: left; padding: 5px 8px; border-bottom: 1px solid #e2e8f0; }
    #data-panel th { font-weight: 600; color: #475569; font-size: 11px; }
    #cities-table { table-layout: fixed; width: 100%%; box-sizing: border-box; }
    #cities-table th:first-child, #cities-table td:first-child { width: auto; min-width: 0; }
    #cities-table th:last-child, #cities-table td:last-child { width: 48px; min-width: 48px; text-align: right; }
    #cities-table tbody tr:hover { background: #f1f5f9; }
    #cities-wrap { max-height: 220px; min-height: 0; overflow-y: auto; margin-top: 6px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; }
    #cities-wrap table { width: 100%%; min-width: 100%%; box-sizing: border-box; }
    #cities-table thead th { position: sticky; top: 0; background: #f8fafc; z-index: 1; box-shadow: 0 1px 0 #e2e8f0; }
    #details-wrap { max-height: 200px; overflow: auto; margin-top: 6px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; }
    #details-table { width: 100%%; border-collapse: collapse; font-size: 11px; }
    #details-table th, #details-table td { padding: 4px 6px; border-bottom: 1px solid #f1f5f9; text-align: left; }
    #details-table th { font-weight: 600; background: #f1f5f9; position: sticky; top: 0; z-index: 1; }
    #legend {
      position: fixed; top: 10px; right: 148px; left: auto; width: auto; min-width: 140px;
      background: #fff; z-index: 9999; padding: 12px 14px; font-size: 13px; line-height: 1.6;
      box-shadow: 0 2px 12px rgba(0,0,0,.15); border-radius: 8px; border: 1px solid rgba(0,0,0,.08);
      display: none;
    }
    #legend-wrap { position: fixed; top: 10px; right: 148px; z-index: 9999; }
    #legend-wrap:hover #legend { display: block; }
    #legend-trigger {
      display: block; padding: 6px 12px; font-size: 11px; font-weight: 600; color: #64748b;
      background: #fff; border-radius: 8px; border: 1px solid rgba(0,0,0,.08);
      box-shadow: 0 2px 8px rgba(0,0,0,.1); cursor: default; width: fit-content; margin-left: auto;
    }
    #legend-trigger:hover { color: #1e293b; }
    #legend .legend-title { font-weight: 600; color: #1e293b; margin-bottom: 6px; font-size: 12px; }
    #legend .legend-item { display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
    #legend .legend-dot { width: 10px; height: 10px; border-radius: 50%%; flex-shrink: 0; }
    #legend .legend-dot.city { background: #22c55e; }
    #legend .legend-dot.address { background: #3b82f6; }
    #legend-wrap #legend { padding-right: 12px; }
    #legend-toggle {
      position: fixed; bottom: 20px; left: 20px; z-index: 9999; display: none;
      width: 36px; height: 36px; border: none; background: #fff; border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0,0,0,.15); border: 1px solid rgba(0,0,0,.08);
      cursor: pointer; font-size: 16px; color: #475569; padding: 0;
      align-items: center; justify-content: center; line-height: 1;
    }
    #legend-toggle:hover { background: #f8fafc; color: #1e293b; } 
    #map-logo {
      position: fixed; bottom: 12px; right: 12px; z-index: 9998;
      max-height: 72px; max-width: 180px; pointer-events: none;
    }
    #map-logo img { display: block; max-height: 72px; max-width: 180px; width: auto; height: auto; }
    #loading {
      position: fixed; top: 50%%; left: 50%%; transform: translate(-50%%,-50%%); z-index: 10000;
      display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px;
      background: #fff; padding: 28px 36px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,.12); max-width: 90%%; box-sizing: border-box; text-align: center;
      font-size: 15px; color: #475569; font-weight: 500;
    }
    #loading::before {
      content: ''; width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%%; animation: loading-spin .85s linear infinite;
    }
    @keyframes loading-spin { to { transform: rotate(360deg); } }
    #loading.loading-error::before { display: none; }
    #loading code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
  </style>
  <style>
    .leaflet-control-layers-toggle { background-image: url(https://unpkg.com/leaflet@1.9.3/dist/images/layers.png) !important; }
    .leaflet-retina .leaflet-control-layers-toggle { background-image: url(https://unpkg.com/leaflet@1.9.3/dist/images/layers-2x.png) !important; }
  </style>
</head>
<body>
  <div id="loading"><span>Térkép betöltése...</span></div>
  <div id="sidebar" style="display:none;">
    <div id="sidebar-header" title="Kattints az összecsukáshoz / kinyitáshoz">
      <span>Szűrők</span>
      <span class="toggler" id="sidebar-toggler">▼</span>
    </div>
    <div id="sidebar-content">
      <div class="filter-section collapsible" id="filter-section-search">
        <div class="filter-section-header" title="Kattints az összecsukáshoz / kinyitáshoz">
          <span>Keresés és szűrés</span>
          <span class="section-toggler">▼</span>
        </div>
        <div class="filter-section-content">
        <div class="filter-field">
          <label for="searchfilter">Város vagy irányítószám</label>
          <input type="text" id="searchfilter" placeholder="pl. Budapest, 1201" autocomplete="off" />
        </div>
        <div class="filter-row">
          <div class="filter-field"><label for="filterBrand">Gyártó</label><input type="text" id="filterBrand" list="brand-list" placeholder="pl. Solinteg" autocomplete="off" /></div>
          <div class="filter-field"><label for="filterModel">Típus</label><input type="text" id="filterModel" list="model-list" placeholder="pl. MHT-5K" autocomplete="off" /></div>
        </div>
        <div class="filter-row full">
          <div class="filter-field">
            <label for="filterInstalled">Telepítve (év / dátum rész)</label>
            <input type="text" id="filterInstalled" placeholder="pl. 2024, 2026.02" autocomplete="off" />
          </div>
        </div>
        <div class="btn-row" style="margin-top: 10px;">
          <button type="button" id="btnApply" class="btn btn-primary">Alkalmaz</button>
        </div>
        </div>
      </div>
      <div class="filter-section collapsible collapsed" id="filter-section-actions">
        <div class="filter-section-header" title="Kattints az összecsukáshoz / kinyitáshoz">
          <span>Műveletek</span>
          <span class="section-toggler">▼</span>
        </div>
        <div class="filter-section-content">
        <div class="btn-row">
          <button type="button" id="btnClear" class="btn btn-secondary">Törlés</button>
          <button type="button" id="btnExport" class="btn btn-secondary">Export CSV</button>
          <button type="button" id="btnExportIframe" class="btn btn-secondary" title="Egyetlen HTML letöltése">Export iframe</button>
        </div>
        </div>
      </div>
      <datalist id="brand-list">__BRAND_OPTIONS__</datalist>
      <datalist id="model-list"></datalist>
    </div>
    <div id="data-panel">
      <p style="margin:0 0 12px 0; padding:8px 10px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; font-size:11px; color:#1e40af;">Ha az adat nem tölt be (nagy fájl): nyisd meg a <strong>heatmap-standalone.html</strong> fájlt fájlkezelőben (dupla kattintás) – nincs szerver, minden adat benne van.</p>
      <div class="panel-section">
        <div class="panel-section-title">Összesítés</div>
        <div class="stats-grid">
          <div class="stat-box">
            <div class="label">Megjelenített adatok</div>
            <div class="value"><span id="stat-visible">__TOTAL__</span> megjelenítve <span>(összesen <span id="stat-total">__TOTAL__</span>)</span></div>
          </div>
        </div>
      </div>
      <div class="panel-section collapsible" id="panel-section-details">
        <div class="panel-section-header with-btn" title="Kattints az összecsukáshoz / kinyitáshoz">
          <span>Részletes adatok (előnézet, max. 500 sor – teljes lista: Táblázat megnyitása)</span>
          <span style="display:flex;align-items:center;gap:6px;">
            <button type="button" class="btn-open-table" id="btnOpenDetailsTable" title="Megnyitás táblázatos nézetben (új ablak)" onclick="event.stopPropagation()">Táblázat megnyitása</button>
            <span class="section-toggler">▼</span>
          </span>
        </div>
        <div id="details-wrap" class="panel-section-body">
          <table id="details-table">
            <thead><tr><th>Város</th><th>Cím</th><th>Gyártó</th><th>Típus</th><th>SN</th><th>Telepítve</th></tr></thead>
            <tbody id="details-tbody"></tbody>
          </table>
        </div>
      </div>
      <div class="panel-section collapsible" id="panel-section-cities">
        <div class="panel-section-header with-btn" title="Kattints az összecsukáshoz / kinyitáshoz">
          <span>Városok (megjelenítve)</span>
          <span style="display:flex;align-items:center;gap:6px;">
            <button type="button" class="btn-open-table" id="btnOpenCitiesTable" title="Megnyitás táblázatos nézetben (új ablak)" onclick="event.stopPropagation()">Táblázat megnyitása</button>
            <span class="section-toggler">▼</span>
          </span>
        </div>
        <div id="cities-wrap" class="panel-section-body">
        <table id="cities-table">
          <colgroup><col style="width: 85%%" /><col style="width: 15%%" /></colgroup>
          <thead><tr><th>Város / hely</th><th>Db</th></tr></thead>
          <tbody id="cities-tbody">__CITIES_ROWS__</tbody>
        </table>
        </div>
      </div>
    </div>
  </div>
  <div id="legend-wrap" style="display:none;">
    <div id="legend">
      <div class="legend-title">Jelmagyarázat</div>
      <div class="legend-item"><span class="legend-dot city"></span><span>Város (középpont)</span></div>
      <div class="legend-item"><span class="legend-dot address"></span><span>Cím (utca szint)</span></div>
    </div>
    <div id="legend-trigger" title="Jelmagyarázat (hover)">Jelmagyarázat</div>
  </div>
  <div id="map-logo" style="display:none;"><img src="media/logo.png" alt="Logo" /></div>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
  <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
  <script>
(function(){
  function hideLoading(errMsg) {
    var el = document.getElementById('loading');
    if (el) {
      if (errMsg) {
        el.classList.add('loading-error');
        el.innerHTML = '<div style="max-width:420px;line-height:1.5;">' + errMsg + '</div>';
        el.style.display = 'block';
        el.style.color = '#c00';
      } else {
        el.classList.remove('loading-error');
        el.style.display = 'none';
      }
    }
  }
  function showUI() {
    var loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
    var s = document.getElementById('sidebar'); if (s) s.style.display = 'block';
    var w = document.getElementById('legend-wrap'); if (w) w.style.display = 'block';
    var logo = document.getElementById('map-logo'); if (logo) logo.style.display = 'block';
  }
  if (typeof L === 'undefined') {
    hideLoading('Leaflet nem töltődött be. Ellenőrizd a hálózatot (CDN), majd frissítsd az oldalt.');
    return;
  }
  function initMap() {
  try {
  var MAP_CENTER = [47.1625, 19.5033];
  var MAP_ZOOM = 7;
  var CHUNK_SIZE = 180;
  var filterSearch = '';
  var filterBrand = '';
  var filterModel = '';
  var filterInstalled = '';
  var showPins = true;

  var map = L.map('map', {
    center: MAP_CENTER,
    zoom: MAP_ZOOM,
    preferCanvas: true,
    zoomControl: true
  });
  L.control.scale().addTo(map);

  var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  });
  var dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CartoDB'
  });
  osm.addTo(map);

  var baseLayers = { 'OSM': osm, 'Sötét': dark };
  var overlays = {};
  var heatCity = L.heatLayer([], { radius: 10, blur: 15, maxZoom: 12, gradient: { 0.4: 'blue', 0.65: 'lime', 1: 'red' } });
  var heatAddr = L.heatLayer([], { radius: 10, blur: 15, maxZoom: 12, gradient: { 0.4: 'purple', 0.65: 'orange', 1: 'red' } });
  var fgOverlays = L.featureGroup();
  var cluster = L.markerClusterGroup({ chunkedLoading: true });
  var allMarkers = [];
  var brandsToModels = {};
  var allModels = new Set();
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }
  fgOverlays.addLayer(cluster);
  overlays['Heatmap - Város'] = heatCity;
  overlays['Heatmap - Cím'] = heatAddr;
  overlays['Pintek'] = fgOverlays;
  L.control.layers(baseLayers, overlays, { collapsed: true }).addTo(map);
  heatCity.addTo(map);
  heatAddr.addTo(map);
  fgOverlays.addTo(map);
  map.invalidateSize();
  showUI();
  hideLoading();

  function matchFilter(m) {
    if (filterSearch) {
      var s = filterSearch.toLowerCase();
      var city = (m.city && m.city.toString().toLowerCase()) || '';
      var zip = (m.zip && m.zip.toString().toLowerCase()) || '';
      if (city.indexOf(s) === -1 && zip.indexOf(s) === -1) return false;
    }
    if (filterBrand) {
      var b = (m.brand && m.brand.toString().toLowerCase()) || '';
      if (b.indexOf(filterBrand) === -1) return false;
    }
    if (filterModel) {
      var t = (m.model && m.model.toString().toLowerCase()) || '';
      if (t.indexOf(filterModel) === -1) return false;
    }
    if (filterInstalled) {
      var i = (m.installed && m.installed.toString().toLowerCase()) || '';
      if (i.indexOf(filterInstalled) === -1) return false;
    }
    return true;
  }

  function applyFilters() {
    var searchEl = document.getElementById('searchfilter');
    var brandEl = document.getElementById('filterBrand');
    var modelEl = document.getElementById('filterModel');
    var installedEl = document.getElementById('filterInstalled');
    filterSearch = (searchEl && searchEl.value || '').trim().toLowerCase();
    filterBrand = (brandEl && brandEl.value || '').trim().toLowerCase();
    filterModel = (modelEl && modelEl.value || '').trim().toLowerCase();
    filterInstalled = (installedEl && installedEl.value || '').trim().toLowerCase();
    showPins = true;
    cluster.clearLayers();
    var visibleCity = [];
    var visibleAddr = [];
    for (var i = 0; i < allMarkers.length; i++) {
      var layer = allMarkers[i];
      var m = layer.options && layer.options.data;
      if (!m) continue;
      var show = matchFilter(m) && showPins;
      if (show) {
        cluster.addLayer(layer);
        if (m.search_type === 'address') visibleAddr.push([m.lat, m.lng]);
        else visibleCity.push([m.lat, m.lng]);
      }
    }
    heatCity.setLatLngs(visibleCity);
    heatAddr.setLatLngs(visibleAddr);
    updateDataTable();
  }

  function updateDataTable() {
    var total = allMarkers.length;
    var layers = cluster.getLayers();
    var visible = layers.length;
    var byCity = {};
    for (var i = 0; i < layers.length; i++) {
      var m = layers[i].options && layers[i].options.data;
      if (m) {
        var name = (m.city && m.city.split(',')[0].trim()) || '–';
        byCity[name] = (byCity[name] || 0) + 1;
      }
    }
    var totalEl = document.getElementById('stat-total');
    var visibleEl = document.getElementById('stat-visible');
    if (totalEl) totalEl.textContent = total.toLocaleString('hu-HU');
    if (visibleEl) visibleEl.textContent = visible.toLocaleString('hu-HU');
    var tbody = document.getElementById('cities-tbody');
    if (tbody) {
      var cities = Object.keys(byCity).sort(function(a,b) { return byCity[b] - byCity[a]; });
      tbody.innerHTML = cities.map(function(c) { return '<tr><td>' + esc(c) + '</td><td>' + byCity[c] + '</td></tr>'; }).join('');
    }
    var detailsBody = document.getElementById('details-tbody');
    if (detailsBody) {
      var maxRows = 500;
      var rows = [];
      for (var j = 0; j < layers.length && j < maxRows; j++) {
        var md = layers[j].options && layers[j].options.data;
        if (!md) continue;
        var cityShort = (md.city && md.city.split(',')[0].trim()) || '–';
        rows.push('<tr><td>' + esc(cityShort) + '</td><td>' + esc((md.address_short || '').substring(0, 30)) + '</td><td>' + esc(md.brand) + '</td><td>' + esc(md.model) + '</td><td>' + esc(md.sn) + '</td><td>' + esc(md.installed) + '</td></tr>');
      }
      detailsBody.innerHTML = rows.join('');
      if (layers.length > maxRows) detailsBody.innerHTML += '<tr><td colspan="6"><em>… és még ' + (layers.length - maxRows) + ' pont</em></td></tr>';
    }
  }

  function updateModelDatalist() {
    var brandInput = document.getElementById('filterBrand');
    var modelList = document.getElementById('model-list');
    if (!modelList) return;
    var brandVal = (brandInput && brandInput.value || '').trim().toLowerCase();
    var models;
    if (brandVal) {
      var modelsSet = new Set();
      for (var k in brandsToModels) {
        if (k.indexOf(brandVal) !== -1) brandsToModels[k].forEach(function(m) { modelsSet.add(m); });
      }
      models = Array.from(modelsSet);
    } else {
      models = Array.from(allModels);
    }
    models.sort();
    modelList.innerHTML = models.map(function(m) { return '<option value="' + esc(m) + '">'; }).join('');
  }

  function exportVisible() {
    var rows = ['lat,lon,popup'];
    var layers = cluster.getLayers();
    for (var i = 0; i < layers.length; i++) {
      var layer = layers[i];
      var c = layer.getLatLng();
      var popup = (layer.options && layer.options.data && layer.options.data.popup) || '';
      rows.push([c.lat, c.lng, '"' + String(popup).replace(/"/g, '""') + '"'].join(','));
    }
    var blob = new Blob([rows.join('\\n')], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'visible.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function openTableInWindow(title, theadHtml, tbodyHtml) {
    var html = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>' + esc(title) + '</title><style>'
      + 'body{font-family:Segoe UI,sans-serif;margin:12px;background:#f8fafc;}'
      + 'h1{font-size:16px;color:#1e293b;margin:0 0 12px 0;}'
      + '.table-filter{margin-bottom:10px;padding:8px 12px;width:100%%;max-width:400px;box-sizing:border-box;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;}'
      + '.table-filter:focus{outline:none;border-color:#3b82f6;}'
      + 'table{width:100%%;border-collapse:collapse;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.1);border-radius:8px;}'
      + 'th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e2e8f0;}'
      + 'th{background:#f1f5f9;font-weight:600;color:#475569;}'
      + 'tr:hover{background:#f8fafc;}'
      + 'tr.hidden{display:none;}'
      + '</style></head><body><h1>' + esc(title) + '</h1>'
      + '<p><input type="text" class="table-filter" id="tableFilter" placeholder="Szűrés a táblázatban (város, cím, gyártó, modell…)..." autocomplete="off"></p>'
      + '<table><thead>' + theadHtml + '</thead><tbody id="popup-tbody">' + tbodyHtml + '</tbody></table></body>'
      + '<script>'
      + '(function(){ var inp=document.getElementById("tableFilter"); var tbody=document.getElementById("popup-tbody"); if(!inp||!tbody)return; '
      + 'function filter(){ var q=(inp.value||"").trim().toLowerCase(); var rows=tbody.querySelectorAll("tr"); '
      + 'for(var i=0;i<rows.length;i++){ var tr=rows[i]; var show=!q||(tr.textContent||"").toLowerCase().indexOf(q)!==-1; tr.classList.toggle("hidden",!show); } '
      + '} '
      + 'inp.addEventListener("input",filter); inp.addEventListener("keyup",filter); })();'
      + '<\\/script></html>';
    var w = window.open('', '_blank', 'width=960,height=680,scrollbars=yes,resizable=yes');
    if (w) {
      w.document.write(html);
      w.document.close();
    } else {
      alert('Engedélyezd a felugró ablakokat a táblázat megnyitásához.');
    }
  }

  var el;
  el = document.getElementById('btnOpenDetailsTable'); if (el) el.addEventListener('click', function() {
    var tbl = document.getElementById('details-table');
    if (!tbl) return;
    var thead = tbl.querySelector('thead');
    var layers = cluster.getLayers();
    var rows = [];
    for (var j = 0; j < layers.length; j++) {
      var md = layers[j].options && layers[j].options.data;
      if (!md) continue;
      var cityShort = (md.city && md.city.split(',')[0].trim()) || '–';
      rows.push('<tr><td>' + esc(cityShort) + '</td><td>' + esc((md.address_short || '').substring(0, 50)) + '</td><td>' + esc(md.brand) + '</td><td>' + esc(md.model) + '</td><td>' + esc(md.sn) + '</td><td>' + esc(md.installed) + '</td></tr>');
    }
    openTableInWindow('Részletes adatok (összes megjelenített: ' + rows.length + ' pont)', thead ? thead.innerHTML : '', rows.join(''));
  });
  el = document.getElementById('btnOpenCitiesTable'); if (el) el.addEventListener('click', function() {
    var tbl = document.getElementById('cities-table');
    if (!tbl) return;
    var thead = tbl.querySelector('thead');
    var tbody = document.getElementById('cities-tbody');
    openTableInWindow('Városok (megjelenítve)', thead ? thead.innerHTML : '', tbody ? tbody.innerHTML : '');
  });
  el = document.getElementById('btnApply'); if (el) el.addEventListener('click', applyFilters);
  el = document.getElementById('btnClear'); if (el) el.addEventListener('click', function() {
    var sf = document.getElementById('searchfilter'); if (sf) sf.value = '';
    var fb = document.getElementById('filterBrand'); if (fb) fb.value = '';
    var fm = document.getElementById('filterModel'); if (fm) fm.value = '';
    var fi = document.getElementById('filterInstalled'); if (fi) fi.value = '';
    applyFilters();
  });
  el = document.getElementById('searchfilter'); if (el) {
    el.addEventListener('keydown', function(e) { if (e.key === 'Enter') applyFilters(); });
    el.addEventListener('input', function() {
      var t = this._searchTimer;
      if (t) clearTimeout(t);
      this._searchTimer = setTimeout(applyFilters, 400);
    });
  }
  el = document.getElementById('filterBrand'); if (el) {
    el.addEventListener('input', updateModelDatalist);
    el.addEventListener('change', updateModelDatalist);
  }
  el = document.getElementById('btnExport'); if (el) el.addEventListener('click', exportVisible);
  el = document.getElementById('btnExportIframe'); if (el) el.addEventListener('click', function() {
    fetch('heatmap-standalone.html').then(function(r) {
      if (!r.ok) throw new Error('Szerver nem adta vissza a fájlt.');
      return r.text();
    }).then(function(html) {
      if (!html || html.length < 1000) throw new Error('A fájl túl nagy a szerverről való betöltéshez.');
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([html], { type: 'text/html;charset=utf-8' }));
      a.download = 'heatmap-iframe.html';
      a.click();
      URL.revokeObjectURL(a.href);
    }).catch(function() {
      alert('A heatmap-standalone.html nem tölthető a szerverről (túl nagy fájl).\\n\\nNyisd meg közvetlenül fájlként: dupla kattintás a heatmap-standalone.html-re a mappában.');
    });
  });
  el = document.getElementById('sidebar-header'); if (el) el.addEventListener('click', function() {
    var sb = document.getElementById('sidebar');
    var t = document.getElementById('sidebar-toggler');
    if (sb) sb.classList.toggle('collapsed');
    if (t) t.textContent = sb && sb.classList.contains('collapsed') ? '▶' : '▼';
  });
  document.querySelectorAll('.filter-section.collapsible .filter-section-header').forEach(function(header) {
    header.addEventListener('click', function() {
      var section = this.closest('.filter-section');
      if (section) section.classList.toggle('collapsed');
    });
  });
  document.querySelectorAll('.panel-section.collapsible .panel-section-header').forEach(function(header) {
    header.addEventListener('click', function() {
      var section = this.closest('.panel-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  function addMarkersInChunks(list, index, done) {
    index = index || 0;
    if (index >= list.length) {
      if (typeof map.invalidateSize === 'function') map.invalidateSize();
      if (done) done();
      return;
    }
    var end = Math.min(index + CHUNK_SIZE, list.length);
    for (var i = index; i < end; i++) {
      var m = list[i];
      var color = m.search_type === 'address' ? 'blue' : 'green';
      var marker = L.circleMarker([m.lat, m.lng], {
        radius: 5,
        fillColor: color,
        color: color,
        weight: 2,
        fillOpacity: 0.7,
        data: m
      });
      marker.bindPopup(m.popup, { maxWidth: 280 });
      if (m.address_short) marker.bindTooltip(m.address_short, { permanent: false, direction: 'top', className: 'marker-tooltip' });
      marker.addTo(cluster);
      allMarkers.push(marker);
    }
    requestAnimationFrame(function() { addMarkersInChunks(list, end, done); });
  }

  var dataPromise = window.__MAP_DATA__
    ? Promise.resolve(window.__MAP_DATA__)
    : fetch('data.json').then(function(r) {
        if (!r.ok) throw new Error('data.json nem elérhető (pl. indítsd a Live Server-t a mappában).');
        return r.json();
      });
  var statVisible = document.getElementById('stat-visible');
  var statTotal = document.getElementById('stat-total');
  if (statVisible) statVisible.textContent = 'Betöltés…';
  if (statTotal) statTotal.textContent = 'Betöltés…';
  var loadingTimeout = setTimeout(function() {
    var el = document.getElementById('loading');
    if (el && el.style.display !== 'none' && el.textContent.indexOf('Hiba') === -1) {
      el.innerHTML = '<div style="max-width:420px;line-height:1.5;">A betöltés sokáig tart (a data.json nagy lehet). Várj még 1 percet, vagy nyisd meg a böngésző konzolt (F12) hibákért.</div>';
      el.style.color = '#c00';
    }
  }, 60000);
  dataPromise
    .then(function(d) {
      if (!d) { showUI(); hideLoading('Nincs adat.'); return; }
      requestAnimationFrame(function() {
        heatCity.setLatLngs(d.heat_city || []);
        heatAddr.setLatLngs(d.heat_addr || []);
      });
      var list = d.markers || [];
      var i, m, brand, brandLower, modelStr;
      for (i = 0; i < list.length; i++) {
        m = list[i];
        brand = (m.brand && m.brand.toString().trim()) || '';
        brandLower = brand.toLowerCase();
        modelStr = (m.model && m.model.toString().trim()) || '';
        if (modelStr) {
          allModels.add(modelStr);
          if (brandLower) {
            if (!brandsToModels[brandLower]) brandsToModels[brandLower] = new Set();
            brandsToModels[brandLower].add(modelStr);
          }
        }
      }
      addMarkersInChunks(list, 0, function() {
        clearTimeout(loadingTimeout);
        if (typeof map.invalidateSize === 'function') map.invalidateSize();
        updateModelDatalist();
        applyFilters();
        setTimeout(updateDataTable, 100);
        setTimeout(updateDataTable, 500);
        setTimeout(function() { if (map && map.invalidateSize) map.invalidateSize(); }, 150);
        setTimeout(function() { if (map && map.invalidateSize) map.invalidateSize(); }, 500);
      });
    })
    .catch(function(err) {
      clearTimeout(loadingTimeout);
      var msg = (err && err.message ? err.message : 'data betöltése sikertelen.');
      var tip = 'Tipp: nyisd meg a <strong>heatmap-standalone.html</strong> fájlt (adat beágyazva), vagy ellenőrizd, hogy a <strong>data.json</strong> ugyanabban a mappában van-e (pl. 127.0.0.1:5500/data.json).';
      hideLoading('Hiba: ' + msg + '<br><br>' + tip);
      console.error(err);
    });

  window.map = map;
  window.applyFilters = applyFilters;
  window.exportVisible = exportVisible;
  } catch (e) {
    hideLoading('Hiba: ' + (e && e.message ? e.message : String(e)));
    console.error(e);
  }
  }
  if (document.readyState === 'complete') {
    requestAnimationFrame(initMap);
  } else {
    window.addEventListener('load', function() { requestAnimationFrame(initMap); });
  }
})();
  </script>
</body>
</html>
"""

# Beágyazott adat kikapcsolva: a böngésző fetch('data.json')-t használ (Live Server / helyi szerver esetén).
# A pontszám és a városlista beégetve az HTML-be, hogy a tábla azonnal látszódjon.
city_counts = Counter((m.get("city") or "").split(",")[0].strip() or "–" for m in markers)
cities_rows = "".join(
    "<tr><td>{}</td><td>{}</td></tr>".format(html_module.escape(c), n)
    for c, n in city_counts.most_common(50)
)
if len(city_counts) > 50:
    cities_rows += '<tr><td colspan="2"><em>… és még {} hely</em></td></tr>'.format(len(city_counts) - 50)
brand_options = "".join(
    '<option value="{}">'.format(html_module.escape(b))
    for b in sorted(set(m.get("brand") for m in markers if m.get("brand")))
)
html_output = (
    HTML_TEMPLATE.replace("__TOTAL__", str(len(markers)))
    .replace("__CITIES_ROWS__", cities_rows)
    .replace("__BRAND_OPTIONS__", brand_options)
    .replace("%%", "%")
)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_output)

# Iframe-be / SharePoint-ra tölthető verzió: egyetlen fájl, adat beágyazva.
# SharePoint-on a külső scriptek gyakran blokkolva vannak, ezért a CSS/JS beágyazzuk.
STANDALONE_HTML = "heatmap-standalone.html"
data_js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
standalone_content = html_output.replace(
    '  <script src="https://unpkg.com/leaflet',
    '  <script>window.__MAP_DATA__ = ' + data_js + ';</script>\n  <script src="https://unpkg.com/leaflet',
    1
)

# Külső CSS/JS beágyazása (SharePoint / szigorú hálózat esetén csak a térképcache marad külső)
print("Külső CSS/JS letöltése a SharePoint-barát verzióhoz...")
resources = [
    ('https://unpkg.com/leaflet@1.9.3/dist/leaflet.css', '  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />', 'style', False),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css', '  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />', 'style', False),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css', '  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />', 'style', False),
    ('https://unpkg.com/leaflet@1.9.3/dist/leaflet.js', '  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>', 'script', True),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js', '  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>', 'script', True),
    ('https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js', '  <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>', 'script', True),
]
for url, old_tag, tag_name, escape_script in resources:
    content = fetch_url(url)
    if content:
        if escape_script:
            content = content.replace("</script>", "<\\/script>").replace("</style>", "<\\/style>")
        inline = "  <{0}>{1}</{0}>".format(tag_name, content)
        standalone_content = standalone_content.replace(old_tag, inline, 1)
        print(f"  Beágyazva: {url.split('/')[-1]}")
    else:
        print(f"  Kihagyva (CDN elérhetetlen): {url.split('/')[-1]} – a fájl külső linkekkel marad.")

with open(STANDALONE_HTML, "w", encoding="utf-8") as f:
    f.write(standalone_content)

print(f"Heatmap mentve: {OUT_HTML}")
print(f"SharePoint / iframe verzió: {STANDALONE_HTML} (CSS/JS beágyazva, csak a térképkép külső)")
print("Nyisd meg a böngészőben (heatmap.html + data.json ugyanabban a mappában).")