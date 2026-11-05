#!/bin/sh
# Explicit manual rollback, no accidental deletion of pkg-owned files.
echo 'Bei pkg-Installation: Sicherung unter /usr/local/opnsense/speedtest-csv-dashboard/pkg-migrations/'
echo 'Zum Zuruecksetzen zuerst pkg delete os-speedtest-csv-reporting ausfuehren.'
echo 'Die Sicherung ist danach manuell und gezielt wiederherzustellen.'
exit 0
