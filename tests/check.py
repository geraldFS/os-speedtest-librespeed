from pathlib import Path
import ast,re
root=Path(__file__).resolve().parents[1]
assert '0.5.4-L' in (root/'build_pkg.py').read_text()
assert 'ookla' not in (root/'src/measure.sh').read_text().lower()
ast.parse((root/'src/measure_libre.py').read_text())
assert 'private const CSV = \'/var/log/librespeed.csv\'' in (root/'src/HistoryController.php').read_text()
assert '--json' in (root/'src/measure_libre.py').read_text()
assert 'sha256' in (root/'scripts/install-librespeed.sh').read_text()
print('LibreSpeed source regression checks OK')

# Old compiled Volt views must not survive an upgrade.
view = (root/'src/index.volt').read_text()
assert 'LibreSpeed – Messwertbericht' in view
assert '/var/log/librespeed.csv' in view
assert 'Ookla-Ergebnis' not in view
assert 'Server-ID' not in view
assert '/var/log/speedtest.csv' not in view
assert 'LibreSpeed-Verlauf' in view
hook=(root/'hooks/post-install.sh').read_text()
assert "-iname '*csvspeedtest*'" in hook
assert '-delete' in hook
assert '-exec rm' not in hook
assert 'maxdepth 1' in hook
installer=(root/'install.sh').read_text()
assert 'configctl webgui restart' in installer
print('Volt-template cache upgrade regression checks OK')

# The renderer must have exactly the same six columns as its row data.
import re
script = (root/'src/csvspeedtest_report.js').read_text()
assert 'const columns = [' in script
column_names = re.search(r'const columns = \[(.*?)\];', script, re.S).group(1)
assert column_names.count("'") == 12
assert "const fields = [dateText(row.ts), row.server || '–', fmt(row.download), fmt(row.upload), fmt(row.ping), fmt(row.jitter)]" in script
assert "$('#st-table thead').empty().append($header);" in script
assert '<td colspan="6">' in view
assert len(re.findall(r'<th(?:\s|>)', view.split('id="st-table"', 1)[1].split('</table>', 1)[0])) == 6
print('Six-column header / value alignment checks OK')
