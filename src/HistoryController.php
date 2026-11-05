<?php
/**
 * OPNsense 26.7 CSV Speedtest data endpoints.
 * CSV format: timestamp and normalized LibreSpeed CLI JSON fields.
 * Read-only endpoints never publish the physical file path.
 */
namespace OPNsense\Csvspeedtest\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;

class HistoryController extends ApiControllerBase
{
    private const CSV = '/var/log/librespeed.csv';

    public function dataAction(): array
    {
        if (!$this->request->isGet()) {
            return ['rows' => [], 'error' => 'GET erforderlich'];
        }
        // Same response as the already installed Lobby widget; bounded for charts.
        return $this->chartRows(self::CSV);
    }

    /** Read-only report: current local CLI identity, NOT past measurement provenance. */
    public function infoAction(): array
    {
        if (!$this->request->isGet()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['error' => 'GET erforderlich'];
        }
        $output = trim((string)(new Backend())->configdRun('csvspeedtest info'));
        $result = json_decode($output, true);
        if (!is_array($result) || !isset($result['installed'])) {
            $this->response->setStatusCode(500, 'Internal Server Error');
            return ['error' => 'CLI-Informationen nicht verfuegbar'];
        }
        $this->response->setHeader('Cache-Control', 'private, no-store');
        return $result;
    }

    /** List public servers from librespeed-cli --list, through restricted configd helper. */
    public function serverlistAction(): array
    {
        if (!$this->request->isGet()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['servers' => [], 'error' => 'GET required'];
        }
        $this->response->setHeader('Cache-Control', 'private, no-store');
        $output = (string)(new Backend())->configdRun('csvspeedtest servers_list', false, 60);
        $result = json_decode(trim($output), true);
        if (!is_array($result) || !isset($result['servers']) || !is_array($result['servers'])) {
            $this->response->setStatusCode(502, 'Bad Gateway');
            return ['servers' => [], 'error' => 'Serverliste nicht verfuegbar'];
        }
        return $result;
    }

    public function settingsAction(): array
    {
        if (!$this->request->isGet()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['error' => 'GET required'];
        }
        $this->response->setHeader('Cache-Control', 'private, no-store');
        $output = (string)(new Backend())->configdRun('csvspeedtest servers_settings');
        $result = json_decode(trim($output), true);
        if (!is_array($result) || !isset($result['settings'])) {
            $this->response->setStatusCode(500, 'Internal Server Error');
            return ['error' => 'Einstellungen nicht verfuegbar'];
        }
        return $result;
    }

    /** CSRF checked by ApiControllerBase; requires full admin privilege. */
    public function savesettingsAction(): array
    {
        if (!$this->request->isPost()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['error' => 'POST required'];
        }
        $this->throwReadOnly();
        $this->throwNotFullAdmin();
        $servers = $this->request->getPost('servers');
        if (!is_array($servers) || count($servers) > 3) {
            $this->response->setStatusCode(400, 'Bad Request');
            return ['error' => 'Maximal drei Server erlaubt'];
        }
        $ids = [];
        foreach ($servers as $sid) {
            if ((!is_string($sid) && !is_int($sid)) ||
                !preg_match('/^[1-9][0-9]{0,9}$/D', (string)$sid) ||
                (float)$sid > 2147483647) {
                $this->response->setStatusCode(400, 'Bad Request');
                return ['error' => 'Ungueltige Server-ID'];
            }
            $ids[] = (int)$sid;
        }
        if (count(array_unique($ids)) !== count($ids)) {
            $this->response->setStatusCode(400, 'Bad Request');
            return ['error' => 'Doppelte Server-ID'];
        }
        $payload = [
            'mode' => $this->request->getPost('mode'),
            'servers' => $ids,
            'execution' => $this->request->getPost('execution'),
            'concurrent' => $this->request->getPost('concurrent'),
            'duration' => $this->request->getPost('duration'),
        ];
        $encoded = rtrim(strtr(base64_encode(json_encode($payload)), '+/', '-_'), '=');
        $output = (string)(new Backend())->configdpRun('csvspeedtest servers_save', [$encoded]);
        $result = json_decode(trim($output), true);
        if (!is_array($result) || !empty($result['error']) || !isset($result['settings'])) {
            $this->response->setStatusCode(400, 'Bad Request');
            return ['error' => (string)($result['error'] ?? 'Speichern fehlgeschlagen')];
        }
        return $result;
    }

    /** Start a single manual measurement, using the persisted server settings.
     *  The configd helper returns immediately; polling handles long-running tests.
     */
    public function manualstartAction(): array
    {
        if (!$this->request->isPost()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['status' => 'error', 'message' => 'POST erforderlich'];
        }
        $this->throwReadOnly();
        $this->throwNotFullAdmin();
        $this->response->setHeader('Cache-Control', 'private, no-store');
        try {
            $output = (string)(new Backend())->configdRun('csvspeedtest manual_start', false, 15);
            $result = json_decode(trim($output), true);
        } catch (\Throwable $exc) {
            $this->response->setStatusCode(503, 'Service Unavailable');
            return ['status' => 'error', 'message' => 'Messdienst nicht erreichbar'];
        }
        if (!is_array($result) || !isset($result['status'])) {
            $this->response->setStatusCode(502, 'Bad Gateway');
            return ['status' => 'error', 'message' => 'Ungueltige Antwort vom Messdienst'];
        }
        if ($result['status'] === 'error') {
            $this->response->setStatusCode(409, 'Conflict');
        }
        return $result;
    }

    /** Safe read-only status for the manual measurement started above. */
    public function manualstatusAction(): array
    {
        if (!$this->request->isGet()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['status' => 'error', 'message' => 'GET erforderlich'];
        }
        $this->response->setHeader('Cache-Control', 'private, no-store');
        try {
            $output = (string)(new Backend())->configdRun('csvspeedtest manual_status', false, 10);
            $result = json_decode(trim($output), true);
        } catch (\Throwable $exc) {
            $this->response->setStatusCode(503, 'Service Unavailable');
            return ['status' => 'error', 'message' => 'Messstatus nicht erreichbar'];
        }
        if (!is_array($result) || !isset($result['status'])) {
            $this->response->setStatusCode(502, 'Bad Gateway');
            return ['status' => 'error', 'message' => 'Ungueltiger Messstatus'];
        }
        return $result;
    }

    public function tableAction(): array
    {
        if (!$this->request->isGet()) {
            return ['rows' => [], 'total' => 0, 'error' => 'GET erforderlich'];
        }
        $period = (string)$this->request->getQuery('period', 'string', '24h');
        if (!in_array($period, ['24h', '7d', 'all'], true)) {
            return ['rows' => [], 'total' => 0, 'error' => 'Ungueltiger Zeitraum'];
        }
        $page = max(1, min(1000000, (int)$this->request->getQuery('page', 'int', 1)));
        $pageSize = max(1, min(200, (int)$this->request->getQuery('pageSize', 'int', 50)));
        return $this->pagedRows(self::CSV, $period, $page, $pageSize);
    }

    public function downloadAction()
    {
        if (!$this->request->isGet()) {
            return ['error' => 'GET erforderlich'];
        }
        return $this->streamCsvDownload(self::CSV, 'librespeed-');
    }

    /** Download per-measurement CLI/version attestation sidecar. */
    public function provenanceAction()
    {
        if (!$this->request->isGet()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['error' => 'GET erforderlich'];
        }
        return $this->streamCsvDownload('/var/log/librespeed_provenance.csv', 'librespeed-provenance-');
    }

    /**
     * Stream an unmodified local CSV with the OPNsense 26.7 MVC Response API.
     * Response::setContent(resource, true) uses fpassthru(), not HTML escaping.
     * ApiControllerBase::afterExecuteRoute sends the response when this returns null.
     * Paths are fixed by the controller and never derived from request input.
     */
    protected function streamCsvDownload(string $path, string $filenamePrefix): ?array
    {
        if (is_link($path) || !is_file($path) || !is_readable($path)) {
            $this->response->setStatusCode(404, 'Not Found');
            return ['error' => 'CSV-Datei fehlt oder ist nicht lesbar'];
        }
        $stream = @fopen($path, 'rb');
        if ($stream === false) {
            $this->response->setStatusCode(404, 'Not Found');
            return ['error' => 'CSV-Datei konnte nicht geoeffnet werden'];
        }
        $this->response->setHeader('Cache-Control', 'private, no-store');
        $this->response->setHeader('X-Content-Type-Options', 'nosniff');
        $this->response->setHeader(
            'Content-Disposition',
            'attachment; filename="' . $filenamePrefix . date('Ymd-His') . '.csv"'
        );
        $this->response->setContentType('text/csv', 'UTF-8');
        // Do not close: OPNsense Response::send() streams and closes the resource.
        $this->response->setContent($stream, true);
        return null;
    }

    public function clearAction(): array
    {
        if (!$this->request->isPost()) {
            $this->response->setStatusCode(405, 'Method Not Allowed');
            return ['status' => 'error', 'message' => 'POST erforderlich'];
        }
        // Destructive operation: require full administrators and reject read-only users.
        // OPNsense ApiControllerBase also enforces session CSRF tokens for POST.
        $this->throwReadOnly();
        $this->throwNotFullAdmin();
        $output = trim((string)(new Backend())->configdRun('csvspeedtest clear'));
        $result = json_decode($output, true);
        if (!is_array($result) || !isset($result['status'])) {
            $this->response->setStatusCode(500, 'Internal Server Error');
            return ['status' => 'error', 'message' => 'configd lieferte keine gueltige Antwort'];
        }
        if ($result['status'] !== 'ok') {
            $this->response->setStatusCode(500, 'Internal Server Error');
        }
        return $result;
    }

    /** LibreSpeed normalized CSV: speeds are already Mbps, loss is unknown. */
    private function csvRow(array $fields): ?array
    {
        if (count($fields) !== 8 || !is_numeric($fields[3]) || !is_numeric($fields[4])) {
            return null;
        }
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', trim($fields[0]));
        if ($date === false || $date->format('Y-m-d H:i:s') !== trim($fields[0])) {
            return null;
        }
        $numeric = static function ($value): ?float {
            return is_numeric($value) && is_finite((float)$value) && (float)$value >= 0
                ? round((float)$value, 2) : null;
        };
        $download = $numeric($fields[3]);
        $upload = $numeric($fields[4]);
        if ($download === null || $upload === null) return null;
        return [
            'ts' => $date->getTimestamp(),
            'server' => substr((string)$fields[1], 0, 200),
            'serverId' => '–',
            'resultUrl' => null,
            'download' => $download,
            'upload' => $upload,
            'ping' => $numeric($fields[5]),
            'jitter' => $numeric($fields[6]),
            'loss' => null,
        ];
    }

    private function openCsv(string $path)
    {
        // Never follow an administrator-unexpected symlink.
        if (is_link($path) || !is_file($path) || !is_readable($path)) {
            return false;
        }
        return @fopen($path, 'rb');
    }

    /** Read limited data for the Lobby and report charts. */
    protected function chartRows(string $path): array
    {
        $handle = $this->openCsv($path);
        if ($handle === false) {
            return ['rows' => [], 'error' => 'LibreSpeed-CSV fehlt oder ist nicht lesbar.'];
        }
        $rows = [];
        $cutoff = time() - 31 * 86400;
        try {
            while (($fields = fgetcsv($handle, 0, ',', '"', '')) !== false) {
                $row = $this->csvRow($fields);
                if ($row === null || $row['ts'] < $cutoff || $row['ts'] > time() + 3600) {
                    continue;
                }
                // Use only the fields already expected by the Lobby widget.
                unset($row['serverId']);
                $rows[] = $row;
                // The latest 5000 in file order, with bounded memory.
                if (count($rows) > 5000) {
                    array_shift($rows);
                }
            }
        } finally {
            fclose($handle);
        }
        usort($rows, static fn($a, $b) => $a['ts'] <=> $b['ts']);
        return ['rows' => $rows, 'error' => null];
    }

    /**
     * Two sequential passes: constant memory w.r.t. CSV size.
     * Page 1 contains the most recently APPENDED measurements.
     * This avoids transmitting the complete history to a browser.
     */
    protected function pagedRows(string $path, string $period, int $page, int $pageSize): array
    {
        $handle = $this->openCsv($path);
        if ($handle === false) {
            return ['rows' => [], 'total' => 0, 'page' => $page, 'pageSize' => $pageSize,
                'error' => 'LibreSpeed-CSV fehlt oder ist nicht lesbar.'];
        }
        $cutoff = $period === '24h' ? time() - 86400 : ($period === '7d' ? time() - 7 * 86400 : 0);
        $total = 0;
        $rows = [];
        try {
            while (($fields = fgetcsv($handle, 0, ',', '"', '')) !== false) {
                $row = $this->csvRow($fields);
                if ($row !== null && $row['ts'] >= $cutoff && $row['ts'] <= time() + 3600) {
                    ++$total;
                }
            }
            $start = max(0, $total - $page * $pageSize);
            $end = max(0, $total - ($page - 1) * $pageSize);
            if ($start < $end) {
                rewind($handle);
                $matching = 0;
                while (($fields = fgetcsv($handle, 0, ',', '"', '')) !== false) {
                    $row = $this->csvRow($fields);
                    if ($row === null || $row['ts'] < $cutoff || $row['ts'] > time() + 3600) {
                        continue;
                    }
                    if ($matching >= $start && $matching < $end) {
                        $rows[] = $row;
                    }
                    ++$matching;
                    if ($matching >= $end) {
                        break;
                    }
                }
            }
        } finally {
            fclose($handle);
        }
        return ['rows' => array_reverse($rows), 'total' => $total, 'page' => $page,
            'pageSize' => $pageSize, 'error' => null];
    }
}
