#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
#   CS 1.6 Sprite API — GitHub UPDATE Script (Termux)
#   Pulls latest from repo, syncs all local files, pushes
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Banner ────────────────────────────────────────────────────
clear
echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║   CS 1.6 Sprite API — GitHub Updater (Termux)   ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${DIM}  Syncs /sdcard/Download/sprite_api_advanced/ → GitHub${RESET}"
echo ""

# ── Step 1: Dependencies ──────────────────────────────────────
echo -e "${YELLOW}[1/6]${RESET} Checking dependencies..."

for pkg in git curl jq; do
  if ! command -v "$pkg" &>/dev/null; then
    echo -e "     ${YELLOW}Installing $pkg...${RESET}"
    pkg install -y "$pkg" -q
  else
    echo -e "     ${GREEN}✓ $pkg${RESET}"
  fi
done
echo ""

# ── Step 2: Credentials ───────────────────────────────────────
echo -e "${YELLOW}[2/6]${RESET} ${BOLD}GitHub credentials${RESET}"
echo ""

# Check for saved config
CONFIG_FILE="$HOME/.sprite_api_github"
if [[ -f "$CONFIG_FILE" ]]; then
  echo -e "     ${DIM}Found saved config at ~/.sprite_api_github${RESET}"
  echo -e "${CYAN}     Load saved credentials? ${RESET}[Y/n]:"
  read -r -p "     → " USE_SAVED
  if [[ ! "$USE_SAVED" =~ ^[Nn]$ ]]; then
    source "$CONFIG_FILE"
    echo -e "     ${GREEN}✓ Loaded: ${BOLD}$GH_USERNAME${RESET} / ${BOLD}$REPO_NAME${RESET}"
    echo ""
  else
    rm -f "$CONFIG_FILE"
  fi
fi

# Ask for credentials if not loaded
if [[ -z "$GH_USERNAME" ]]; then
  echo -e "${CYAN}  GitHub Username:${RESET}"
  read -r -p "  → " GH_USERNAME
  GH_USERNAME=$(echo "$GH_USERNAME" | tr -d '[:space:]')
  [[ -z "$GH_USERNAME" ]] && echo -e "${RED}  ✗ Empty. Aborting.${RESET}" && exit 1
  echo ""
fi

if [[ -z "$GH_TOKEN" ]]; then
  echo -e "${CYAN}  GitHub Token (classic, needs 'repo' scope):${RESET}"
  echo -e "  ${BLUE}github.com/settings/tokens${RESET}"
  read -r -s -p "  → " GH_TOKEN
  echo ""
  GH_TOKEN=$(echo "$GH_TOKEN" | tr -d '[:space:]')
  [[ -z "$GH_TOKEN" ]] && echo -e "${RED}  ✗ Empty. Aborting.${RESET}" && exit 1
  echo ""
fi

if [[ -z "$REPO_NAME" ]]; then
  echo -e "${CYAN}  Repository name:${RESET} (Enter = ${BOLD}cs16-sprite-api${RESET})"
  read -r -p "  → " REPO_NAME
  REPO_NAME=$(echo "$REPO_NAME" | tr -d '[:space:]')
  [[ -z "$REPO_NAME" ]] && REPO_NAME="cs16-sprite-api"
  echo ""
fi

# Ask commit message
echo -e "${CYAN}  Commit message:${RESET} (Enter = auto timestamp)"
read -r -p "  → " COMMIT_MSG
if [[ -z "$COMMIT_MSG" ]]; then
  COMMIT_MSG="🔄 Update $(date '+%Y-%m-%d %H:%M:%S')"
fi
echo ""

# Save credentials for next run
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo -e "${CYAN}  Save credentials for future runs? ${RESET}[Y/n]:"
  read -r -p "  → " SAVE_CREDS
  echo ""
  if [[ ! "$SAVE_CREDS" =~ ^[Nn]$ ]]; then
    cat > "$CONFIG_FILE" <<EOF
GH_USERNAME="$GH_USERNAME"
GH_TOKEN="$GH_TOKEN"
REPO_NAME="$REPO_NAME"
EOF
    chmod 600 "$CONFIG_FILE"
    echo -e "     ${GREEN}✓ Saved to ~/.sprite_api_github${RESET}"
    echo ""
  fi
fi

echo -e "     ${GREEN}✓ Username : ${BOLD}$GH_USERNAME${RESET}"
echo -e "     ${GREEN}✓ Repo     : ${BOLD}$REPO_NAME${RESET}"
echo -e "     ${GREEN}✓ Message  : ${BOLD}$COMMIT_MSG${RESET}"
echo ""

# ── Step 3: Verify token ──────────────────────────────────────
echo -e "${YELLOW}[3/6]${RESET} Verifying token..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $GH_TOKEN" \
  https://api.github.com/user)

if [[ "$HTTP_CODE" != "200" ]]; then
  echo -e "${RED}  ✗ Token invalid or expired (HTTP $HTTP_CODE)${RESET}"
  echo -e "${RED}    Delete ~/.sprite_api_github and re-run to enter new token.${RESET}"
  exit 1
fi

echo -e "     ${GREEN}✓ Token OK${RESET}"
echo ""

# ── Step 4: Verify repo exists ────────────────────────────────
echo -e "${YELLOW}[4/6]${RESET} Checking repo ${BOLD}$GH_USERNAME/$REPO_NAME${RESET}..."

REPO_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/$GH_USERNAME/$REPO_NAME")

if [[ "$REPO_CHECK" == "404" ]]; then
  echo -e "     ${YELLOW}⚠ Repo not found — creating it...${RESET}"
  curl -s -X POST \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"CS 1.6 Sprite Generator API\",\"private\":false}" \
    > /dev/null
  echo -e "     ${GREEN}✓ Repo created${RESET}"
elif [[ "$REPO_CHECK" == "200" ]]; then
  echo -e "     ${GREEN}✓ Repo found${RESET}"
else
  echo -e "${RED}  ✗ Unexpected response: $REPO_CHECK${RESET}"
  exit 1
fi

REPO_URL="https://github.com/$GH_USERNAME/$REPO_NAME"
echo ""

# ── Step 5: Sync files ────────────────────────────────────────
echo -e "${YELLOW}[5/6]${RESET} Syncing files..."

SOURCE_DIR="$HOME/storage/downloads/sprite_api_advanced"
WORK_DIR="$HOME/.sprite_api_update_tmp"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo -e "${RED}  ✗ Source not found: $SOURCE_DIR${RESET}"
  echo -e "${RED}    Put sprite_api_advanced/ folder in Downloads.${RESET}"
  exit 1
fi

echo -e "     ${GREEN}✓ Source: $SOURCE_DIR${RESET}"

# ── Clone existing repo into tmp ──
rm -rf "$WORK_DIR"
echo -e "     Cloning existing repo..."

CLONE_OUTPUT=$(git clone \
  "https://$GH_USERNAME:$GH_TOKEN@github.com/$GH_USERNAME/$REPO_NAME.git" \
  "$WORK_DIR" 2>&1)

CLONE_EXIT=$?

# If clone failed (empty repo / new repo), init fresh
if [[ $CLONE_EXIT -ne 0 ]]; then
  echo -e "     ${YELLOW}⚠ Clone failed (probably empty repo) — starting fresh${RESET}"
  mkdir -p "$WORK_DIR"
  cd "$WORK_DIR" || exit 1
  git init -q
  git remote add origin \
    "https://$GH_USERNAME:$GH_TOKEN@github.com/$GH_USERNAME/$REPO_NAME.git"
else
  echo -e "     ${GREEN}✓ Cloned existing repo${RESET}"
  cd "$WORK_DIR" || exit 1
fi

# Configure git identity
git config user.email "$GH_USERNAME@users.noreply.github.com"
git config user.name  "$GH_USERNAME"

# ── Wipe old files (keep .git), copy fresh ones ──
echo -e "     Replacing files with latest version..."
find "$WORK_DIR" -mindepth 1 -not -path "*/.git*" -delete 2>/dev/null

cp -r "$SOURCE_DIR"/. "$WORK_DIR/"

FILE_COUNT=$(find "$WORK_DIR" -not -path "*/.git*" -type f | wc -l)
echo -e "     ${GREEN}✓ $FILE_COUNT files staged${RESET}"

# Show what changed
echo ""
echo -e "     ${DIM}Changed files:${RESET}"
git add -A
git status --short | sed 's/^/       /'
echo ""

# ── Step 6: Commit + Push ─────────────────────────────────────
echo -e "${YELLOW}[6/6]${RESET} Committing and pushing..."

# Check if there is anything to commit
if git diff --cached --quiet; then
  echo -e "     ${YELLOW}⚠ No changes detected — repo is already up to date.${RESET}"
  cd "$HOME" && rm -rf "$WORK_DIR"
  echo ""
  echo -e "${GREEN}${BOLD}  ✓ Nothing to update. All good!${RESET}"
  echo -e "  ${CYAN}${BOLD}  $REPO_URL${RESET}"
  echo ""
  exit 0
fi

git commit -q -m "$COMMIT_MSG"

# Try main branch first, then master
PUSH_OUT=$(git push origin main 2>&1)
if [[ $? -ne 0 ]]; then
  git branch -M main
  PUSH_OUT=$(git push -u origin main 2>&1)
fi

PUSH_EXIT=$?

# ── Result ────────────────────────────────────────────────────
echo ""
if [[ $PUSH_EXIT -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════╗${RESET}"
  echo -e "${GREEN}${BOLD}║            ✅  UPDATE SUCCESSFUL!                ║${RESET}"
  echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════╝${RESET}"
  echo ""
  echo -e "  ${BOLD}Repository:${RESET}  ${CYAN}${BOLD}$REPO_URL${RESET}"
  echo -e "  ${BOLD}Files pushed:${RESET} $FILE_COUNT"
  echo -e "  ${BOLD}Commit:${RESET}      $COMMIT_MSG"
  echo ""
  echo -e "  ${BOLD}Live API:${RESET}"
  echo -e "  ${CYAN}https://cs16-sprite-api.onrender.com${RESET}"
  echo -e "  ${CYAN}https://cs16-sprite-api.onrender.com/docs${RESET}"
  echo ""
  echo -e "  ${DIM}Render will auto-redeploy in ~1-2 minutes.${RESET}"
  echo ""
else
  echo -e "${RED}${BOLD}  ✗ Push failed:${RESET}"
  echo -e "${RED}    $PUSH_OUT${RESET}"
  echo ""
  echo -e "${YELLOW}  Tips:${RESET}"
  echo -e "  • Token may need 'repo' scope"
  echo -e "  • Delete ${BOLD}~/.sprite_api_github${RESET} to reset saved creds"
  cd "$HOME" && rm -rf "$WORK_DIR"
  exit 1
fi

# ── Cleanup ───────────────────────────────────────────────────
cd "$HOME" && rm -rf "$WORK_DIR"
echo -e "${GREEN}  ✓ Temp files cleaned${RESET}"
echo ""
echo -e "${MAGENTA}${BOLD}  Happy modding! 🎮${RESET}"
echo ""
