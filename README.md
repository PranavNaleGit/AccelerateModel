# LocalCodeEngine

A unified local code generation and benchmarking project.

## First-time setup
```powershell
.\run.ps1 setup
```

## Commands
```powershell
.\run.ps1 health
.\run.ps1 generate -Prompt "Write a Python binary search function."
.\run.ps1 benchmark -Runs 5
.\run.ps1 verify
.\run.ps1 test
```

Configuration: `config/settings.json`
Benchmark results: `results/benchmark-results.json`

The current engine uses Ollama. The launcher expects the Ollama server
to be available at http://127.0.0.1:11435.
