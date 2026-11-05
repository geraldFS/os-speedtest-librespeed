<?php
/**
 * MIT licensed, policy for non-destructive Cron changes.
 * This is separate from the OPNsense model so it can be tested in isolation.
 */
final class CsvSpeedtestCronPolicy
{
    public const COMMAND = 'csvspeedtest run';
    public const DESCRIPTION = 'LibreSpeed Reporting [os-speedtest-csv-reporting]';

    public static function isOwned(array $job): bool
    {
        return trim((string)($job['command'] ?? '')) === self::COMMAND
            && trim((string)($job['description'] ?? '')) === self::DESCRIPTION
            && trim((string)($job['parameters'] ?? '')) === '';
    }

    public static function isOtherSpeedtest(array $job): bool
    {
        if (self::isOwned($job)) {
            return false;
        }
        $command = strtolower(trim((string)($job['command'] ?? '')));
        $desc = strtolower(trim((string)($job['description'] ?? '')));
        $params = strtolower(trim((string)($job['parameters'] ?? '')));
        // Be conservative, never modify any possibly related user job.
        return str_contains($command, 'speedtest')
            || str_contains($desc, 'speedtest')
            || str_contains($params, 'speedtest');
    }

    public static function decide(array $jobs): string
    {
        foreach ($jobs as $job) {
            if (self::isOwned($job)) {
                return 'already-managed';
            }
        }
        foreach ($jobs as $job) {
            if (self::isOtherSpeedtest($job)) {
                return 'existing-user-job';
            }
        }
        return 'create';
    }
}
