$ErrorActionPreference = "Stop"

$Distro = "Ubuntu-26.04"
$Port = 8080


# Administratorrechte prüfen
$IsAdmin = (
    New-Object Security.Principal.WindowsPrincipal(
        [Security.Principal.WindowsIdentity]::GetCurrent()
    )
).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $IsAdmin) {
    Write-Host ""
    Write-Host "Dieses Script muss als Administrator gestartet werden." -ForegroundColor Yellow
    Write-Host ""

    Read-Host "Enter zum Beenden"
    exit 1
}


# Aktive Netzwerkverbindung
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


# Netzwerkname
$NetworkProfile = Get-NetConnectionProfile `
    -InterfaceIndex $Network.InterfaceIndex `
    -ErrorAction SilentlyContinue

if ($NetworkProfile) {
    $NetworkName = $NetworkProfile.Name
}
else {
    $NetworkName = $Network.InterfaceAlias
}


# WSL-IP
$WslIpOutput = wsl.exe `
    -d $Distro `
    -- hostname -I

$WslIp = (
    $WslIpOutput.Trim() -split "\s+"
)[0]

if (-not $WslIp) {
    throw "WSL-IP konnte nicht ermittelt werden."
}


# Portweiterleitung
netsh interface portproxy delete v4tov4 `
    listenaddress=0.0.0.0 `
    listenport=$Port `
    2>$null | Out-Null

netsh interface portproxy add v4tov4 `
    listenaddress=0.0.0.0 `
    listenport=$Port `
    connectaddress=$WslIp `
    connectport=$Port | Out-Null


# Firewall
$FirewallRule = Get-NetFirewallRule `
    -DisplayName "IoT Car Web UI" `
    -ErrorAction SilentlyContinue

if (-not $FirewallRule) {
    New-NetFirewallRule `
        -DisplayName "IoT Car Web UI" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort $Port `
        -Action Allow |
        Out-Null
}


Clear-Host

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " IoT-Car Simulator" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Netzwerk" -ForegroundColor White
Write-Host ""

Write-Host "Name       : $NetworkName"
Write-Host "Windows-IP : $WindowsIp"
Write-Host "WSL-IP     : $WslIp"
Write-Host "Port       : $Port"

Write-Host ""

Write-Host "PC-Steuerung" -ForegroundColor Green
Write-Host ""
Write-Host "http://localhost:$Port/control"

Write-Host ""

Write-Host "Handy-Steuerung" -ForegroundColor Green
Write-Host ""
Write-Host "http://${WindowsIp}:$Port/control"

Write-Host ""

Write-Host "Info-Seite" -ForegroundColor Green
Write-Host ""
Write-Host "http://localhost:$Port/info"

Write-Host ""
Write-Host "Das Handy muss sich im Netzwerk '$NetworkName' befinden."
Write-Host ""

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""


# Simulation starten
wsl.exe `
    -d $Distro `
    -- env `
    "IOT_CAR_HOST_IP=$WindowsIp" `
    "IOT_CAR_NETWORK_NAME=$NetworkName" `
    bash -lc '$HOME/iot_car_ws/tools/start_stack.sh'
