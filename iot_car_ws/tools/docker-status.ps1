$Distro = "Ubuntu-26.04"

Clear-Host

wsl.exe `
    -d $Distro `
    -- bash -lc '$HOME/iot_car_ws/tools/docker-status.sh'

Write-Host ""
Read-Host "Enter zum Beenden"
