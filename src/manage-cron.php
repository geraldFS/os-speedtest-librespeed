#!/usr/local/bin/php
<?php
/**
 * OPNsense Cron 26.7 integration. Only installs/removes tagged GUI jobs.
 * Uses OPNsense Cron model and persists to config.xml via Config class;
 * never performs direct XML rewriting.
 */
require_once __DIR__ . '/cron_policy.php';
require_once '/usr/local/opnsense/mvc/script/load_phalcon.php';

use OPNsense\Cron\Cron;
use OPNsense\Core\Config;

if (PHP_SAPI !== 'cli' || !isset($argv[1]) || !in_array($argv[1], ['--ensure', '--remove-owned', '--status'], true)) {
    fwrite(STDERR, "Use: manage-cron.php --ensure|--remove-owned|--status\n");
    exit(2);
}

try {
    $action = $argv[1];
    $config = Config::getInstance();
    if ($action !== '--status') {
        $config->lock();
    }
    $model = new Cron();
    $jobs = [];
    foreach ($model->jobs->job->iterateItems() as $node) {
        $attributes = $node->getAttributes();
        $jobs[] = [
            'uuid' => (string)($attributes['uuid'] ?? ''),
            'command' => (string)$node->command,
            'description' => (string)$node->description,
            'parameters' => (string)$node->parameters,
        ];
    }

    if ($action === '--status') {
        echo 'Cron-Entscheidung: ' . CsvSpeedtestCronPolicy::decide($jobs) . "\n";
        exit(0);
    }
    if ($action === '--remove-owned') {
        $removed = 0;
        foreach ($jobs as $job) {
            if (CsvSpeedtestCronPolicy::isOwned($job) && $job['uuid'] !== '') {
                if ($model->jobs->job->del($job['uuid'])) {
                    ++$removed;
                }
            }
        }
        if ($removed) {
            $model->serializeToConfig();
            $config->save(['description' => 'Remove package-managed LibreSpeed Reporting cron job']);
        }
        printf("Cron: %d eindeutig paketverwaltete GUI-Jobs entfernt.\n", $removed);
        exit(0);
    }

    $decision = CsvSpeedtestCronPolicy::decide($jobs);
    if ($decision !== 'create') {
        echo $decision === 'already-managed'
            ? "Cron: Paket-Job existiert bereits (Intervall bleibt unveraendert).\n"
            : "Cron: Benutzer-Speedtest-Job erkannt. Keine weitere Messung eingeplant.\n";
        exit(0);
    }
    $job = $model->jobs->job->Add();
    // 'cron' permits editing and deletion through the standard WebGUI.
    $job->origin = 'cron';
    $job->enabled = '1';
    $job->minutes = '0';
    $job->hours = '*';
    $job->days = '*';
    $job->months = '*';
    $job->weekdays = '*';
    $job->who = 'root';
    $job->command = CsvSpeedtestCronPolicy::COMMAND;
    $job->parameters = '';
    $job->description = CsvSpeedtestCronPolicy::DESCRIPTION;
    $messages = $model->performValidation();
    if (count($messages) !== 0) {
        foreach ($messages as $message) {
            fwrite(STDERR, $message->getField() . ': ' . $message->getMessage() . "\n");
        }
        exit(1);
    }
    $model->serializeToConfig();
    $config->save(['description' => 'Create hourly GUI LibreSpeed Reporting cron job']);
    echo "Cron: Neuer GUI-Job 0 * * * * fuer csvspeedtest run angelegt.\n";
} catch (Throwable $error) {
    fwrite(STDERR, 'Cron integration: ' . $error->getMessage() . "\n");
    exit(1);
}
