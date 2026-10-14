"""
Agentic AI Travel Intelligence Platform - Web Server & Interactive Dashboard
Runs a lightweight, zero-dependency Python HTTP server with live REST API endpoints
and an interactive glassmorphic web dashboard for executing the verified multi-source travel engine.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from dotenv import load_dotenv
from engine import AgenticTravelEngine

load_dotenv()

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
      padding: 16px 32px;
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
    .container {
      max-width: 1460px;
      margin: 0 auto;
      padding: 24px 20px;
      width: 100%;
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 22px;
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
    .btn-primary {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 12px 16px;
      font-size: 0.95rem;
      font-weight: 600;
      width: 100%;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, #1d4ed8, #1e40af);
      transform: translateY(-1px);
    }
    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
    .btn-sm {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--border);
      color: #94a3b8;
      border-radius: 4px;
      padding: 3px 8px;
      font-size: 0.72rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-sm:hover {
      background: rgba(255, 255, 255, 0.16);
      color: #fff;
    }
    .pulse-ready {
      animation: pulse-glow 1.5s infinite;
    }
    @keyframes pulse-glow {
      0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.5); }
      70% { box-shadow: 0 0 0 8px rgba(37, 99, 235, 0); }
      100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
    }
    .btn-download {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--border);
      color: #fff;
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: all 0.2s;
    }
    .btn-download:hover {
      background: rgba(255, 255, 255, 0.15);
      border-color: rgba(255, 255, 255, 0.2);
    }
    .tab-bar {
      display: flex;
      gap: 6px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 18px;
      overflow-x: auto;
      padding-bottom: 6px;
    }
    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 500;
      padding: 8px 12px;
      border-radius: 6px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }
    .tab-btn:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.04);
    }
    .tab-btn.active {
      color: #60a5fa;
      background: rgba(37, 99, 235, 0.15);
      font-weight: 600;
    }
    .table-container {
      overflow-x: auto;
      max-height: 580px;
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      text-align: left;
    }
    th {
      background: #0b1329;
      color: #cbd5e1;
      font-weight: 600;
      padding: 10px 14px;
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
    }
    td {
      padding: 9px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: #e2e8f0;
      white-space: nowrap;
    }
    tr:nth-child(even) td {
      background: rgba(255, 255, 255, 0.015);
    }
    tr:hover td {
      background: rgba(37, 99, 235, 0.06);
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
      grid-template-columns: repeat(3, 1fr);
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
    .pill-link {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 3px 7px;
      border-radius: 5px;
      font-size: 0.72rem;
      font-weight: 500;
      text-decoration: none;
      margin-right: 4px;
      transition: all 0.15s;
    }
    .pill-g-hotels { background: rgba(66, 133, 244, 0.15); color: #93c5fd; border: 1px solid rgba(66, 133, 244, 0.3); }
    .pill-g-hotels:hover { background: rgba(66, 133, 244, 0.3); }
    .pill-g-maps { background: rgba(52, 168, 83, 0.15); color: #86efac; border: 1px solid rgba(52, 168, 83, 0.3); }
    .pill-g-maps:hover { background: rgba(52, 168, 83, 0.3); }
    .pill-booking { background: rgba(0, 53, 128, 0.4); color: #60a5fa; border: 1px solid rgba(0, 53, 128, 0.6); }
    .pill-booking:hover { background: rgba(0, 53, 128, 0.7); }
    .pill-expedia { background: rgba(254, 187, 2, 0.15); color: #fde047; border: 1px solid rgba(254, 187, 2, 0.3); }
    .pill-expedia:hover { background: rgba(254, 187, 2, 0.3); }
    .pill-wyndham { background: rgba(225, 29, 72, 0.15); color: #fda4af; border: 1px solid rgba(225, 29, 72, 0.3); }
    .pill-wyndham:hover { background: rgba(225, 29, 72, 0.3); }
    .badge-avail {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
    }
  </style>
</head>
<body>

<header>
  <div class="logo">
    <span style="font-size: 1.5rem;">✈️</span>
    <div>
      <div>Agentic AI Travel Intelligence Platform</div>
      <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 400;">Multi-Source Transit & Hotel Intelligence Platform</div>
    </div>
  </div>
  <div style="display: flex; gap: 12px; align-items: center;">
    <a href="/api/download-n8n-workflow" class="btn-download" style="border-color: rgba(99, 102, 241, 0.4); background: rgba(99, 102, 241, 0.15); color: #a5b4fc;">
      <span>⚡</span> Download n8n Workflow (.json)
    </a>
    <a href="/api/download-excel" class="btn-download">
      <span>📥</span> Download Master Excel (.xlsx)
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
        <input type="number" id="budgetMin" value="50" min="20" max="300" placeholder="Min $">
        <input type="number" id="budgetMax" value="60" min="20" max="350" placeholder="Max $">
      </div>
    </div>

    <div class="control-group">
      <label>Max Commute Threshold (Minutes)</label>
      <input type="number" id="maxCommute" value="90" min="15" max="180">
    </div>

    <div class="control-group">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <label style="margin: 0;">Target Metropolitan Markets</label>
        <div style="display: flex; gap: 4px;">
          <button type="button" class="btn-sm" onclick="selectAllCities(true)">Select All</button>
          <button type="button" class="btn-sm" onclick="selectAllCities(false)">Deselect All</button>
        </div>
      </div>
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
      <div style="margin-top: 8px;">
        <label for="customCityInput" style="font-size: 0.75rem;">Or Enter Custom City / Destination (Worldwide):</label>
        <input type="text" id="customCityInput" placeholder="e.g. Seattle, Denver, London, Toronto" style="width: 100%; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; color: #fff; font-size: 0.85rem; outline: none;">
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
        <div class="metric-val" id="metricCorridors">88</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Verified Budget Matches</div>
        <div class="metric-val" style="color: #34d399;" id="metricBudget">0 Hotels</div>
      </div>
    </div>

    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('final_output', this)">⭐ Sheet 6: Final Recommendations</button>
      <button class="tab-btn" onclick="switchTab('scores', this)">📊 Sheet 5: Recommendation Scores</button>
      <button class="tab-btn" onclick="switchTab('transit', this)">🚆 Sheet 2: Transit Connectivity</button>
      <button class="tab-btn" onclick="switchTab('accommodations', this)">🏨 Sheet 3: Verified Accommodations</button>
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
let activeAbortController = null;

async function executeEngine() {
  if (activeAbortController) {
    activeAbortController.abort();
  }
  activeAbortController = new AbortController();

  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.classList.remove('pulse-ready');
  btn.innerHTML = '<span>⏳</span> Querying Intelligence APIs...';

  const budgetMin = parseFloat(document.getElementById('budgetMin').value) || 50;
  const budgetMax = parseFloat(document.getElementById('budgetMax').value) || 60;
  const maxCommute = parseInt(document.getElementById('maxCommute').value) || 90;
  let cityChecks = Array.from(document.querySelectorAll('input[name="city"]:checked')).map(cb => cb.value);
  const customCity = (document.getElementById('customCityInput').value || '').trim();
  if (customCity) {
    const customList = customCity.split(',').map(c => c.trim()).filter(c => c.length > 0);
    cityChecks = customList.concat(cityChecks);
  }

  if (cityChecks.length === 0) {
    alert('Please select at least one metropolitan market or enter a custom destination.');
    btn.disabled = false;
    btn.innerHTML = '<span>🚀</span> Run Autonomous Agents';
    return;
  }

  try {
    const res = await fetch('/api/run-pipeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: activeAbortController.signal,
      body: JSON.stringify({
        budget_min: budgetMin,
        budget_max: budgetMax,
        max_commute_minutes: maxCommute,
        cities: cityChecks
      })
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || 'Server error ' + res.status);
    }
    const result = await res.json();
    currentData = result.data;
    renderMetrics(result);
    renderLogs(result.logs || []);
    renderTable(activeTabName);
  } catch (err) {
    if (err.name !== 'AbortError') {
      alert('Simulation error: ' + err.message);
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>🚀</span> Run Autonomous Agents';
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
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
  const matchCount = res.accommodations_count !== undefined ? res.accommodations_count : 0;
  document.getElementById('metricBudget').innerText = `${matchCount} Hotels`;
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
    container.innerHTML = '<div style="padding: 50px 20px; text-align: center; color: #f87171; font-weight: 600; font-size: 1.05rem; background: rgba(239, 68, 68, 0.06); border: 1px dashed rgba(239, 68, 68, 0.3); border-radius: 12px; margin: 20px;">⚠️ No hotels found within your selected budget</div>';
    return;
  }

  let html = '<table><thead><tr>';
  if (tabKey === 'final_output') {
    html += '<th>City</th><th>Downtown</th><th>Locality & Station</th><th>Commute</th><th>Hotel</th><th>Nightly Rate</th><th>Taxes & Fees</th><th>Total Booking</th><th>Availability</th><th>Multi-Source Direct Links</th><th>Safety</th><th>Score</th><th>Recommendation Summary</th></tr></thead><tbody>';
    items.forEach(r => {
      const isTop = r.recommendation.includes('#1');
      html += `<tr style="${isTop ? 'background: rgba(16, 185, 129, 0.08); font-weight: 500;' : ''}">
        <td><strong>${r.city}</strong></td>
        <td>${r.downtown}</td>
        <td><span style="color: #60a5fa; font-weight: 600;">${r.recommended_locality}</span> (${r.station})</td>
        <td>${r.commute_time}</td>
        <td>${r.hotel}</td>
        <td style="color: #34d399; font-weight: 700;">$${r.rate.toFixed(2)}</td>
        <td>$${(r.taxes_and_fees || 0).toFixed(2)}</td>
        <td style="color: #fbbf24; font-weight: 700;">$${(r.total_booking || 0).toFixed(2)}</td>
        <td><span class="badge-avail">${r.availability_status || 'Available'}</span></td>
        <td>
          <a href="${r.google_hotels_url}" target="_blank" class="pill-link pill-g-hotels">🏨 Google Hotels</a>
          <a href="${r.google_maps_url}" target="_blank" class="pill-link pill-g-maps">📍 Google Maps</a>
          <a href="${r.booking_demand_api_url}" target="_blank" class="pill-link pill-booking">🛎️ Booking.com</a>
          <a href="${r.expedia_rapid_api_url}" target="_blank" class="pill-link pill-expedia">✈️ Expedia</a>
          <a href="${r.wyndham_official_url}" target="_blank" class="pill-link pill-wyndham">🏢 Wyndham</a>
        </td>
        <td>${r.safety.toFixed(0)}</td>
        <td style="color: #38bdf8; font-weight: 700;">${r.overall_score.toFixed(2)}</td>
        <td style="font-size: 0.78rem; color: #cbd5e1; max-width: 320px; overflow: hidden; text-overflow: ellipsis;">${r.recommendation}</td>
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
    html += '<th>City</th><th>Downtown</th><th>Suburb</th><th>Transit Authority</th><th>Mode</th><th>Station</th><th>Commute (Mins)</th><th>Transfers</th><th>Fare (USD)</th><th>Station Map</th></tr></thead><tbody>';
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
        <td><a href="${r.google_maps_station_url || '#'}" target="_blank" class="pill-link pill-g-maps">📍 Station on Maps</a></td>
      </tr>`;
    });
  } else if (tabKey === 'accommodations') {
    html += '<th>City</th><th>Locality</th><th>Hotel Name</th><th>Address</th><th>Base Rate</th><th>Taxes & Fees</th><th>Total Booking</th><th>Availability</th><th>Multi-Source Verification Links</th><th>Primary Source</th><th>Rating</th><th>Dist to Station</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><strong>${r.city}</strong></td>
        <td>${r.locality}</td>
        <td><strong>${r.hotel_name}</strong></td>
        <td style="font-size: 0.78rem;">${r.address}</td>
        <td style="color: #34d399; font-weight: 700;">$${r.base_nightly_rate_usd.toFixed(2)}</td>
        <td>$${r.taxes_and_fees_usd.toFixed(2)}</td>
        <td style="color: #fbbf24; font-weight: 700;">$${r.total_booking_usd.toFixed(2)}</td>
        <td><span class="badge-avail">${r.availability_status}</span></td>
        <td>
          <a href="${r.google_hotels_url}" target="_blank" class="pill-link pill-g-hotels">🏨 Google Hotels</a>
          <a href="${r.google_maps_url}" target="_blank" class="pill-link pill-g-maps">📍 Google Maps</a>
          <a href="${r.booking_demand_api_url}" target="_blank" class="pill-link pill-booking">🛎️ Booking</a>
          <a href="${r.expedia_rapid_api_url}" target="_blank" class="pill-link pill-expedia">✈️ Expedia</a>
          <a href="${r.wyndham_official_url}" target="_blank" class="pill-link pill-wyndham">🏢 Wyndham</a>
        </td>
        <td style="font-size: 0.75rem; color: #94a3b8;">${r.price_source}</td>
        <td>⭐ ${r.rating.toFixed(1)} (${r.review_count})</td>
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
    html += '<th>City ID</th><th>City</th><th>State</th><th>Downtown District / CBD</th><th>Primary Transit Network</th><th>District Map</th><th>Last Sync</th></tr></thead><tbody>';
    items.forEach(r => {
      html += `<tr>
        <td><code>${r.city_id}</code></td>
        <td><strong>${r.city}</strong></td>
        <td>${r.state}</td>
        <td>${r.downtown_district}</td>
        <td>${r.primary_transit_system}</td>
        <td><a href="${r.google_maps_district_url || '#'}" target="_blank" class="pill-link pill-g-maps">📍 Google Maps CBD</a></td>
        <td style="font-size: 0.75rem; color: #94a3b8;">${r.last_updated}</td>
      </tr>`;
    });
  }

  html += '</tbody></table>';
  container.innerHTML = html;
}

// Quick selection helper for cities
function selectAllCities(checked) {
  document.querySelectorAll('input[name="city"]').forEach(cb => {
    cb.checked = checked;
  });
  onFilterChange();
}

// Auto-enable Run button and attach change listeners to all filter inputs
function onFilterChange() {
  if (activeAbortController) {
    activeAbortController.abort();
    activeAbortController = null;
  }
  const btn = document.getElementById('runBtn');
  if (btn) {
    btn.disabled = false;
    btn.innerHTML = '<span>🚀</span> Run Autonomous Agents';
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
    btn.classList.add('pulse-ready');
  }
}

// Initial Load & Event Listener Binding
window.onload = () => {
  // Bind input, change, and keyup events to budgetMin, budgetMax, maxCommute
  ['budgetMin', 'budgetMax', 'maxCommute'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', onFilterChange);
      el.addEventListener('change', onFilterChange);
      el.addEventListener('keyup', onFilterChange);
    }
  });

  // Bind change and click events to all city checkboxes
  document.querySelectorAll('input[name="city"]').forEach(cb => {
    cb.addEventListener('change', onFilterChange);
    cb.addEventListener('click', onFilterChange);
  });

  // Run initial pipeline
  executeEngine();
};
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

        elif parsed.path == "/api/download-n8n-workflow":
            workflow_path = os.path.join(DIRECTORY, "n8n_travel_intelligence_workflow.json")
            if os.path.exists(workflow_path):
                with open(workflow_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="n8n_travel_intelligence_workflow.json"')
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Workflow file not found")
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

            budget_min = float(params.get("budget_min", 50.0))
            budget_max = float(params.get("budget_max", 60.0))
            max_commute = int(params.get("max_commute_minutes", 90))
            cities = params.get("cities") or None

            excel_path = os.path.join(DIRECTORY, "Travel_Intelligence_Master_Workbook.xlsx")
            
            try:
                engine = AgenticTravelEngine(
                    target_cities=cities,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    max_commute_minutes=max_commute
                )
                result = engine.run(output_excel_path=excel_path)

                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ERROR", "message": str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), TravelEngineHTTPHandler) as httpd:
        print(f"[SERVER] AI Travel Intelligence Platform Web Server listening on http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
