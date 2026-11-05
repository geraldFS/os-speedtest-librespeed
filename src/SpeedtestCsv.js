/**
 * OPNsense 26.7: Speedtest history dashboard widget (CSV-backed).
 * Important: WidgetManager serializes getMarkup() to outerHTML and injects a
 * new DOM subtree; therefore onMarkupRendered() must select the live DOM.
 */
export default class SpeedtestCsv extends BaseWidget {
    constructor(config) {
        super(config);
        this.tickTimeout = 60;
        this.periodHours = 24;
        this.measurements = [];
        this.charts = [];
        this.root = null;
    }

    getGridOptions() {
        return { w: 6, h: 6, minW: 4, minH: 4, sizeToContent: 690 };
    }

    getMarkup() {
        // Do not store or attach handlers to this temporary jQuery element:
        // OPNsense WidgetManager inserts a *serialized copy* into the grid.
        return $(`
            <div class="csvspeedtest" style="padding: 8px 12px;">
                <div style="display:flex; justify-content:space-between; gap:10px; align-items:center; margin-bottom:10px;">
                    <span class="csvspeedtest-status text-muted">Messungen werden geladen...</span>
                    <select class="csvspeedtest-range form-control input-sm" style="max-width:145px;" aria-label="Zeitraum">
                        <option value="24">24 Stunden</option>
                        <option value="168">7 Tage</option>
                        <option value="720">30 Tage</option>
                    </select>
                </div>
                <div class="csvspeedtest-summary" style="margin-bottom:10px; font-size:13px;"></div>
                <div style="font-weight:600; margin-bottom:2px;">Download / Upload (Mbit/s)</div>
                <div style="height:205px; position:relative; margin-bottom:10px;"><canvas class="csvspeedtest-speed"></canvas></div>
                <div style="font-weight:600; margin-bottom:2px;">Ping / Jitter (ms)</div>
                <div style="height:135px; position:relative; margin-bottom:10px;"><canvas class="csvspeedtest-latency"></canvas></div>
                <div style="font-weight:600; margin-bottom:2px;">Paketverlust (%)</div>
                <div class="text-muted">LibreSpeed: Paketverlust wird nicht ermittelt.</div>
            </div>
        `);
    }

    async onMarkupRendered() {
        // Target the actual widget in the DOM after OPNsense/GridStack rendered it.
        this.root = $(`.widget-${this.id} .csvspeedtest`).first();
        if (!this.root.length) {
            throw new Error('Speedtest-Widget im Dashboard-DOM nicht gefunden.');
        }
        this.root.find('.csvspeedtest-range')
            .off('change.csvspeedtest')
            .on('change.csvspeedtest', (event) => {
                const next = Number(event.currentTarget.value);
                if ([24, 168, 720].includes(next)) {
                    this.periodHours = next;
                    this.renderCharts();
                }
            });
        // OPNsense WidgetManager calls onWidgetTick() after this method;
        // do not fetch data twice here.
    }

    async onWidgetTick() {
        if (!this.root || !this.root.length || !this.root[0].isConnected) {
            // Do not silently update a detached element if the grid was rebuilt.
            await this.onMarkupRendered();
        }
        try {
            const response = await this.ajaxCall('/api/csvspeedtest/history/data');
            if (response && response.error) {
                throw new Error(String(response.error));
            }
            if (!response || !Array.isArray(response.rows)) {
                throw new Error('Unerwartete API-Antwort (rows fehlt).');
            }
            this.measurements = response.rows;
            this.renderCharts();
        } catch (error) {
            this.destroyCharts();
            const detail = (error && error.message) ? error.message : 'API-Aufruf fehlgeschlagen';
            this.root.find('.csvspeedtest-status').text(`Fehler: ${detail}`);
            console.error('Speedtest CSV widget:', error);
        }
    }

    makeChart(canvas, labels, series) {
        if (!canvas) {
            throw new Error('Diagramm-Canvas fehlt.');
        }
        const colors = ['#D94F00', '#2387BA'];
        const datasets = series.map((item, index) => ({
            label: item.label,
            data: item.values,
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length],
            pointRadius: labels.length > 45 ? 0 : 3,
            pointHoverRadius: 4,
            borderWidth: 2,
            fill: false,
            tension: 0.15,
            spanGaps: false
        }));
        const chart = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: series.length > 1, position: 'bottom' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 7, maxRotation: 0 } },
                    y: { beginAtZero: true }
                }
            }
        });
        this.charts.push(chart);
    }

    destroyCharts() {
        for (const chart of this.charts) {
            chart.destroy();
        }
        this.charts = [];
    }

    renderCharts() {
        if (!this.root || !this.root.length) {
            return;
        }
        this.destroyCharts();
        if (typeof Chart !== 'function') {
            this.root.find('.csvspeedtest-status').text('Fehler: Chart.js ist im Dashboard nicht geladen.');
            return;
        }
        const threshold = Date.now() / 1000 - this.periodHours * 3600;
        const rows = this.measurements.filter((row) => Number(row.ts) >= threshold);
        if (!rows.length) {
            this.root.find('.csvspeedtest-status').text('Keine Messungen im gewählten Zeitraum');
            this.root.find('.csvspeedtest-summary').text('');
            return;
        }
        try {
            const last = rows[rows.length - 1];
            const fmt = (value, suffix) => (value === null || value === undefined)
                ? 'n/v'
                : `${Number(value).toFixed(2)} ${suffix}`;
            const dateText = new Date(Number(last.ts) * 1000).toLocaleString('de-DE');
            this.root.find('.csvspeedtest-status')
                .text(`${rows.length} Messung(en) · zuletzt ${dateText}`);
            this.root.find('.csvspeedtest-summary').text(
                `Download: ${fmt(last.download, 'Mbit/s')} | ` +
                `Upload: ${fmt(last.upload, 'Mbit/s')} | ` +
                `Ping: ${fmt(last.ping, 'ms')} | ` +
                `Server: ${last.server || "automatisch"}`
            );
            const labels = rows.map((row) => new Date(Number(row.ts) * 1000).toLocaleString('de-DE', {
                day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
            }));
            this.makeChart(this.root.find('.csvspeedtest-speed')[0], labels, [
                { label: 'Download', values: rows.map(row => row.download) },
                { label: 'Upload', values: rows.map(row => row.upload) }
            ]);
            this.makeChart(this.root.find('.csvspeedtest-latency')[0], labels, [
                { label: 'Ping', values: rows.map(row => row.ping) },
                { label: 'Jitter', values: rows.map(row => row.jitter) }
            ]);
        } catch (error) {
            this.destroyCharts();
            this.root.find('.csvspeedtest-status')
                .text(`Diagrammfehler: ${error && error.message ? error.message : 'unbekannt'}`);
            console.error('Speedtest CSV chart:', error);
        }
    }

    onWidgetResize() {
        for (const chart of this.charts) {
            chart.resize();
        }
        return false;
    }

    onWidgetClose() {
        this.destroyCharts();
        this.root = null;
        super.onWidgetClose();
    }
}
