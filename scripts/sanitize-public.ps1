# Strip personal and client data from the plugin before it goes to a public repository.
# Run before every push (the repository is public); safe to run repeatedly.
#
# Two rule sets:
#   - generic regex rules below (safe to publish);
#   - literal rules in scripts/sanitize-rules.local.json (gitignored: they contain
#     the exact names being removed, so they must never be committed).
#     Format: [{ "Pattern": "<.NET regex>", "Replace": "<text>" }, ...]
# When check-public.ps1 reports a new finding, add a rule to the local file
# (or here, if the pattern itself reveals nothing).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts/sanitize-public.ps1

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\plugins\create-plugin")).Path
$Utf8 = New-Object System.Text.UTF8Encoding($false)

$Rules = @(
    # Antivirus script injected into a saved HTML page (machine-specific id)
    @{ Pattern = '<script[^>]*kaspersky-labs[^>]*>.*?</script>'; Replace = '' },
    @{ Pattern = '<link[^>]*kaspersky-labs[^>]*>'; Replace = '' },

    # Client workspaces in example pages -> template placeholder (file-share links: local rules)
    @{ Pattern = 'https://[a-z0-9.-]+/workspaces/[0-9a-f-]{36}'; Replace = '{{ССЫЛКА_ПРОСТРАНСТВО}}' }
)

$Local = Join-Path $PSScriptRoot "sanitize-rules.local.json"
if (Test-Path $Local) {
    foreach ($r in @([IO.File]::ReadAllText($Local, $Utf8) | ConvertFrom-Json)) { foreach ($x in $r) { $Rules += @{ Pattern = $x.Pattern; Replace = $x.Replace } } }
} else {
    Write-Warning "sanitize-rules.local.json not found: only generic rules applied. check-public.ps1 will flag what is left."
}

$TextExt = '.md', '.html', '.json', '.css', '.py', '.yaml', '.txt'
$changed = @()
Get-ChildItem $Root -Recurse -File | Where-Object { $TextExt -contains $_.Extension } | ForEach-Object {
    $text = [IO.File]::ReadAllText($_.FullName, $Utf8)
    $new = $text
    foreach ($r in $Rules) {
        $new = [regex]::Replace($new, $r.Pattern, $r.Replace, [Text.RegularExpressions.RegexOptions]::Singleline)
    }
    if ($new -ne $text) {
        [IO.File]::WriteAllText($_.FullName, $new, $Utf8)
        $changed += $_.FullName.Substring($Root.Length + 1)
    }
}

if ($changed.Count -eq 0) { Write-Output "Sanitize: nothing to change." }
else { Write-Output "Sanitized $($changed.Count) file(s):"; $changed | ForEach-Object { Write-Output "  $_" } }