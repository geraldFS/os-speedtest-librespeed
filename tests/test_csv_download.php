<?php
/* Regression test for OPNsense 26.7 MVC Response CSV streaming.
 * Does not open or alter real /var/log/speedtest* files.
 */
namespace OPNsense\Base {
    class ApiControllerBase
    {
        public object $response;
        public object $request;
        public function __construct()
        {
            $this->response = new \FakeResponse();
            $this->request = new class {
                public function isGet(): bool { return true; }
            };
        }
    }
}
namespace OPNsense\Core {
    class Backend {}
}
namespace {
    class FakeResponse
    {
        public array $headers = [];
        public int $status = 200;
        public $stream = null;
        public bool $safe = false;
        public function setHeader(string $key, string $value): void { $this->headers[$key] = $value; }
        public function setContentType(string $value, ?string $charset = null): void
        {
            $this->headers['Content-Type'] = $value . ($charset ? '; charset=' . $charset : '');
        }
        public function setStatusCode(int $status, ?string $reason = null): void { $this->status = $status; }
        public function setContent($content, bool $safe = false): void
        {
            $this->stream = $content;
            $this->safe = $safe;
        }
        public function send(): string
        {
            ob_start();
            if (is_resource($this->stream)) {
                if ($this->safe) { fpassthru($this->stream); }
                else { echo htmlspecialchars(stream_get_contents($this->stream), ENT_NOQUOTES); }
                fclose($this->stream);
            }
            return ob_get_clean();
        }
    }
    require __DIR__ . '/../src/HistoryController.php';
    class TestController extends \OPNsense\Csvspeedtest\Api\HistoryController
    {
        public function stream(string $path, string $prefix): ?array
        {
            return $this->streamCsvDownload($path, $prefix);
        }
    }
    class RouteProbe extends \OPNsense\Csvspeedtest\Api\HistoryController
    {
        public string $capturedPath = '';
        public string $capturedPrefix = '';
        protected function streamCsvDownload(string $path, string $filenamePrefix): ?array
        {
            $this->capturedPath = $path;
            $this->capturedPrefix = $filenamePrefix;
            return null;
        }
    }
    function ensure(bool $predicate, string $message): void
    {
        if (!$predicate) { throw new \RuntimeException($message); }
    }
    $routing = new RouteProbe();
    $routing->downloadAction();
    ensure($routing->capturedPath === '/var/log/librespeed.csv', 'measurement endpoint wrong source');
    ensure($routing->capturedPrefix === 'librespeed-', 'measurement endpoint wrong download name');
    $routing->provenanceAction();
    ensure($routing->capturedPath === '/var/log/librespeed_provenance.csv', 'provenance endpoint wrong source');
    ensure($routing->capturedPrefix === 'librespeed-provenance-', 'provenance endpoint wrong download name');
    $path = tempnam(sys_get_temp_dir(), 'speedtest-download-');
    ensure(is_string($path), 'tempnam() failed');
    try {
        $raw = "Timestamp,Server,Download\n2026-11-04 12:20:25,\"R-KOM\",\"34931585\"\n<>&\"\x00\x01\n";
        file_put_contents($path, $raw);
        foreach (['librespeed-', 'librespeed-provenance-'] as $prefix) {
            $controller = new TestController();
            ensure($controller->stream($path, $prefix) === null, 'valid CSV should stream');
            ensure(is_resource($controller->response->stream), 'stream must stay open until send');
            ensure($controller->response->safe === true, 'CSV must be sent without HTML escaping');
            ensure($controller->response->headers['Content-Type'] === 'text/csv; charset=UTF-8', 'wrong MIME');
            ensure(str_starts_with($controller->response->headers['Content-Disposition'], 'attachment; filename="' . $prefix), 'download filename missing');
            ensure($controller->response->headers['X-Content-Type-Options'] === 'nosniff', 'missing nosniff header');
            ensure($controller->response->send() === $raw, 'CSV bytes altered');
        }
        $missing = new TestController();
        ensure(($missing->stream($path . '.does-not-exist', 'librespeed-')['error'] ?? '') !== '', 'missing file not rejected');
        ensure($missing->response->status === 404, 'missing file status must be 404');
        if (function_exists('symlink')) {
            $alias = $path . '.lnk';
            if (symlink($path, $alias)) {
                try {
                    $linked = new TestController();
                    ensure($linked->stream($alias, 'librespeed-') !== null, 'symlink not rejected');
                    ensure($linked->response->status === 404, 'symlink error status must be 404');
                } finally { unlink($alias); }
            }
        }
    } finally { @unlink($path); }
    echo "Download streaming regression tests passed (routes, unaltered bytes, both filename types, 404, symlink).\n";
}
