#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run xuml from the latest GitHub source using uvx.
.DESCRIPTION
    Passes all arguments through to the xuml CLI. Requires uv/uvx and network access.
.EXAMPLE
    .\xuml.ps1 -svg https://github.com/bonsai/comfy-gen-lora/blob/master/kaggle/interpolate_rife.py
.EXAMPLE
    .\xuml.ps1 -svg .\src\module.py -o .\module.svg
#>

$ErrorActionPreference = 'Stop'

if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    Write-Error 'uvx was not found. Install uv first: https://docs.astral.sh/uv/'
    exit 127
}

$xumlArgs = @($args)
& uvx --from 'git+https://github.com/bonsai/xuml.git' xuml @xumlArgs
exit $LASTEXITCODE
