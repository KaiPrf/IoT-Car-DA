$ErrorActionPreference = "Stop"

$Distro = "Ubuntu-26.04"
$Port = 8080


# Aktive Netzwerkverbindung ermitteln
$Network = Get-NetIPConfiguration |
    Where-Object {
        $_.NetAdapter.Status -eq "Up" -and
        $_.IPv4DefaultGateway -ne $null -and
        $_.IPv4Address.IPAddress -ne $null
    } |
    Select-Object -First 1

if (-not $Network) {
    throw "Keine aktive IPv4-Netzwerkverbindung gefunden."
}


$WindowsIp = $Network.IPv4Address.IPAddress

if ($WindowsIp -is [array]) {
    $WindowsIp = $WindowsIp[0]
}


# Netzwerkname ermitteln
$NetworkProfile = Get-NetConnectionProfile `
    -InterfaceIndex $Network.InterfaceIndex `
    -ErrorAction SilentlyContinue

if ($NetworkProfile) {
    $NetworkName = $NetworkProfile.Name
}
else {
    $NetworkName = $Network.InterfaceAlias
}


# Docker prüfen
Write-Host "Prüfe Docker ..." -ForegroundColor DarkGray

wsl.exe `
    -d $Distro `
    -- docker info *> $null

if ($LASTEXITCODE -ne 0) {
    throw "Docker ist in $Distro nicht verfügbar. Docker Desktop starten und WSL-Integration prüfen."
}


# Firewallregel anlegen
$FirewallRule = Get-NetFirewallRule `
    -DisplayName "IoT Car Docker Web UI" `
    -ErrorAction SilentlyContinue

if (-not $FirewallRule) {
    Write-Host "Erstelle Firewallregel für Port $Port ..." -ForegroundColor DarkGray

    New-NetFirewallRule `
        -DisplayName "IoT Car Docker Web UI" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort $Port `
        -Action Allow |
        Out-Null
}


Clear-Host

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " IoT-Car Simulator - Docker" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Netzwerk" -ForegroundColor White
Write-Host ""
Write-Host "Name       : $NetworkName"
Write-Host "Windows-IP : $WindowsIp"
Write-Host "Port       : $Port"

Write-Host ""

Write-Host "PC" -ForegroundColor Green
Write-Host ""
Write-Host "http://localhost:$Port/info"

Write-Host ""

Write-Host "Handy" -ForegroundColor Green
Write-Host ""
Write-Host "http://${WindowsIp}:$Port/control"

Write-Host ""
Write-Host "Das Handy muss sich im Netzwerk '$NetworkName' befinden."

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Container wird gestartet ..."
Write-Host "Mit Ctrl+C beenden."
Write-Host ""


try {

    wsl.exe `
        -d $Distro `
        -- env `
        "IOT_CAR_HOST_IP=$WindowsIp" `
        "IOT_CAR_NETWORK_NAME=$NetworkName" `
        bash -lc 'cd "$HOME/iot_car_ws" && docker compose up'

}
finally {

    Write-Host ""
    Write-Host "Beende IoT-Car Container ..." -ForegroundColor Yellow

    wsl.exe `
        -d $Distro `
        -- bash -lc 'cd "$HOME/iot_car_ws" && docker compose stop'

    Write-Host ""
    Write-Host "IoT-Car wurde beendet." -ForegroundColor Green
}
