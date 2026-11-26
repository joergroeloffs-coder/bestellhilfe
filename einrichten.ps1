# Richtet den Wochenlauf auf diesem PC ein (einmal pro PC ausfuehren).
# Voraussetzungen: Python und Git sind installiert, Git darf zu GitHub hochladen.
# Aufruf in PowerShell:  powershell -ExecutionPolicy Bypass -File einrichten.ps1
# Legt eine eigene Kopie des Repos unter %LOCALAPPDATA%\Bestellhilfe\repo an (nicht im OneDrive)
# und eine geplante Aufgabe "Bestellhilfe Angebote": Mittwoch 6 Uhr, Nachholen um 9 Uhr;
# war der PC aus, laeuft sie beim naechsten Einschalten.

$ErrorActionPreference = 'Stop'
$ziel = Join-Path $env:LOCALAPPDATA 'Bestellhilfe\repo'
if (-not (Test-Path (Join-Path $ziel '.git'))) {
    New-Item -ItemType Directory -Force (Split-Path $ziel) | Out-Null
    git clone https://github.com/joergroeloffs-coder/bestellhilfe.git $ziel
    if ($LASTEXITCODE -ne 0) { throw 'git clone fehlgeschlagen' }
}

$skript = Join-Path $ziel 'wochenlauf.ps1'
$aktion = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$skript`"" -WorkingDirectory $ziel
$ausloeser = @(
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Wednesday -At '06:00'),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Wednesday -At '09:00')
)
$einst = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'Bestellhilfe Angebote' -Action $aktion -Trigger $ausloeser -Settings $einst `
    -Description 'Holt mittwochs die aktuellen EDEKA-Angebote und laedt die Bestellhilfe hoch (wochenlauf.ps1).' -Force | Out-Null
Write-Host "Eingerichtet. Repo: $ziel  Protokoll: $env:LOCALAPPDATA\Bestellhilfe\lauf.log"
