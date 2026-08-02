#!/usr/bin/env bash
set -euo pipefail

LABEL="io.github.emperorkundis.mike.omnivoice"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OMNI_PYTHON="${MIKE_OMNIVOICE_PYTHON:-$REPO/.venv-omnivoice/bin/python}"
SERVER="$REPO/scripts/omnivoice_server.py"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="${MIKE_HOME:-$HOME/Library/Application Support/MIKE}/logs"
OMNI_BASE_URL="${MIKE_OMNIVOICE_URL:-http://127.0.0.1:8130}"
if [[ ! "$OMNI_BASE_URL" =~ ^http://127\.0\.0\.1:[0-9]{4,5}/?$ ]]; then
  echo "MIKE_OMNIVOICE_URL musí být http://127.0.0.1:<port>." >&2
  exit 2
fi
HEALTH_URL="${OMNI_BASE_URL%/}/health"
DOMAIN="gui/$(id -u)"

is_loaded() {
  launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1
}

install_service() {
  if curl -fsS --max-time 2 "$HEALTH_URL" >/dev/null 2>&1; then
    echo "Na $HEALTH_URL už odpovídá kompatibilní OmniVoice; nic neměním."
    return 0
  fi
  if [[ ! -x "$OMNI_PYTHON" ]]; then
    echo "Chybí $OMNI_PYTHON; nejprve vytvořte .venv-omnivoice podle README." >&2
    return 2
  fi
  mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"
  chmod 700 "$LOG_DIR"
  umask 077
  cp "$REPO/scripts/omnivoice_service.plist.template" "$PLIST"
  plutil -replace Label -string "$LABEL" "$PLIST"
  plutil -replace ProgramArguments.0 -string "$OMNI_PYTHON" "$PLIST"
  plutil -replace ProgramArguments.1 -string "$SERVER" "$PLIST"
  plutil -replace WorkingDirectory -string "$REPO" "$PLIST"
  plutil -replace EnvironmentVariables.MIKE_HOME -string \
    "${MIKE_HOME:-$HOME/Library/Application Support/MIKE}" "$PLIST"
  plutil -replace StandardOutPath -string "$LOG_DIR/omnivoice.log" "$PLIST"
  plutil -replace StandardErrorPath -string "$LOG_DIR/omnivoice-error.log" "$PLIST"
  chmod 600 "$PLIST"
  launchctl bootstrap "$DOMAIN" "$PLIST"
  launchctl kickstart -k "$DOMAIN/$LABEL"
  echo "OmniVoice LaunchAgent nainstalován: $PLIST"
}

stop_service() {
  if is_loaded; then
    launchctl bootout "$DOMAIN/$LABEL"
    echo "OmniVoice LaunchAgent zastaven."
  else
    echo "OmniVoice LaunchAgent neběží."
  fi
}

uninstall_service() {
  stop_service
  if [[ -f "$PLIST" ]]; then
    rm -f "$PLIST"
    echo "Odstraněn pouze $PLIST; modelová cache a data zůstala zachována."
  fi
}

status_service() {
  is_loaded && echo "LaunchAgent: načten" || echo "LaunchAgent: nenačten"
  curl -fsS --max-time 3 "$HEALTH_URL" || true
  echo
}

case "${1:-}" in
  install) install_service ;;
  start) exec "$OMNI_PYTHON" "$SERVER" ;;
  stop) stop_service ;;
  status) status_service ;;
  uninstall) uninstall_service ;;
  *) echo "Použití: $0 {install|start|stop|status|uninstall}" >&2; exit 2 ;;
esac
