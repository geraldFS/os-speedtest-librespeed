{# Speedtest reporting page, OPNsense 26.7 MVC. Auth enforced by IndexController/ACL. #}
<script src="{{ cache_safe('/ui/js/chart.umd.min.js') }}"></script>
{# Versioned local asset URL: avoids using legacy 1.2.0 seven-column JavaScript after upgrades. #}
<script src="/ui/js/csvspeedtest_report.js?v=0.5.4-L"></script>
<style>
  .st-report-controls { display:flex; flex-wrap:wrap; gap:12px; align-items:center; padding:12px 0; }
  .st-report-controls .form-control { max-width:200px; display:inline-block; }
  .st-report-chart { position:relative; height:240px; }
  .st-report-chart.compact { height:165px; }
  .st-report-num { font-variant-numeric:tabular-nums; text-align:right; white-space:nowrap; }
  .st-report-table { overflow-x:auto; }
  .st-report-table th { white-space:nowrap; }
  .st-report-actions { display:flex; flex-wrap:wrap; gap:8px; }
  .st-report-info { color:var(--text-muted, #777); }
</style>
<div class="content-box">
  <div class="row">
    <div class="col-md-12">
      <h2>LibreSpeed – Messwertbericht</h2>
      <p class="st-report-info">Datenquelle: /var/log/librespeed.csv · Download/Upload in Mbit/s · Ping/Jitter in ms · Paketverlust nicht verfügbar</p>
      <div class="st-report-actions">
        <a class="btn btn-default" id="st-download" href="/api/csvspeedtest/history/download"><i class="fa fa-download"></i> CSV-Log herunterladen</a>
        <a class="btn btn-default" id="st-provenance" href="/api/csvspeedtest/history/provenance"><i class="fa fa-download"></i> LibreSpeed-CLI-Nachweise herunterladen</a>
        <button class="btn btn-primary" id="st-manual-start" type="button"><i class="fa fa-play"></i> Messung jetzt starten</button>
        <button class="btn btn-default" id="st-refresh" type="button"><i class="fa fa-refresh"></i> Aktualisieren</button>
        <button class="btn btn-danger" id="st-clear" type="button"><i class="fa fa-trash"></i> Logdatei leeren</button>
      </div>
      <p class="st-report-info" id="st-manual-message" role="status" aria-live="polite">Eine manuelle Messung verwendet die zuletzt gespeicherte Serverkonfiguration und beeinflusst den Cronjob nicht.</p>
      <p class="st-report-info" style="margin-top:8px;">Beim Leeren wird die gesamte Logdatei vorher gesichert. Nur Administratoren mit Vollzugriff dürfen den Vorgang ausführen. Der LibreSpeed-Cronjob bleibt aktiv.</p>
      <div id="st-alert" class="alert" style="display:none" role="alert"></div>
      <h3>Messsoftware / Nachvollziehbarkeit</h3>
      <p class="st-report-info">Diese Angaben beziehen sich auf die <strong>aktuell installierte</strong> Software. Die Version historischer Messungen ist nur dokumentiert, wenn sie beim jeweiligen Test in <code>/var/log/librespeed_provenance.csv</code> protokolliert wurde. Bestehende ältere Messungen enthalten diese Information nicht rückwirkend.</p>
      <dl class="dl-horizontal" id="st-cli-info">
        <dt>Messprogramm</dt><dd id="st-cli-name">Wird ermittelt ...</dd>
        <dt>Version (aktuell)</dt><dd id="st-cli-version">–</dd>
        <dt>Programmdatei</dt><dd id="st-cli-path">–</dd>
        <dt>Paketzuordnung</dt><dd id="st-cli-package">–</dd>
        <dt>SHA-256 (aktuell)</dt><dd><code id="st-cli-sha256" style="overflow-wrap:anywhere">–</code></dd>
        <dt>Geprüft am</dt><dd id="st-cli-checked">–</dd>
      </dl>
      <p class="st-report-info">LibreSpeed-Messwerte dienen der technischen Verlaufskontrolle. Dokumentiere Zeitpunkt, gewählten Testserver, eingesetzte CLI-Version und die Original-CSV. Diese Messungen ersetzen kein offizielles Nachweisverfahren bei Vertragsabweichungen.</p>
    </div>
  </div>
  <hr>
  <div class="row">
    <div class="col-md-12" id="st-server-settings">
      <h3>Messserver &amp; Testeinstellungen</h3>
      <p class="st-report-info">Serverliste aus <code>librespeed-cli --list</code>. Maximal drei Server auswählbar. Gespeicherte Einstellungen gelten für manuelle und Cron-Messungen.</p>
      <div class="st-report-controls">
        <label for="st-server-mode">Serverauswahl:</label>
        <select id="st-server-mode" class="form-control">
          <option value="auto">Automatisch (LibreSpeed)</option>
          <option value="selected">Ausgewählte Server</option>
        </select>
        <label for="st-server-execution">Ausführung:</label>
        <select id="st-server-execution" class="form-control">
          <option value="sequential">Nacheinander (vergleichbare Einzelmessungen)</option>
          <option value="parallel">Gleichzeitig (Belastungstest)</option>
        </select>
        <label for="st-concurrent">HTTP-Verbindungen je Server:</label>
        <input id="st-concurrent" class="form-control" type="number" min="1" max="12" value="6" style="width:85px">
        <label for="st-duration">Messdauer je Phase (s):</label>
        <input id="st-duration" class="form-control" type="number" min="5" max="60" value="20" style="width:85px">
      </div>
      <p class="st-report-info">Gleichzeitige Tests teilen sich dieselbe Leitung und liefern keine unabhängig vergleichbaren Maximalwerte. Für Bandbreitenvergleiche ist „Nacheinander“ empfohlen.</p>
      <div class="st-report-controls">
        <label for="st-server-filter">Server suchen:</label>
        <input id="st-server-filter" class="form-control" type="search" placeholder="Standort, Anbieter oder ID" style="max-width:300px">
        <button id="st-servers-reload" class="btn btn-default" type="button"><i class="fa fa-refresh"></i> Serverliste aktualisieren</button>
        <span id="st-servers-count" class="st-report-info" role="status">Serverliste wird geladen ...</span>
      </div>
      <div class="st-report-table" style="max-height:270px;overflow:auto">
        <table id="st-servers-table" class="table table-condensed table-striped">
          <thead><tr><th>Auswahl</th><th>ID</th><th>Standort / Anbieter</th><th>Server-URL</th></tr></thead>
          <tbody><tr><td colspan="4">Serverliste wird geladen ...</td></tr></tbody>
        </table>
      </div>
      <div class="st-report-controls">
        <span id="st-servers-selected">0 von 3 ausgewählt</span>
        <button type="button" class="btn btn-primary" id="st-servers-save">Einstellungen speichern</button>
        <span id="st-servers-message" class="st-report-info" role="status"></span>
      </div>
    </div>
  </div>
  <hr>
  <div class="row">
    <div class="col-md-12">
      <h3>Messwerte als Tabelle</h3>
      <div class="st-report-controls">
        <label for="st-period">Zeitraum:</label>
        <select id="st-period" class="form-control">
          <option value="24h">Letzte 24 Stunden</option>
          <option value="7d">Letzte 7 Tage</option>
          <option value="all">Gesamte Logdatei</option>
        </select>
        <label for="st-page-size">Zeilen pro Seite:</label>
        <select id="st-page-size" class="form-control">
          <option value="25">25</option>
          <option value="50" selected>50</option>
          <option value="100">100</option>
          <option value="200">200</option>
        </select>
        <span id="st-table-status" class="st-report-info" role="status">Daten werden geladen ...</span>
      </div>
      <div class="st-report-table">
        <table class="table table-condensed table-striped table-hover" id="st-table">
          <thead>
            <tr>
              <th>Datum / Uhrzeit</th><th>Server</th>
              <th class="st-report-num">Download (Mbit/s)</th><th class="st-report-num">Upload (Mbit/s)</th>
              <th class="st-report-num">Ping (ms)</th><th class="st-report-num">Jitter (ms)</th>
              
            </tr>
          </thead>
          <tbody><tr><td colspan="6">Messwerte werden geladen ...</td></tr></tbody>
        </table>
      </div>
      <div class="st-report-controls">
        <button class="btn btn-default" id="st-prev" type="button">Vorherige Seite</button>
        <span id="st-page-info">Seite 1</span>
        <button class="btn btn-default" id="st-next" type="button">Nächste Seite</button>
      </div>
    </div>
  </div>
  <hr>
  <div class="row">
    <div class="col-md-12">
      <h3>LibreSpeed-Verlauf – wie im Dashboard</h3>
      <div class="st-report-controls">
        <label for="st-chart-period">Diagrammzeitraum:</label>
        <select id="st-chart-period" class="form-control">
          <option value="24">24 Stunden</option><option value="168">7 Tage</option><option value="720">30 Tage</option>
        </select>
        <span id="st-chart-status" class="st-report-info" role="status">Diagramme werden geladen ...</span>
      </div>
      <h4>Download / Upload (Mbit/s)</h4>
      <div class="st-report-chart"><canvas id="st-chart-speed"></canvas></div>
      <h4>Ping / Jitter (ms)</h4>
      <div class="st-report-chart compact"><canvas id="st-chart-latency"></canvas></div>
      <p class="st-report-info">Paketverlust wird vom verwendeten LibreSpeed-CLI nicht ermittelt.</p>
    </div>
  </div>
</div>
