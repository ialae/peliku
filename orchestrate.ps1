<#
.SYNOPSIS
    Orchestrate GitHub Copilot CLI agents for sprint execution and review.

.DESCRIPTION
    Runs the sprintexecutor and/or sprintreviewer Copilot agents
    for one or more sprints, fully automated with no human confirmation.
    All agent output is captured to log files in ./logs/.

.PARAMETER Sprint
    The sprint number to start from (required).

.PARAMETER EndSprint
    The last sprint number (inclusive). Defaults to Sprint for single-sprint runs.

.PARAMETER Mode
    Which agents to run: "both" (executor then reviewer),
    "execute" (executor only), or "review" (reviewer only).
#>

param(
    [Parameter(Mandatory = $true)]
    [int]$Sprint,

    [int]$EndSprint = 0,

    [ValidateSet("both", "execute", "review")]
    [string]$Mode = "both"
)

$ErrorActionPreference = "Stop"
$script:ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $script:ProjectDir

$logsDir = Join-Path $script:ProjectDir "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

if (-not (Get-Command "gh" -ErrorAction SilentlyContinue)) {
    Write-Output "[ERROR] GitHub CLI (gh) not found on PATH"
    exit 1
}

if ($EndSprint -eq 0) { $EndSprint = $Sprint }
if ($EndSprint -lt $Sprint) {
    Write-Output "[ERROR] EndSprint ($EndSprint) must be >= Sprint ($Sprint)"
    exit 1
}

$EXECUTOR_MODEL = "claude-opus-4.6"
$REVIEWER_MODEL = "claude-sonnet-4.6"

function Get-Timestamp { return (Get-Date -Format "HH:mm:ss") }

function Invoke-Agent {
    param(
        [string]$Label,
        [string]$Prompt,
        [string]$Agent,
        [string]$Model,
        [string]$SessionLog,
        [string]$RawLog
    )

    $ts = Get-Timestamp
    Write-Output "[$Label] $ts - Starting: $Prompt"
    Write-Output "[$Label] Logging to: $RawLog"

    # Remove stale log so we start fresh
    if (Test-Path $RawLog) { Remove-Item $RawLog -Force }

    # Run gh copilot as a separate process with output redirected to file.
    # Piping (| Tee-Object) causes PowerShell to buffer all output until
    # the command finishes, which makes the bot appear stuck.
    $proc = Start-Process -FilePath "gh" `
        -ArgumentList @(
            "copilot",
            "-p", "`"$Prompt`"",
            "--agent", $Agent,
            "--model", $Model,
            "--yolo",
            "--no-ask-user",
            "--autopilot",
            "--share", "`"$SessionLog`""
        ) `
        -RedirectStandardOutput $RawLog `
        -RedirectStandardError "$RawLog.err" `
        -NoNewWindow `
        -PassThru `
        -Wait

    $code = $proc.ExitCode
    $ts = Get-Timestamp

    # Stream key lines from the log to stdout for the bot to pick up
    if (Test-Path $RawLog) {
        $logSize = (Get-Item $RawLog).Length
        Write-Output "[$Label] Log size: $logSize bytes"
        # Show last 20 lines as summary
        Get-Content $RawLog -Tail 20 | ForEach-Object { Write-Output $_ }
    }

    # Also show stderr if any
    $errFile = "$RawLog.err"
    if ((Test-Path $errFile) -and (Get-Item $errFile).Length -gt 0) {
        Write-Output "[$Label] STDERR:"
        Get-Content $errFile -Tail 10 | ForEach-Object { Write-Output $_ }
    }

    if ($code -ne 0) {
        Write-Output "[$Label] $ts - FAILED (exit code $code)"
        Write-Output "[$Label] Session: $SessionLog"
        Write-Output "[$Label] Raw log: $RawLog"
        exit 1
    }

    Write-Output "[$Label] $ts - COMPLETED"
}

for ($s = $Sprint; $s -le $EndSprint; $s++) {

    # --- Sprint Executor ---
    if ($Mode -in @("both", "execute")) {
        $sessionLog = Join-Path $logsDir "sprint-$s-executor.md"
        $rawLog = Join-Path $logsDir "sprint-$s-executor-raw.log"

        Invoke-Agent `
            -Label "EXECUTOR" `
            -Prompt "Execute sprint $s" `
            -Agent "sprintexecutor" `
            -Model $EXECUTOR_MODEL `
            -SessionLog $sessionLog `
            -RawLog $rawLog
    }

    # --- Sprint Reviewer ---
    if ($Mode -in @("both", "review")) {
        $sessionLog = Join-Path $logsDir "sprint-$s-reviewer.md"
        $rawLog = Join-Path $logsDir "sprint-$s-reviewer-raw.log"

        Invoke-Agent `
            -Label "REVIEWER" `
            -Prompt "Review sprint $s" `
            -Agent "sprintreviewer" `
            -Model $REVIEWER_MODEL `
            -SessionLog $sessionLog `
            -RawLog $rawLog
    }

    Write-Output "[DONE] $(Get-Timestamp) - Sprint $s"
}

if ($Sprint -ne $EndSprint) {
    Write-Output "[DONE] $(Get-Timestamp) - ALL SPRINTS ($Sprint to $EndSprint) COMPLETED"
}

exit 0
