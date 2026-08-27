param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$WranglerArguments
)

$values = @{}
Get-Content (Join-Path $PSScriptRoot '..\.env') -ErrorAction SilentlyContinue | ForEach-Object {
    $key, $value = $_ -split '=', 2
    if ($null -ne $value) {
        $values[$key.Trim()] = $value.Trim().Trim('"').Trim("'")
    }
}

function Get-CredentialValue([string[]]$Names) {
    foreach ($name in $Names) {
        $environmentValue = [Environment]::GetEnvironmentVariable($name)
        if ($environmentValue) { return $environmentValue }
        if ($values.ContainsKey($name) -and $values[$name]) { return $values[$name] }
    }
    return ''
}

$candidates = @(
    @{ id = Get-CredentialValue @('cloudflare-api-id', 'CLOUDFLARE_API_ID'); token = Get-CredentialValue @('cloudflare-api-token', 'CLOUDFLARE_API_TOKEN') },
    @{ id = Get-CredentialValue @('IA_API_ACCOUNT'); token = Get-CredentialValue @('IA_API_KEY') },
    @{ id = Get-CredentialValue @('CLOUDFLARE_ACCOUNT_ID'); token = Get-CredentialValue @('CLOUDFLARE_API_TOKEN') }
) | Where-Object { $_.id -and $_.token }

if (-not $candidates) {
    throw 'Missing Cloudflare account/token credentials in api/.env'
}

$lastExitCode = 1
foreach ($candidate in $candidates) {
    $env:CLOUDFLARE_ACCOUNT_ID = $candidate.id
    $env:CLOUDFLARE_API_TOKEN = $candidate.token
    cmd /c npx wrangler @WranglerArguments
    $lastExitCode = $LASTEXITCODE
    if ($lastExitCode -eq 0) { exit 0 }
}
exit $lastExitCode
