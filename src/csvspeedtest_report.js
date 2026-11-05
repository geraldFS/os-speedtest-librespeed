/* OPNsense LibreSpeed Reporting page, no third-party CDN or JavaScript dependencies. */
(function ($) {
    'use strict';
    // Useful when diagnosing cached scripts; read in the browser console.
    window.OPNsenseSpeedtestReportVersion = '0.5.4-L';
    $(function () {
        const API = '/api/csvspeedtest/history';
        const state = { period: '24h', page: 1, pageSize: 50, total: 0, points: [], charts: [] };
        const $body = $('#st-table tbody');
        // Rebuild headings from the exact data fields rendered below.
        // OPNsense may still serve a compiled Volt view from older releases,
        // whose extra Ookla columns would otherwise mislabel LibreSpeed values.
        const columns = [
            'Datum / Uhrzeit', 'Server', 'Download (Mbit/s)',
            'Upload (Mbit/s)', 'Ping (ms)', 'Jitter (ms)'
        ];
        const $header = $('<tr>');
        columns.forEach((name, index) => {
            $header.append($('<th>').toggleClass('st-report-num', index >= 2).text(name));
        });
        $('#st-table thead').empty().append($header);
        const fmt = (v, decimals = 2) => (v === null || v === undefined || !Number.isFinite(Number(v)))
            ? '–' : Number(v).toLocaleString('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
        const dateText = ts => new Date(Number(ts) * 1000).toLocaleString('de-DE');
        function notify(message, danger = false) {
            $('#st-alert').removeClass('alert-success alert-danger')
                .addClass(danger ? 'alert-danger' : 'alert-success').text(message).show();
        }
        function errMessage(xhr) {
            if (xhr && xhr.responseJSON) {
                return xhr.responseJSON.message || xhr.responseJSON.error || 'API-Fehler';
            }
            return xhr && xhr.status ? `HTTP ${xhr.status}` : 'Verbindungsfehler';
        }
        async function fetchCliInfo() {
            try {
                const data = await $.getJSON(`${API}/info`);
                const safe = value => (value === null || value === undefined || value === '') ? '–' : String(value);
                $('#st-cli-name').text(data.installed
                    ? (data.officialLibreSpeed ? 'LibreSpeed CLI (Erkennung anhand Versionsausgabe)'
                        : 'LibreSpeed-CLI (nicht bestätigt)')
                    : 'Nicht installiert oder nicht ausführbar');
                $('#st-cli-version').text(safe(data.version));
                $('#st-cli-path').text(safe(data.path));
                $('#st-cli-package').text(safe(data.package));
                $('#st-cli-sha256').text(safe(data.sha256));
                $('#st-cli-checked').text(safe(data.checkedAt));
            } catch (err) {
                $('#st-cli-name').text(`Abfrage fehlgeschlagen: ${err.message || errMessage(err)}`);
            }
        }
        async function fetchTable() {
            $('#st-table-status').text('Lade Messwerte ...');
            $('#st-prev, #st-next').prop('disabled', true);
            try {
                const data = await $.getJSON(`${API}/table`, {
                    period: state.period, page: state.page, pageSize: state.pageSize
                });
                if (data.error || !Array.isArray(data.rows)) {
                    throw new Error(data.error || 'Ungültige API-Antwort');
                }
                state.total = Number(data.total) || 0;
                $body.empty();
                if (!data.rows.length) {
                    $body.append($('<tr>').append($('<td>').attr('colspan', 6).text('Keine Messungen gefunden')));
                }
                for (const row of data.rows) {
                    // Never inject untrusted CSV values as HTML.
                    const $tr = $('<tr>');
                    const fields = [dateText(row.ts), row.server || '–', fmt(row.download), fmt(row.upload), fmt(row.ping), fmt(row.jitter)];
                    for (let i = 0; i < fields.length; i++) {
                        $tr.append($('<td>').addClass(i > 1 ? 'st-report-num' : '').text(fields[i]));
                    }
                    $body.append($tr);
                }
                const pages = Math.max(1, Math.ceil(state.total / state.pageSize));
                $('#st-page-info').text(`Seite ${state.page} von ${pages}`);
                $('#st-table-status').text(`${state.total.toLocaleString('de-DE')} Messung(en)`);
                $('#st-prev').prop('disabled', state.page <= 1);
                $('#st-next').prop('disabled', state.page >= pages);
            } catch (err) {
                $body.empty().append($('<tr>').append($('<td>').attr('colspan', 6).text('Fehler beim Laden')));
                $('#st-table-status').text(`Fehler: ${err.message || errMessage(err)}`);
                console.error('Speedtest-Tabelle:', err);
            }
        }
        function destroyCharts() {
            for (const chart of state.charts) chart.destroy();
            state.charts = [];
        }
        function addChart(id, labels, series) {
            const palette = ['#D94F00', '#2387BA'];
            const datasets = series.map((item, i) => ({
                label: item.label, data: item.values,
                borderColor: palette[i % palette.length], backgroundColor: palette[i % palette.length],
                borderWidth: 2, tension: 0.15, fill: false,
                pointRadius: labels.length > 45 ? 0 : 3, spanGaps: false
            }));
            const chart = new Chart(document.getElementById(id).getContext('2d'), {
                type: 'line', data: { labels, datasets }, options: {
                    responsive: true, maintainAspectRatio: false, animation: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: { legend: { display: series.length > 1, position: 'bottom' } },
                    scales: { x: { ticks: { maxTicksLimit: 9, maxRotation: 0 } }, y: { beginAtZero: true } }
                }
            });
            state.charts.push(chart);
        }
        function renderCharts() {
            destroyCharts();
            if (typeof Chart !== 'function') {
                $('#st-chart-status').text('Chart.js konnte nicht geladen werden');
                return;
            }
            const hours = Number($('#st-chart-period').val()) || 24;
            const cutoff = Date.now() / 1000 - hours * 3600;
            const rows = state.points.filter(p => Number(p.ts) >= cutoff);
            if (!rows.length) {
                $('#st-chart-status').text('Keine Messungen im gewählten Zeitraum');
                return;
            }
            try {
                const labels = rows.map(p => new Date(Number(p.ts) * 1000).toLocaleString('de-DE', {
                    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                }));
                addChart('st-chart-speed', labels, [
                    { label: 'Download', values: rows.map(p => p.download) },
                    { label: 'Upload', values: rows.map(p => p.upload) }
                ]);
                addChart('st-chart-latency', labels, [
                    { label: 'Ping', values: rows.map(p => p.ping) },
                    { label: 'Jitter', values: rows.map(p => p.jitter) }
                ]);
                $('#st-chart-status').text(`${rows.length} Messung(en) · zuletzt ${dateText(rows[rows.length - 1].ts)}`);
            } catch (err) {
                destroyCharts();
                $('#st-chart-status').text(`Fehler: ${err.message}`);
                console.error('Speedtest-Diagramme:', err);
            }
        }
        async function fetchCharts() {
            try {
                const result = await $.getJSON(`${API}/data`);
                if (result.error || !Array.isArray(result.rows)) {
                    throw new Error(result.error || 'Ungültige API-Antwort');
                }
                state.points = result.rows;
                renderCharts();
            } catch (err) {
                destroyCharts();
                $('#st-chart-status').text(`Fehler: ${err.message || errMessage(err)}`);
            }
        }
        $('#st-period').on('change', function () {
            state.period = this.value; state.page = 1; fetchTable();
        });
        $('#st-page-size').on('change', function () {
            state.pageSize = Number(this.value) || 50; state.page = 1; fetchTable();
        });
        $('#st-prev').on('click', function () { if (state.page > 1) { --state.page; fetchTable(); } });
        $('#st-next').on('click', function () {
            if (state.page * state.pageSize < state.total) { ++state.page; fetchTable(); }
        });
        $('#st-chart-period').on('change', renderCharts);
        $('#st-refresh').on('click', function () { fetchTable(); fetchCharts(); fetchCliInfo(); });
        $('#st-clear').on('click', function () {
            if (!window.confirm('Alle Messwerte aus /var/log/librespeed.csv entfernen? Eine Sicherung wird vorher erstellt.')) {
                return;
            }
            // OPNsense ajaxCall sends POST and supplies X_CSRFTOKEN for session requests.
            $('#st-clear').prop('disabled', true);
            ajaxCall(`${API}/clear`, {}, function (response, status) {
                $('#st-clear').prop('disabled', false);
                if (status === 'success' && response && response.status === 'ok') {
                    notify(response.message + (response.backup ? ` Sicherung: ${response.backup}` : ''));
                    state.page = 1; fetchTable(); fetchCharts();
                } else {
                    notify(`Leeren fehlgeschlagen: ${(response && (response.message || response.error)) || 'Anforderung abgelehnt'}`, true);
                }
            });
        });
        // One-shot manual test: asynchronous backend process; poll without blocking PHP.
        // Uses persisted server settings, not unsaved form inputs.
        let manualTimer = null;
        let manualRequestPending = false;
        let lastCompletedToken = null;
        let consecutivePollErrors = 0;
        const $manualButton = $('#st-manual-start');
        const $manualText = $('#st-manual-message');
        function setManualMessage(message, failed = false) {
            $manualText.text(message).css('color', failed ? '#b54432' : '');
        }
        function stopManualPolling() {
            if (manualTimer !== null) { clearInterval(manualTimer); manualTimer = null; }
        }
        async function pollManualStatus() {
            try {
                const data = await $.getJSON(`${API}/manualstatus`);
                consecutivePollErrors = 0;
                const state = String(data.status || 'idle');
                const running = state === 'running' || state === 'starting';
                $manualButton.prop('disabled', running || manualRequestPending);
                if (running) {
                    setManualMessage('Manuelle LibreSpeed-Messung läuft. Je nach Serverauswahl kann das mehrere Minuten dauern.');
                    if (manualTimer === null) manualTimer = setInterval(pollManualStatus, 3500);
                } else {
                    stopManualPolling();
                    if (state === 'done') {
                        setManualMessage('Messung erfolgreich abgeschlossen. Die Messwerte wurden aktualisiert.');
                        if (data.token && data.token !== lastCompletedToken) {
                            lastCompletedToken = data.token;
                            fetchTable(); fetchCharts();
                        }
                    } else if (state === 'failed') {
                        setManualMessage(`Messung fehlgeschlagen: ${data.message || 'LibreSpeed-Fehlerprotokoll prüfen'}`, true);
                    } else if (state === 'error') {
                        setManualMessage(data.message || 'Messstatus konnte nicht ermittelt werden', true);
                    }
                }
            } catch (err) {
                consecutivePollErrors++;
                if (consecutivePollErrors >= 3) {
                    stopManualPolling();
                    $manualButton.prop('disabled', false);
                    setManualMessage(`Messstatus nicht erreichbar: ${errMessage(err)}`, true);
                }
            }
        }
        $manualButton.on('click', function () {
            if (manualRequestPending) return;
            if (!window.confirm('Manuellen LibreSpeed-Test mit den zuletzt gespeicherten Einstellungen starten?')) return;
            manualRequestPending = true;
            $manualButton.prop('disabled', true);
            setManualMessage('Messung wird gestartet ...');
            // ajaxCall includes the OPNsense session CSRF token. Never use GET for this action.
            ajaxCall(`${API}/manualstart`, {}, function (data, result) {
                manualRequestPending = false;
                if (result === 'success' && data && ['running', 'starting'].includes(data.status)) {
                    setManualMessage('Manueller Messlauf gestartet. Die Tabelle wird nach Abschluss aktualisiert.');
                    pollManualStatus();
                } else {
                    $manualButton.prop('disabled', false);
                    setManualMessage((data && data.message) || 'Messung konnte nicht gestartet werden', true);
                }
            });
        });
        pollManualStatus();
        // Settings are stored server-side through configd and never evaluated as shell text.
        const serverUi = {available: [], selected: [], loaded: false};
        function updateServerCounter() {
            $('#st-servers-selected').text(`${serverUi.selected.length} von 3 ausgewählt`);
        }
        function renderServerChoices() {
            const text = String($('#st-server-filter').val() || '').toLowerCase().trim();
            const $tbody = $('#st-servers-table tbody').empty();
            let visible = 0;
            for (const item of serverUi.available) {
                if (text && !`${item.id} ${item.name} ${item.url}`.toLowerCase().includes(text)) continue;
                visible++;
                const $check = $('<input>').attr('type','checkbox').addClass('st-server-check')
                    .val(String(item.id)).prop('checked', serverUi.selected.includes(Number(item.id)));
                const $tr = $('<tr>');
                $tr.append($('<td>').append($check));
                $tr.append($('<td>').text(String(item.id)));
                $tr.append($('<td>').text(String(item.name)));
                $tr.append($('<td>').text(String(item.url)));
                $tbody.append($tr);
            }
            if (!visible) $tbody.append($('<tr>').append($('<td>').attr('colspan',4).text('Keine passenden Server gefunden')));
            updateServerCounter();
        }
        async function loadServerSettings() {
            try {
                const response = await $.getJSON(`${API}/settings`);
                if (response.error || !response.settings) throw new Error(response.error || 'Keine Einstellungen');
                const cfg = response.settings;
                $('#st-server-mode').val(cfg.mode || 'auto');
                $('#st-server-execution').val(cfg.execution || 'sequential');
                $('#st-concurrent').val(cfg.concurrent || 6);
                $('#st-duration').val(cfg.duration || 20);
                serverUi.selected = Array.isArray(cfg.servers) ? cfg.servers.map(Number) : [];
                updateServerCounter();
                if (serverUi.loaded) renderServerChoices();
            } catch (err) {
                $('#st-servers-message').text(`Einstellungen konnten nicht geladen werden: ${errMessage(err)}`);
            }
        }
        async function loadServerList() {
            $('#st-servers-count').text('Lade LibreSpeed-Serverliste ...');
            try {
                const response = await $.getJSON(`${API}/serverlist`);
                if (response.error || !Array.isArray(response.servers)) throw new Error(response.error || 'Serverliste nicht verfügbar');
                serverUi.available = response.servers;
                serverUi.loaded = true;
                $('#st-servers-count').text(`${response.servers.length} Server verfügbar`);
                renderServerChoices();
            } catch (err) {
                $('#st-servers-count').text(`Abruf fehlgeschlagen: ${err.message || errMessage(err)}`);
            }
        }
        $('#st-server-filter').on('input', renderServerChoices);
        $('#st-servers-reload').on('click', loadServerList);
        $('#st-servers-table').on('change', '.st-server-check', function () {
            const id = Number(this.value);
            if (this.checked) {
                if (serverUi.selected.length >= 3) {
                    this.checked = false;
                    $('#st-servers-message').text('Maximal drei Server können ausgewählt werden.');
                    return;
                }
                if (!serverUi.selected.includes(id)) serverUi.selected.push(id);
            } else {
                serverUi.selected = serverUi.selected.filter(x => x !== id);
            }
            $('#st-servers-message').text('');
            updateServerCounter();
        });
        $('#st-servers-save').on('click', function () {
            const mode = $('#st-server-mode').val();
            const execution = $('#st-server-execution').val();
            const concurrent = Number($('#st-concurrent').val());
            const duration = Number($('#st-duration').val());
            if (mode === 'selected' && !serverUi.selected.length) {
                $('#st-servers-message').text('Wähle mindestens einen Server aus.'); return;
            }
            if (!Number.isInteger(concurrent) || concurrent < 1 || concurrent > 12 ||
                !Number.isInteger(duration) || duration < 5 || duration > 60) {
                $('#st-servers-message').text('HTTP-Verbindungen 1–12 und Messdauer 5–60 Sekunden.'); return;
            }
            if (mode === 'selected' && (!serverUi.loaded || serverUi.selected.some(id => !serverUi.available.some(s => Number(s.id) === id)))) {
                $('#st-servers-message').text('Serverliste neu laden und gültige Server auswählen.'); return;
            }
            $('#st-servers-save').prop('disabled', true);
            $('#st-servers-message').text('Speichere ...');
            ajaxCall(`${API}/savesettings`, {
                mode, execution, concurrent, duration, servers: serverUi.selected
            }, function (data, status) {
                $('#st-servers-save').prop('disabled', false);
                if (status === 'success' && data && data.settings && !data.error) {
                    $('#st-servers-message').text('Einstellungen gespeichert – gelten ab dem nächsten Messlauf.');
                } else {
                    $('#st-servers-message').text(`Speichern fehlgeschlagen: ${(data && data.error) || 'Berechtigung oder API-Fehler'}`);
                }
            });
        });
        loadServerSettings().then(loadServerList);
        fetchTable(); fetchCharts(); fetchCliInfo();
        // The report page is refreshed on demand; the Dashboard widget updates automatically.
    });
})(jQuery);
