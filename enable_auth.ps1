$cfgPath = "C:\Program Files\MongoDB\Server\8.2\bin\mongod.cfg"

# 1. Check for Admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "ERROR: This script must be run as Administrator! Please open PowerShell as Administrator and run again."
    exit 1
}

if (-Not (Test-Path $cfgPath)) {
    Write-Error "ERROR: MongoDB config file not found at $cfgPath"
    exit 1
}

Write-Host "Reading config from $cfgPath..."
$content = Get-Content -Path $cfgPath -Raw
$updated = $false
$newContent = ""

if ($content -match "authorization: enabled") {
    Write-Host "Authorization is already enabled in mongod.cfg."
} elseif ($content -match "#security:") {
    Write-Host "Enabling authorization..."
    $newContent = $content -replace '#security:', "security:`r`n  authorization: enabled"
    $updated = $true
} elseif ($content -match "security:") {
    Write-Host "Security section exists. Appending authorization: enabled..."
    $newContent = $content -replace "security:", "security:`r`n  authorization: enabled"
    $updated = $true
} else {
    Write-Host "Adding security section..."
    $newContent = $content + "`r`n`r`nsecurity:`r`n  authorization: enabled`r`n"
    $updated = $true
}

if ($updated) {
    try {
        Set-Content -Path $cfgPath -Value $newContent -Encoding utf8 -ErrorAction Stop
        Write-Host "[SUCCESS] Successfully updated mongod.cfg."
    } catch {
        Write-Error "ERROR: Failed to update mongod.cfg. Details: $_"
        exit 1
    }
}

Write-Host "Restarting MongoDB service..."
try {
    Restart-Service -Name MongoDB -Force -ErrorAction Stop
    Write-Host "[SUCCESS] MongoDB service restarted successfully with password protection active!"
} catch {
    Write-Error "ERROR: Failed to restart MongoDB service. Details: $_"
    exit 1
}
