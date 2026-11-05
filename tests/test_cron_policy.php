<?php
require_once __DIR__ . '/../src/cron_policy.php';
function ck($ok, $msg) { if (!$ok) { fwrite(STDERR, "$msg\n"); exit(1); } }
$own = ['command'=>'csvspeedtest run','description'=>CsvSpeedtestCronPolicy::DESCRIPTION,'parameters'=>''];
$user = ['command'=>'speedtest run','description'=>'My old Ookla Speedtest','parameters'=>''];
$modified = ['command'=>'csvspeedtest run','description'=>'Handgeschriebener Job','parameters'=>''];
ck(CsvSpeedtestCronPolicy::decide([])==='create','fresh');
ck(CsvSpeedtestCronPolicy::decide([$own])==='already-managed','idempotence');
ck(CsvSpeedtestCronPolicy::decide([$user])==='existing-user-job','legacy user');
ck(CsvSpeedtestCronPolicy::decide([$modified])==='existing-user-job','untagged new action');
ck(CsvSpeedtestCronPolicy::decide([$user,$own])==='already-managed','mixed');
ck(!CsvSpeedtestCronPolicy::isOwned(['command'=>'csvspeedtest run','description'=>'Other']), 'never remove user');
ck(!CsvSpeedtestCronPolicy::isOtherSpeedtest(['command'=>'cron restart','description'=>'system']), 'other jobs');
echo "GUI-Cron policy cases OK\n";
