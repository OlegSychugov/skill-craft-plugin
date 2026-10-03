# Fail if the repository contains personal or client data that must not be public.
# Run before every push. Exit code 1 = findings (fix via sanitize-public.ps1 rules).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts/check-public.ps1

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Utf8 = New-Object System.Text.UTF8Encoding($false)

$Deny = [ordered]@{
    'ФИО с отчеством'          = '[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(вич|вна|ична)\b'
    'Фамилия И.О.'             = '[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s?[А-ЯЁ]\.|[А-ЯЁ]\.\s?[А-ЯЁ]\.\s?[А-ЯЁ][а-яё]{2,}'
    'e-mail'                   = '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}'
    'телефон'                  = '(\+7|\b8)[\s(-]*\d{3}[\s)-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}\b'
    'антивирусная вставка'     = 'kaspersky-labs'
    'рабочее пространство'     = '/workspaces/[0-9a-f]{8}-'
    'токен в URL'              = 'https?://[^/\s:@]+:[^@\s]+@'
    'GitHub/GitLab токен'      = 'ghp_[A-Za-z0-9]{20,}|github_pat_|glpat-'
    'путь профиля Windows'     = 'C:\\Users\\[^\\\s]+'
    'абсолютный путь Windows'  = '\b[C-Z]:\\[A-Za-zА-Яа-яЁё0-9]'
}
# Literal patterns from the gitignored local sanitize rules are checked too
$Local = Join-Path $PSScriptRoot "sanitize-rules.local.json"
if (Test-Path $Local) {
    $i = 0
    foreach ($r in @([IO.File]::ReadAllText($Local, $Utf8) | ConvertFrom-Json)) { foreach ($x in $r) { $i++; $Deny["локальное правило $i"] = $x.Pattern } }
}
# Known false positives (literal substrings)
$Allow = @('noreply@anthropic.com', 'black@0.')

$TextExt = '.md', '.html', '.json', '.css', '.py', '.yaml', '.ps1', '.txt', ''
$self = $MyInvocation.MyCommand.Path
$hits = @()
Get-ChildItem $Root -Recurse -File | Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and $TextExt -contains $_.Extension -and $_.FullName -ne $self -and $_.Name -ne 'sanitize-public.ps1' -and $_.Name -notlike '*.local.json'
} | ForEach-Object {
    $file = $_
    $n = 0
    foreach ($line in [IO.File]::ReadAllLines($file.FullName, $Utf8)) {
        $n++
        foreach ($k in $Deny.Keys) {
            foreach ($m in [regex]::Matches($line, $Deny[$k])) {
                $ctx = $line.Substring([Math]::Max(0, $m.Index - 10), [Math]::Min(60, $line.Length - [Math]::Max(0, $m.Index - 10)))
                if ($Allow | Where-Object { $ctx.Contains($_) }) { continue }
                $hits += "{0}:{1} [{2}] {3}" -f $file.FullName.Substring($Root.Length + 1), $n, $k, $m.Value
            }
        }
    }
}

if ($hits.Count -eq 0) { Write-Output "check-public: OK"; exit 0 }
Write-Output "check-public: $($hits.Count) finding(s)"
$hits | ForEach-Object { Write-Output "  $_" }
exit 1
