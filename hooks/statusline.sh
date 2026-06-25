#!/usr/bin/env bash
# Prints a mode badge, e.g. [CAPYBARAA] (deep) or [CAPYBARAA:LEAN]. Empty when off/unset.
flag="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.capybaraa-active"
[ -f "$flag" ] || exit 0
level=$(head -n1 "$flag" | tr -d '[:space:]')
[ -z "$level" ] && exit 0
[ "$level" = "off" ] && exit 0
if [ "$level" = "deep" ]; then
  printf '\033[38;5;179m[CAPYBARAA]\033[0m'
else
  printf '\033[38;5;179m[CAPYBARAA:%s]\033[0m' "$(printf '%s' "$level" | tr '[:lower:]' '[:upper:]')"
fi
