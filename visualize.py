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
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
  <style>
    html, body { height: 100%%; margin: 0; padding: 0; }
    #map { position: absolute; top: 0; left: 0; right: 0; bottom: 0; height: 100vh; min-height: 100vh; width: 100%%; }
    #sidebar {
      position: fixed; top: 10px; left: 10px; width: 280px;
      background: #fff; z-index: 9999;
      box-shadow: 0 2px 8px rgba(0,0,0,.2); border-radius: 6px;
      overflow: hidden;
    }
    #sidebar-header {
      padding: 10px 12px; cursor: pointer; user-select: none;
      font-weight: bold; font-size: 14px; border-bottom: 1px solid #eee;
      display: flex; align-items: center; justify-content: space-between;
    }
    #sidebar-header:hover { background: #f5f5f5; }
    #sidebar-header .toggler { font-size: 12px; color: #666; }
    #sidebar-content { padding: 10px; }
    #sidebar.collapsed #sidebar-content { display: none; }
    #sidebar.collapsed #data-panel { display: none; }
    #sidebar h4 { margin: 0 0 8px 0; }
    #sidebar-content input { width: 100%%; box-sizing: border-box; margin-bottom: 6px; }
    #sidebar-content button { margin-right: 6px; margin-top: 4px; }
    #data-panel {
      max-height: 280px; overflow: auto; padding: 8px; font-size: 12px;
      border-top: 1px solid #eee; background: #fafafa;
    }
    #data-panel table { width: 100%%; border-collapse: collapse; }
    #data-panel th, #data-panel td { text-align: left; padding: 4px 6px; border-bottom: 1px solid #eee; }
    #data-panel th { font-weight: 600; }
    #data-panel .summary-row { font-weight: 600; background: #f0f0f0; }
    #legend {
      position: fixed; bottom: 50px; left: 50px; width: 160px;
      background: #fff; z-index: 9999; padding: 10px; font-size: 13px;
      box-shadow: 0 2px 8px rgba(0,0,0,.2); border-radius: 6px;
    }
    #loading { position: fixed; top: 50%%; left: 50%%; transform: translate(-50%%,-50%%); z-index: 10000;
      background: #fff; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,.2); }
  </style>
</head>
<body>
  <div id="loading">Térkép betöltése...</div>
  <div id="sidebar" style="display:none;">
    <div id="sidebar-header" title="Kattints az összecsukáshoz / kinyitáshoz">
      <span>Szűrők</span>
      <span class="toggler" id="sidebar-toggler">▼</span>
    </div>
    <div id="sidebar-content">
      ZIP: <input type="text" id="zipfilter" placeholder="pl. 8956" />
      Város: <input type="text" id="cityfilter" placeholder="pl. Budapest" />
      <br/>
      <label><input type="checkbox" id="pinsToggle" checked /> Pintek mutatása</label>
      <br/>
      <button type="button" id="btnApply">Alkalmaz</button>
      <button type="button" id="btnExport">Látható exportálása</button>
      <button type="button" id="btnExportIframe" title="Egyetlen HTML fájl letöltése, amit feltölthetsz és iframe-be ágyazhatsz">Export (iframe-be tölthető)</button>
    </div>
    <div id="data-panel">
      <table id="data-table">
        <thead><tr><th>Megjelenített adatok</th><th></th></tr></thead>
        <tbody>
          <tr class="summary-row"><td>Összes pont</td><td id="stat-total">__TOTAL__</td></tr>
          <tr class="summary-row"><td>Megjelenítve</td><td id="stat-visible">__TOTAL__</td></tr>
        </tbody>
      </table>
      <table id="cities-table" style="margin-top:8px;">
        <thead><tr><th>Város / hely</th><th>Db</th></tr></thead>
        <tbody id="cities-tbody">__CITIES_ROWS__</tbody>
      </table>
    </div>
  </div>
  <div id="legend" style="display:none;">
    <b>Jelmagyarázat</b><br/>
    <span style="color:green">●</span> Város<br/>
    <span style="color:blue">●</span> Cím
  </div>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
  <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
  <script>
(function(){
  function hideLoading(errMsg) {
    var el = document.getElementById('loading');
    if (el) {
      el.style.display = 'none';
      if (errMsg) { el.textContent = errMsg; el.style.display = 'block'; el.style.color = '#c00'; }
    }
  }
  function showUI() {
    document.getElementById('loading').style.display = 'none';
    var s = document.getElementById('sidebar'); if (s) s.style.display = 'block';
    var l = document.getElementById('legend'); if (l) l.style.display = 'block';
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
  var filterZip = '', filterCity = '', showPins = true;

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
  fgOverlays.addLayer(cluster);
  overlays['Heatmap - Város'] = heatCity;
  overlays['Heatmap - Cím'] = heatAddr;
  overlays['Pintek'] = fgOverlays;
  L.control.layers(baseLayers, overlays, { collapsed: true }).addTo(map);
  heatCity.addTo(map);
  heatAddr.addTo(map);
  fgOverlays.addTo(map);
  map.invalidateSize();

  function matchFilter(m) {
    if (filterZip && m.zip && m.zip.toString().toLowerCase().indexOf(filterZip) === -1) return false;
    if (filterCity && m.city && m.city.toLowerCase().indexOf(filterCity) === -1) return false;
    return true;
  }

  function applyFilters() {
    filterZip = (document.getElementById('zipfilter').value || '').trim().toLowerCase();
    filterCity = (document.getElementById('cityfilter').value || '').trim().toLowerCase();
    showPins = document.getElementById('pinsToggle').checked;
    for (var i = 0; i < allMarkers.length; i++) {
      var layer = allMarkers[i];
      var m = layer.options && layer.options.data;
      var show = m && matchFilter(m) && showPins;
      layer.setOpacity(show ? 1 : 0);
      layer.setZIndexOffset(show ? 0 : -1000);
      var el = layer._path || (layer._icon);
      if (el) el.style.pointerEvents = show ? '' : 'none';
    }
    updateDataTable();
  }

  function updateDataTable() {
    var total = allMarkers.length;
    var visible = 0;
    var byCity = {};
    for (var i = 0; i < allMarkers.length; i++) {
      var layer = allMarkers[i];
      var m = layer.options && layer.options.data;
      if (layer.getOpacity && layer.getOpacity() === 1 && m) {
        visible++;
        var name = (m.city && m.city.split(',')[0].trim()) || '–';
        byCity[name] = (byCity[name] || 0) + 1;
      }
    }
    var totalEl = document.getElementById('stat-total') || document.querySelector('#data-panel #stat-total');
    var visibleEl = document.getElementById('stat-visible') || document.querySelector('#data-panel #stat-visible');
    if (totalEl) totalEl.textContent = total;
    if (visibleEl) visibleEl.textContent = visible;
    var tbody = document.getElementById('cities-tbody') || document.querySelector('#data-panel #cities-tbody');
    if (tbody) {
      var cities = Object.keys(byCity).sort(function(a,b) { return byCity[b] - byCity[a]; });
      tbody.innerHTML = cities.slice(0, 50).map(function(c) { return '<tr><td>' + c + '</td><td>' + byCity[c] + '</td></tr>'; }).join('');
      if (cities.length > 50) tbody.innerHTML += '<tr><td colspan="2"><em>… és még ' + (cities.length - 50) + ' hely</em></td></tr>';
    }
  }

  function exportVisible() {
    var rows = ['lat,lon,popup'];
    for (var i = 0; i < allMarkers.length; i++) {
      var layer = allMarkers[i];
      if (layer.getOpacity && layer.getOpacity() !== 1) continue;
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

  document.getElementById('btnApply').addEventListener('click', applyFilters);
  document.getElementById('btnExport').addEventListener('click', exportVisible);
  document.getElementById('btnExportIframe').addEventListener('click', function() {
    fetch('heatmap-standalone.html').then(function(r) { return r.text(); }).then(function(html) {
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([html], { type: 'text/html;charset=utf-8' }));
      a.download = 'heatmap-iframe.html';
      a.click();
      URL.revokeObjectURL(a.href);
    }).catch(function() { alert('A heatmap-standalone.html nem található. Futtasd a visualize.py-t.'); });
  });
  document.getElementById('pinsToggle').addEventListener('change', applyFilters);
  document.getElementById('sidebar-header').addEventListener('click', function() {
    var sb = document.getElementById('sidebar');
    var t = document.getElementById('sidebar-toggler');
    sb.classList.toggle('collapsed');
    if (t) t.textContent = sb.classList.contains('collapsed') ? '▶' : '▼';
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
    var self = arguments.callee;
    requestAnimationFrame(function() { self(list, end, done); });
  }

  var dataPromise = window.__MAP_DATA__
    ? Promise.resolve(window.__MAP_DATA__)
    : fetch('data.json').then(function(r) {
        if (!r.ok) throw new Error('data.json nem elérhető (pl. indítsd a Live Server-t a mappában).');
        return r.json();
      });
  dataPromise
    .then(function(d) {
      if (!d) { showUI(); hideLoading('Nincs adat.'); return; }
      requestAnimationFrame(function() {
        heatCity.setLatLngs(d.heat_city || []);
        heatAddr.setLatLngs(d.heat_addr || []);
      });
      var list = d.markers || [];
      addMarkersInChunks(list, 0, function() {
        if (typeof map.invalidateSize === 'function') map.invalidateSize();
        showUI();
        applyFilters();
        setTimeout(updateDataTable, 100);
        setTimeout(updateDataTable, 500);
      });
    })
    .catch(function(err) {
      hideLoading('Hiba: ' + (err && err.message ? err.message : 'data betöltése sikertelen.'));
      console.error(err);
      showUI();
      if (typeof updateDataTable === 'function') setTimeout(updateDataTable, 200);
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
html_output = HTML_TEMPLATE.replace("__TOTAL__", str(len(markers))).replace("__CITIES_ROWS__", cities_rows)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_output)

# Iframe-be / SharePoint-ra tölthető verzió: egyetlen fájl, adat beágyazva.
# SharePoint-on a külső scriptek gyakran blokkolva vannak, ezért a CSS/JS beágyazzuk.
STANDALONE_HTML = "heatmap-standalone.html"
data_js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
standalone_content = html_output.replace(
    '  <script src="https://unpkg.com/leaflet',
    '  <script>window.__MAP_DATA__ = ' + data_js + ';</script>\n  <script src="https://unpkg.com/leaflet'
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
        standalone_content = standalone_content.replace(old_tag, inline)
        print(f"  Beágyazva: {url.split('/')[-1]}")
    else:
        print(f"  Kihagyva (CDN elérhetetlen): {url.split('/')[-1]} – a fájl külső linkekkel marad.")

with open(STANDALONE_HTML, "w", encoding="utf-8") as f:
    f.write(standalone_content)

print(f"Heatmap mentve: {OUT_HTML}")
print(f"SharePoint / iframe verzió: {STANDALONE_HTML} (CSS/JS beágyazva, csak a térképkép külső)")
print("Nyisd meg a böngészőben (heatmap.html + data.json ugyanabban a mappában).")