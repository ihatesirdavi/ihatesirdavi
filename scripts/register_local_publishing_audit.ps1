<#
Register one bounded read-only local Windows audit using existing Task Scheduler.
Run from an ordinary Windows PowerShell session. Never creates a service,
cloud task, deployment, runner, or privilege-elevated process.
#>
[CmdletBinding()]
param(
    [string]$TaskName = 'GitHub-Publishing-Local-Audit',
    [string]$DailyAt = '07:30',
    [string]$OutputDir = (Join-Path $env:LOCALAPPDATA 'GitHub-Publishing\Receipts')
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if($PSVersionTable.PSEdition -eq 'Core' -and -not $IsWindows){
    throw 'Windows Task Scheduler is required'
}
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $repo 'scripts\local_publishing_audit.py'
if(-not (Test-Path -LiteralPath $source -PathType Leaf)){throw 'Missing local Python source'}
if(-not (Test-Path -LiteralPath (Join-Path $repo 'README.md'))){throw 'Missing profile repository'}
$python = Get-Command python.exe -ErrorAction Stop
$pythonw = Join-Path (Split-Path $python.Source -Parent) 'pythonw.exe'
if(-not (Test-Path -LiteralPath $pythonw -PathType Leaf)){throw 'Installed Python has no headless pythonw.exe'}
if(Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue){
    throw ('Existing task needs inspection; refusing duplicate '+$TaskName)
}
$time = [DateTime]::ParseExact($DailyAt, 'HH:mm', [Globalization.CultureInfo]::InvariantCulture)
$principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$arguments = '"' + $source + '" --root "' + $repo + '" --output-dir "' + $OutputDir + '"'
$action = New-ScheduledTaskAction -Execute $pythonw -Argument $arguments -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At $time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 3) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$definition = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Read-only local publishing health audit with versioned JSON receipts. No GitHub writes.'
$null = Register-ScheduledTask -TaskName $TaskName -InputObject $definition
$stored = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
if($stored.Actions.Execute -ne $pythonw -or $stored.Actions.Arguments -ne $arguments -or $stored.State -eq 'Disabled'){
    throw 'Registered task does not match the checked action'
}
Write-Output ('REGISTERED_LOCAL_TASK='+$stored.TaskName)
Write-Output ('TASK_STATE='+$stored.State)
Write-Output ('TASK_EXECUTABLE='+$stored.Actions.Execute)
Write-Output ('TASK_SCHEDULE='+$DailyAt)
Write-Output ('TASK_OUTPUT_DIR='+$OutputDir)