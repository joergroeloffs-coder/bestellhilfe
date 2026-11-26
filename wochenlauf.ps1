# Wochenlauf der Bestellhilfe: aktuelle Angebote holen und die App hochladen.
# Laeuft als geplante Aufgabe in Windows (Mittwoch frueh) auf einem oder mehreren PCs.
# Jeder PC hat eine eigene Kopie dieses Repos (nicht im OneDrive-Ordner).
# Ablauf: neuesten Stand holen (git pull) -> aktualisieren.py -> bei Aenderung hochladen.
# Hat ein anderer PC die Angebote dieser Woche schon geholt, steht das im geholten stand.json,
# und aktualisieren.py tut nichts. Protokoll: %LOCALAPPDATA%\Bestellhilfe\lauf.log

$ErrorActionPreference = 'Continue'
$hier = $PSScriptRoot
$logOrdner = Join-Path $env:LOCALAPPDATA 'Bestellhilfe'
New-Item -ItemType Directory -Force $logOrdner | Out-Null
$log = Join-Path $logOrdner 'lauf.log'

function Schreib($text) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $text) -Encoding UTF8 }
function Fuehre-Aus($exe, [string[]]$argumente) {
    & $exe @argumente 2>&1 | ForEach-Object { Schreib "  $_" }
    return $LASTEXITCODE
}

Schreib "=== Start auf $env:COMPUTERNAME"
Set-Location $hier

if ((Fuehre-Aus 'git' @('pull', '--ff-only')) -ne 0) { Schreib 'FEHLER: git pull'; exit 1 }

$env:PYTHONIOENCODING = 'utf-8'
if ((Fuehre-Aus 'python' @('-I', '-X', 'utf8', 'aktualisieren.py')) -ne 0) { Schreib 'FEHLER: aktualisieren.py'; exit 1 }

git add index.html stand.json
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Schreib 'Nichts Neues, nichts hochgeladen.'; exit 0 }

$datum = Get-Date -Format 'yyyy-MM-dd'
if ((Fuehre-Aus 'git' @('-c', 'user.name=joergroeloffs-coder', '-c', 'user.email=joergroeloffs-coder@users.noreply.github.com',
        'commit', '-m', "Angebote aktualisiert ($datum, $env:COMPUTERNAME)")) -ne 0) { Schreib 'FEHLER: commit'; exit 1 }
if ((Fuehre-Aus 'git' @('push')) -ne 0) {
    Schreib 'FEHLER: push (vielleicht war ein anderer PC schneller), lokalen Stand zuruecksetzen'
    git reset --hard '@{u}' | Out-Null
    exit 1
}
Schreib 'Hochgeladen.'
exit 0
