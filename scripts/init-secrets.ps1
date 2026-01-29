# PowerShell script to create detect-secrets baseline
Set-StrictMode -Version Latest

python -m pip install --upgrade pip
pip install detect-secrets

detect-secrets scan > .secrets.baseline
Write-Host "Created .secrets.baseline. Review the file and commit it if it is correct (do NOT commit real secrets)."