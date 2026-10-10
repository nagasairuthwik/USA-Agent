"""
Agentic AI Travel Intelligence Platform - Web Server & Interactive Dashboard
Runs a lightweight, zero-dependency Python HTTP server with live REST API endpoints
and a modern glassmorphic web dashboard for executing the multi-agent travel engine.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from engine import AgenticTravelEngine

PORT = 8088
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agentic AI Travel Intelligence Platform</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --navy: #0f172a;
      --navy-card: #1e293b;
      --accent: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --border: rgba(255, 255, 255, 0.08);
      --card-bg: rgba(30, 41, 59, 0.7);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body {
      background: radial-gradient(circle at 10% 20%, #0f172a 0%, #020617 90%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 18px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 1.25rem;
      font-weight: 700;
      color: #fff;
    }
    .badge-live {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.05em;
    }
    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 28px 24px;
      width: 100%;
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 24px;
    }
    .card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }
    h2 {
      font-size: 1.05rem;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #f1f5f9;
    }
    .control-group {
      margin-bottom: 18px;
    }
    label {
      display: block;
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    input[type="number"], select {
      width: 100%;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      color: #fff;
      font-size: 0.9rem;
      outline: none;
      transition: all 0.2s;
    }
    input[type="number"]:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
    }
    .cities-checkbox-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      max-height: 170px;
      overflow-y: auto;
      background: rgba(15, 23, 42, 0.6);
      padding: 10px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }
    .city-check {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: #cbd5e1;
      cursor: pointer;
    }
    .slider-row {
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .btn-primary {
      width: 100%;
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #fff;
      border: none;
      border-radius: 10px;
      padding: 13px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35);
      transition: all 0.2s;
    }
    .btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
    }
    .btn-download {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      border: none;
      border-radius: 10px;
      padding: 11px 20px;
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
      transition: all 0.2s;
    }
    .btn-download:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
    .tab-bar {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
      margin-bottom: 16px;
      overflow-x: auto;
    }
    .tab-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
    }
    .tab-btn.active {
      background: rgba(37, 99, 235, 0.15);
      color: #60a5fa;
      border-color: rgba(37, 99, 235, 0.3);
      font-weight: 600;
    }
    .table-container {
      overflow-x: auto;
      max-height: 520px;
      border-radius: 10px;
      border: 1px solid var(--border);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
      text-align: left;
    }
    th {
      background: #0f172a;
      color: #94a3b8;
      font-weight: 600;
      padding: 11px 14px;
      position: sticky;
      top: 0;
      border-bottom: 1px solid var(--border);
    }
    td {
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: #e2e8f0;
    }
    tr:hover td {
      background: rgba(255, 255, 255, 0.03);
    }
    .rank-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.75rem;
    }
    .rank-1 { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .rank-2 { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .rank-3 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .log-box {
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.78rem;
      color: #38bdf8;
      max-height: 180px;
      overflow-y: auto;
      margin-top: 16px;
    }
    .log-item { margin-bottom: 4px; line-height: 1.4; }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 20px;
    }
    .metric-card {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 14px;
    }
    .metric-title { font-size: 0.75rem; color: var(--text-muted); }
    .metric-val { font-size: 1.35rem; font-weight: 700; color: #fff; margin-top: 2px; }
  </style>
</head>
<body>

<header>
  <div class="logo">
    <span style="font-size: 1.5rem;">✈️</span>
    <div>
      <div>Agentic AI Travel Intelligence Platform</div>
      <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 400;">Autonomous Multi-Agent Transit, Safety & Budget Engine</div>
    </div>
  </div>
  <div style="display: flex; gap: 12px; align-items: center;">
    <span class="badge-live">⚡ Multi-Agent Active</span>
    <a href="/api/download-excel" class="btn-download">
      <span>📥</span> Download Excel (.xlsx)
    </a>
  </div>
</header>

<div class="container">
  <!-- LEFT PANEL: CONTROLS & AGENT SETTINGS -->
  <div class="card">
    <h2><span>⚙️</span> Engine Parameters</h2>
    
    <div class="control-group">
      <label>Target Budget Range (USD)</label>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <input type="number" id="budgetMin" value="50" min="20" max="200" placeholder="Min $">
        <input type="number" id="budgetMax" value="60" min="30" max="300" placeholder="Max $">
      </div>
    </div>

    <div class="control-group">
      <label>Max Commute Threshold (Minutes)</label>
      <input type="number" id="maxCommute" value="90" min="15" max="180">
    </div>

    <div class="control-group">
      <label>Target Metropolitan Markets</label>
      <div class="cities-checkbox-grid">
        <label class="city-check"><input type="checkbox" name="city" value="New York" checked> New York</label>
        <label class="city-check"><input type="checkbox" name="city" value="New Jersey" checked> New Jersey</label>
        <label class="city-check"><input type="checkbox" name="city" value="Washington" checked> Washington DC</label>
        <label class="city-check"><input type="checkbox" name="city" value="Philadelphia" checked> Philadelphia</label>
        <label class="city-check"><input type="checkbox" name="city" value="Boston" checked> Boston</label>
        <label class="city-check"><input type="checkbox" name="city" value="Chicago" checked> Chicago</label>
        <label class="city-check"><input type="checkbox" name="city" value="Dallas" checked> Dallas</label>
        <label class="city-check"><input type="checkbox" name="city" value="Miami" checked> Miami</label>
        <label class="city-check"><input type="checkbox" name="city" value="San Francisco" checked> San Francisco</label>
        <label class="city-check"><input type="checkbox" name="city" value="San Antonio" checked> San Antonio</label>
        <label class="city-check"><input type="checkbox" name="city" value="San Jose" checked> San Jose</label>
      </div>
    </div>

    <button class="btn-primary" id="runBtn" onclick="executeEngine()">
      <span>🚀</span> Run Autonomous Agents
    </button>

    <h2 style="margin-top: 24px;"><span>🤖</span> Agent Reasoning Feed</h2>
    <div class="log-box" id="logBox">
      <div class="log-item">[Ready] Click 'Run Autonomous Agents' to execute multi-agent loop...</div>
    </div>
  </div>

  <!-- RIGHT PANEL: INTERACTIVE RESULTS & TAB VIEW -->
  <div class="card">
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-title">Cities Analyzed</div>
        <div class="metric-val" id="metricCities">11</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Transit Corridors</div>
        <div class="metric-val" id="metricCorridors">55</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Budget Matches ($50-$60)</div>
        <div class="metric-val" style="color: #34d399;" id="metricBudget">55/55</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Validation Status</div>
        <div class="metric-val" style="color: #38bdf8;" id="metricValidation">PASS</div>
      </div>
    </div>

    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('final_output', this)">⭐ Sheet 6: Final Recommendations</button>
      <button class="tab-btn" onclick="switchTab('scores', this)">📊 Sheet 5: Recommendation Scores</button>
      <button class="tab-btn" onclick="switchTab('transit', this)">🚆 Sheet 2: Transit Connectivity</button>
      <button class="tab-btn" onclick="switchTab('accommodations', this)">🏨 Sheet 3: Accommodations ($50-$60)</button>
      <button class="tab-btn" onclick="switchTab('safety', this)">🛡️ Sheet 4: Safety & Crime Index</button>
      <button class="tab-btn" onclick="switchTab('cities', this)">🏙️ Sheet 1: City Master</button>
    </div>

    <div class="table-container" id="tableContainer">
      <div style="padding: 40px; text-align: center; color: var(--text-muted);">
        Loading intelligence data...
      </div>
    </div>
  </div>
</div>

<script>
let currentData = null;
let activeTabName = 'final_output';

async function executeEngine() {
  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.innerHTML = '<span>⏳</span> Agents Working...';

  const budgetMin = parseFloat(document.getElementById('budgetMin').value) || 50;
  const budgetMax = parseFloat(document.getElementById('budgetMax').value) || 60;
  const maxCommute = parseInt(document.getElementById('maxCommute').value) || 90;
  const cityChecks = Array.from(document.querySelectorAll('input[name="city"]:checked')).map(cb => cb.value);

  try {
    const res = await fetch('/api/run-pipeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        budget_min: budgetMin,
        budget_max: budgetMax,
        max_commute_minutes: maxCommute,
        cities: cityChecks
      })
    });
    const result = await res.json();
    currentData = result.data;
    renderMetrics(result);
    renderLogs(result.logs);
    renderTable(activeTabName);
  } catch (err) {
    alert('Failed to execute engine: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>🚀</span> Run Autonomous Agents';
  }
}

function renderLogs(logs) {
  const box = document.getElementById('logBox');
  box.innerHTML = logs.map(l => `<div class="log-item"><span style="color:#64748b;">[${l.timestamp}]</span> <strong style="color:#a855f7;">[${l.agent}]</strong> ${l.message}</div>`).join('');
  box.scrollTop = box.scrollHeight;
}

function renderMetrics(res) {
  document.getElementById('metricCities').innerText = res.cities_count || 11;
  document.getElementById('metricCorridors').innerText = res.transit_corridors || 55;
  document.getElementById('metricBudget').innerText = res.validation ? res.validation.budget_compliance : '55/55';
  document.getElementById('metricValidation').innerText = res.validation ? res.validation.status : 'PASS';
}

function switchTab(tabKey, btnElem) {
  activeTabName = tabKey;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  if (btnElem) btnElem.classList.add('active');
  renderTable(tabKey);
}

function renderTable(tabKey) {
  if (!currentData) return;
  const container = document.getElementById('tableContainer');
  const items = currentData[tabKey] || [];

  if (items.length === 0) {
    container.innerHTML = '<div style="padding: 30px; text-align: center; color: #94a3b8;">No records matched your search filters.</div>';
    return;
  }

  let html = '<table><thead><tr>';
  if (tabKey === 'final_output') {
    html += '<th>City</th><th>Downtown</th><th>Recommended Locality</th><th>Transit & Station</th><th>Commute</th><th>Hotel</th><th>Nightly Rate</th><th>Safety</th><th>Score</th><th>Recommendation Summary</th></tr></thead><tbody>';
    items.forEach(r => {
      const isTop = r.recommendation.includes('#1');
      html += `<tr style="${isTop ? 'background: rgba(16, 185, 129, 0.08); font-weight: 500;' : ''}">
        <td><strong>${r.city}</strong></td>
        <td>${r.downtown}</td>
        <td><span style="color: #60a5fa; font-weight: 600;">${r.recommended_locality}</span></td>
        <td>${r.transit_system} (${r.station})</td>
        <td>${r.commute_time}</td>
        <td>${r.hotel}</td>
        <td style="color: #34d399; font-weight: 600;">$${r.rate.toFixed(0)}</td>
        <td>${r.safety.toFixed(0)}</td>
        <td style="color: #38bdf8; font-weight: 700;">${r.overall_score.toFixed(2)}</td>
        <td style="font-size: 0.78rem; color: #cbd5e1;">${r.recommendation}</td>
      </tr>`;
    });
  } else if (tabKey === 'scores') {
    html += '<th>Rank</th><th>City</th><th>Locality</th><th>Safety Score</th><th>Cost Score</th><th>Commute Score</th><th>Transit Score</th><th>Overall Score</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><span class="rank-badge rank-${r.rank}">${r.rank}</span></td>
        <td><strong>${r.city}</strong></td>
        <td>${r.locality}</td>
        <td>${r.safety_score.toFixed(1)}</td>
        <td>${r.cost_score.toFixed(1)}</td>
        <td>${r.commute_score.toFixed(1)}</td>
        <td>${r.transit_score.toFixed(1)}</td>
        <td style="color: #34d399; font-weight: 700;">${r.overall_score.toFixed(2)}</td>
      </tr>`;
    });
  } else if (tabKey === 'transit') {
    html += '<th>City</th><th>Downtown</th><th>Suburb</th><th>Transit Authority</th><th>Mode</th><th>Station</th><th>Commute (Mins)</th><th>Transfers</th><th>Fare (USD)</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><strong>${r.city}</strong></td>
        <td>${r.downtown}</td>
        <td>${r.suburb}</td>
        <td>${r.transit_system}</td>
        <td>${r.transit_mode}</td>
        <td>${r.nearest_station}</td>
        <td><strong>${r.commute_minutes}m</strong></td>
        <td>${r.transfers}</td>
        <td>$${r.fare_usd.toFixed(2)}</td>
      </tr>`;
    });
  } else if (tabKey === 'accommodations') {
    html += '<th>City</th><th>Locality</th><th>Hotel Name</th><th>Address</th><th>Nightly Rate</th><th>Rating</th><th>Reviews</th><th>Dist to Station</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><strong>${r.city}</strong></td>
        <td>${r.locality}</td>
        <td><strong>${r.hotel_name}</strong></td>
        <td style="font-size: 0.78rem;">${r.address}</td>
        <td style="color: #34d399; font-weight: 700;">$${r.nightly_rate_usd.toFixed(0)}</td>
        <td>⭐ ${r.rating.toFixed(1)}</td>
        <td>${r.review_count}</td>
        <td>${r.distance_to_station_miles} mi</td>
      </tr>`;
    });
  } else if (tabKey === 'safety') {
    html += '<th>City</th><th>Locality</th><th>Safety Score (1-100)</th><th>Crime Index</th><th>Walkability</th><th>Neighborhood Category</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><strong>${r.city}</strong></td>
        <td>${r.locality}</td>
        <td style="color: #34d399; font-weight: 700;">${r.safety_score.toFixed(0)} / 100</td>
        <td>${r.crime_index.toFixed(1)}</td>
        <td>${r.walkability} / 100</td>
        <td><span style="background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem;">${r.category}</span></td>
      </tr>`;
    });
  } else if (tabKey === 'cities') {
    html += '<th>City ID</th><th>City</th><th>State</th><th>Downtown District / CBD</th><th>Primary Transit Network</th><th>Coordinates</th><th>Last Sync</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><code>${r.city_id}</code></td>
        <td><strong>${r.city}</strong></td>
        <td>${r.state}</td>
        <td>${r.downtown_district}</td>
        <td>${r.primary_transit_system}</td>
        <td style="font-size: 0.78rem;">${r.latitude.toFixed(4)}, ${r.longitude.toFixed(4)}</td>
        <td style="font-size: 0.75rem; color: #94a3b8;">${r.last_updated}</td>
      </tr>`;
    });
  }

  html += '</tbody></table>';
  container.innerHTML = html;
}

// Initial Load
window.onload = () => executeEngine();
</script>

</body>
</html>
"""

class TravelEngineHTTPHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode('utf-8'))
            return
            
        elif parsed.path == "/api/download-excel":
            excel_path = os.path.join(DIRECTORY, "Travel_Intelligence_Master_Workbook.xlsx")
            if not os.path.exists(excel_path):
                engine = AgenticTravelEngine()
                engine.run(excel_path)
            
            with open(excel_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            self.send_header("Content-Disposition", 'attachment; filename="Travel_Intelligence_Master_Workbook.xlsx"')
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
            
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/run-pipeline":
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            try:
                params = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {str(e)}"}).encode('utf-8'))
                return
            
            budget_min = float(params.get('budget_min', 50.0))
            budget_max = float(params.get('budget_max', 60.0))
            max_commute = int(params.get('max_commute_minutes', 90))
            cities = params.get('cities', None)
            
            engine = AgenticTravelEngine(
                target_cities=cities,
                budget_min=budget_min,
                budget_max=budget_max,
                max_commute_minutes=max_commute
            )
            excel_path = os.path.join(DIRECTORY, "Travel_Intelligence_Master_Workbook.xlsx")
            result = engine.run(excel_path)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            return

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), TravelEngineHTTPHandler) as httpd:
        print("=" * 75)
        print(f"[+] Agentic AI Travel Intelligence Engine Server Running!")
        print(f"[+] Web Dashboard URL: http://localhost:{PORT}")
        print("=" * 75)
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()

