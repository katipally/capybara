# Prints a mode badge, e.g. [CAPYBARAA] (deep) or [CAPYBARAA:LEAN]. Empty when off/unset.
$flag = Join-Path ($env:CLAUDE_CONFIG_DIR ? $env:CLAUDE_CONFIG_DIR : (Join-Path $HOME ".claude")) ".capybaraa-active"
if (-not (Test-Path $flag)) { exit 0 }
$level = (Get-Content $flag -First 1).Trim()
if (-not $level -or $level -eq "off") { exit 0 }
$e = [char]27
if ($level -eq "deep") {
  [Console]::Write("$e[38;5;179m[CAPYBARAA]$e[0m")
} else {
  [Console]::Write("$e[38;5;179m[CAPYBARAA:$($level.ToUpper())]$e[0m")
}
