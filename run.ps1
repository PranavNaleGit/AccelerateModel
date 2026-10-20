param(
    [ValidateSet("setup", "health", "generate", "benchmark", "test", "verify")]
    [string]$Action = "health",
    [string]$Prompt = "Write a Python function to check prime numbers.",
    [int]$Runs = 5,
    [string]$File = "examples/sample_solution.py"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$env:OLLAMA_HOST = "http://127.0.0.1:11435"
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if ($Action -eq "setup") {
    if (!(Test-Path $python)) {
        py -3 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
    }

    & $python -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

    Write-Host "Setup complete." -ForegroundColor Green
    exit
}

if (!(Test-Path $python)) {
    Write-Host "Run setup first: .\run.ps1 setup" -ForegroundColor Yellow
    exit 1
}

switch ($Action) {
    "health" {
        & $python -m local_code_engine health
    }
    "generate" {
        & $python -m local_code_engine generate $Prompt
    }
    "benchmark" {
        & $python -m local_code_engine benchmark --runs $Runs --output "results\benchmark-results.json"
    }
    "test" {
        & $python -m pytest
    }
    "verify" {
        & $python -m local_code_engine verify --file $File
    }
}

if ($LASTEXITCODE -ne 0) {
    throw "Action '$Action' failed. Read the error above."
}
