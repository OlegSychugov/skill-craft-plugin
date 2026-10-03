# Sync skill-craft content from the source of truth (.kilo/skills/skill-craft in cowork_hub)
# into plugins/skill-craft/skills/skill-craft. SKILL.md is excluded: the marketplace
# version has its own frontmatter and the "Команды плагина" section.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts/sync-from-source.ps1 [-Source <path>]

param(
    [string]$Source = (Join-Path $PSScriptRoot "..\..\skill-craft")
)

$ErrorActionPreference = "Stop"
$Source = (Resolve-Path $Source).Path
$Target = Join-Path $PSScriptRoot "..\plugins\skill-craft\skills\skill-craft"
New-Item -ItemType Directory -Force $Target | Out-Null
$Target = (Resolve-Path $Target).Path

# Not published: proprietary GigaCowork brand assets and the SB Sans font.
# brand_cards.py / auto_edit.py fall back to a brand-coloured gradient and Arial.
$Exclude = @("*\brand\*", "*\__pycache__\*", "*.ttf", "*.otf")

$changed = @()
Get-ChildItem $Source -Recurse -File | Where-Object { $_.Name -ne "SKILL.md" -or $_.DirectoryName -ne $Source } | Where-Object {
    $p = $_.FullName; -not ($Exclude | Where-Object { $p -like $_ })
} | ForEach-Object {
    $rel = $_.FullName.Substring($Source.Length + 1)
    $dst = Join-Path $Target $rel
    if (-not (Test-Path $dst) -or (Get-FileHash $_.FullName).Hash -ne (Get-FileHash $dst).Hash) {
        New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
        Copy-Item $_.FullName $dst -Force
        $changed += $rel
    }
}

if ($changed.Count -eq 0) {
    Write-Output "Up to date."
} else {
    Write-Output "Updated $($changed.Count) file(s):"
    $changed | ForEach-Object { Write-Output "  $_" }
    Write-Output "Review SKILL.md manually if the source SKILL.md changed (reference map, checklist)."
}

# The repository is public: strip personal/client data, then verify nothing is left.
& (Join-Path $PSScriptRoot "sanitize-public.ps1")
& (Join-Path $PSScriptRoot "check-public.ps1")
exit $LASTEXITCODE
