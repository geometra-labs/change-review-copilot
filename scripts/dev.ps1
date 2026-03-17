param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("api", "web", "test", "lint", "fmt", "migrate")]
    [string]$Task
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Invoke-WebScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ScriptName
    )

    $pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
    if ($pnpm) {
        & $pnpm.Source $ScriptName
        return
    }

    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if ($npm) {
        & $npm.Source "run" $ScriptName
        return
    }

    throw "Neither 'pnpm' nor 'npm' is installed or on PATH."
}

switch ($Task) {
    "api" {
        Set-Location (Join-Path $repoRoot "apps/api")
        python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    }
    "web" {
        Set-Location (Join-Path $repoRoot "apps/web")
        Invoke-WebScript -ScriptName "dev"
    }
    "test" {
        Set-Location (Join-Path $repoRoot "apps/api")
        python -m pytest -q
    }
    "lint" {
        Set-Location (Join-Path $repoRoot "apps/api")
        python -m ruff check .
        Set-Location (Join-Path $repoRoot "apps/web")
        Invoke-WebScript -ScriptName "lint"
    }
    "fmt" {
        Set-Location (Join-Path $repoRoot "apps/api")
        python -m ruff format .
        Set-Location (Join-Path $repoRoot "apps/web")
        Invoke-WebScript -ScriptName "format"
    }
    "migrate" {
        Set-Location (Join-Path $repoRoot "apps/api")
        python -m alembic upgrade head
    }
}
