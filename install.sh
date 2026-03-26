#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/obslove/synthetic-profile-generator.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"
REPO_ROOT="${REPO_ROOT:-$HOME/Repositories}"
REPO_DIR="${REPO_DIR:-$REPO_ROOT/synthetic-profile-generator}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

log() {
  printf '[synthetic-profile-generator] %s\n' "$1"
}

fail() {
  printf '[synthetic-profile-generator] erro: %s\n' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "comando obrigatório ausente: $1"
}

ensure_repo() {
  mkdir -p "$REPO_ROOT"

  if [ -d "$REPO_DIR/.git" ]; then
    log "atualizando repositório em $REPO_DIR"
    git -C "$REPO_DIR" fetch origin "$REPO_BRANCH"
    git -C "$REPO_DIR" checkout "$REPO_BRANCH"
    git -C "$REPO_DIR" pull --ff-only origin "$REPO_BRANCH"
    return
  fi

  if [ -d "$PWD/.git" ] && [ -f "$PWD/pyproject.toml" ] && [ -f "$PWD/main.py" ]; then
    log "usando repositório atual em $PWD"
    REPO_DIR="$PWD"
    return
  fi

  log "clonando repositório em $REPO_DIR"
  git clone --branch "$REPO_BRANCH" "$REPO_URL" "$REPO_DIR"
}

ensure_venv() {
  if [ ! -x "$REPO_DIR/.venv/bin/python" ]; then
    log "criando ambiente virtual em $REPO_DIR/.venv"
    "$PYTHON_BIN" -m venv "$REPO_DIR/.venv"
  fi
}

install_project() {
  log "instalando dependências do projeto"
  "$REPO_DIR/.venv/bin/python" -m pip install --upgrade pip setuptools wheel
  "$REPO_DIR/.venv/bin/python" -m pip install -e "$REPO_DIR"
}

install_launcher() {
  mkdir -p "$BIN_DIR"
  cat >"$BIN_DIR/synthetic-profile-generator" <<EOF
#!/usr/bin/env bash
exec "$REPO_DIR/.venv/bin/synthetic-profile-generator" "\$@"
EOF
  chmod +x "$BIN_DIR/synthetic-profile-generator"
}

print_next_steps() {
  cat <<EOF

Instalação concluída.

Comando principal:
  synthetic-profile-generator generate --c BR --g male

Se "$BIN_DIR" ainda não estiver no PATH:
  export PATH="$BIN_DIR:\$PATH"

Execução direta sem PATH:
  "$REPO_DIR/.venv/bin/synthetic-profile-generator" generate --c BR --g male
EOF
}

main() {
  require_command git
  require_command "$PYTHON_BIN"
  ensure_repo
  ensure_venv
  install_project
  install_launcher
  print_next_steps
}

main "$@"
