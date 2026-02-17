#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
#   CS 1.6 Sprite API — GitHub Auto Push Script (Termux)
#   Asks for token + username, creates repo, pushes files
# ============================================================

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Banner ───────────────────────────────────────────────────
clear
echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║   CS 1.6 Sprite API — GitHub Auto Push (Termux) ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Step 1: Check / Install dependencies ─────────────────────
echo -e "${YELLOW}[1/6]${RESET} Checking dependencies..."

# git
if ! command -v git &> /dev/null; then
    echo -e "     ${YELLOW}git not found. Installing...${RESET}"
    pkg install -y git
else
    echo -e "     ${GREEN}✓ git found${RESET}"
fi

# curl
if ! command -v curl &> /dev/null; then
    echo -e "     ${YELLOW}curl not found. Installing...${RESET}"
    pkg install -y curl
else
    echo -e "     ${GREEN}✓ curl found${RESET}"
fi

# jq (for JSON parsing GitHub API response)
if ! command -v jq &> /dev/null; then
    echo -e "     ${YELLOW}jq not found. Installing...${RESET}"
    pkg install -y jq
else
    echo -e "     ${GREEN}✓ jq found${RESET}"
fi

echo ""

# ── Step 2: Collect credentials ──────────────────────────────
echo -e "${YELLOW}[2/6]${RESET} ${BOLD}Enter your GitHub credentials${RESET}"
echo ""

# GitHub username
echo -e "${CYAN}  GitHub Username:${RESET}"
read -r -p "  → " GH_USERNAME
GH_USERNAME=$(echo "$GH_USERNAME" | tr -d '[:space:]')
if [[ -z "$GH_USERNAME" ]]; then
    echo -e "${RED}  ✗ Username cannot be empty. Aborting.${RESET}"
    exit 1
fi

echo ""

# GitHub token
echo -e "${CYAN}  GitHub Personal Access Token (classic):${RESET}"
echo -e "  ${BLUE}(Get one: github.com/settings/tokens → New token → check 'repo')${RESET}"
read -r -s -p "  → " GH_TOKEN
echo ""
GH_TOKEN=$(echo "$GH_TOKEN" | tr -d '[:space:]')
if [[ -z "$GH_TOKEN" ]]; then
    echo -e "${RED}  ✗ Token cannot be empty. Aborting.${RESET}"
    exit 1
fi

echo ""

# Repo name
echo -e "${CYAN}  Repository name: ${RESET}(press Enter for default: ${BOLD}cs16-sprite-api${RESET})"
read -r -p "  → " REPO_NAME
REPO_NAME=$(echo "$REPO_NAME" | tr -d '[:space:]')
if [[ -z "$REPO_NAME" ]]; then
    REPO_NAME="cs16-sprite-api"
fi

echo ""

# Private or public
echo -e "${CYAN}  Make repo private? ${RESET}[y/N]:"
read -r -p "  → " PRIVATE_ANSWER
if [[ "$PRIVATE_ANSWER" =~ ^[Yy]$ ]]; then
    REPO_PRIVATE="true"
    VISIBILITY_LABEL="private"
else
    REPO_PRIVATE="false"
    VISIBILITY_LABEL="public"
fi

echo ""
echo -e "${GREEN}  ✓ Got it!${RESET}"
echo -e "     Username  : ${BOLD}$GH_USERNAME${RESET}"
echo -e "     Repo name : ${BOLD}$REPO_NAME${RESET}"
echo -e "     Visibility: ${BOLD}$VISIBILITY_LABEL${RESET}"
echo ""

# ── Step 3: Verify token with GitHub API ─────────────────────
echo -e "${YELLOW}[3/6]${RESET} Verifying token with GitHub..."

AUTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user)

if [[ "$AUTH_CHECK" != "200" ]]; then
    echo -e "${RED}  ✗ Token verification failed (HTTP $AUTH_CHECK).${RESET}"
    echo -e "${RED}    Check your token and try again.${RESET}"
    exit 1
fi

echo -e "     ${GREEN}✓ Token verified successfully${RESET}"
echo ""

# ── Step 4: Create repository on GitHub ──────────────────────
echo -e "${YELLOW}[4/6]${RESET} Creating GitHub repository '${BOLD}$REPO_NAME${RESET}'..."

CREATE_RESPONSE=$(curl -s \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    -X POST https://api.github.com/user/repos \
    -d "{
        \"name\": \"$REPO_NAME\",
        \"description\": \"CS 1.6 Sprite Generator API — Convert images and videos to .spr format with AI processing\",
        \"private\": $REPO_PRIVATE,
        \"auto_init\": false,
        \"has_issues\": true,
        \"has_projects\": false,
        \"has_wiki\": false
    }")

# Check if repo was created or already exists
HTTP_STATUS=$(echo "$CREATE_RESPONSE" | jq -r '.id // empty')
REPO_ERRORS=$(echo "$CREATE_RESPONSE" | jq -r '.errors[0].message // empty')

if [[ -n "$HTTP_STATUS" ]]; then
    REPO_URL="https://github.com/$GH_USERNAME/$REPO_NAME"
    echo -e "     ${GREEN}✓ Repository created: ${BOLD}$REPO_URL${RESET}"
elif [[ "$REPO_ERRORS" == *"already exists"* ]]; then
    echo -e "     ${YELLOW}⚠ Repository already exists — will push to it${RESET}"
    REPO_URL="https://github.com/$GH_USERNAME/$REPO_NAME"
else
    echo -e "${RED}  ✗ Failed to create repository.${RESET}"
    echo -e "${RED}    Response: $CREATE_RESPONSE${RESET}"
    exit 1
fi

echo ""

# ── Step 5: Prepare local git repo ───────────────────────────
echo -e "${YELLOW}[5/6]${RESET} Preparing files for push..."

SOURCE_DIR="$HOME/storage/downloads/sprite_api_advanced"
WORK_DIR="$HOME/sprite_api_push_tmp"

# Check source directory exists
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo -e "${RED}  ✗ Source folder not found: $SOURCE_DIR${RESET}"
    echo -e "${RED}    Make sure the sprite_api_advanced folder is in your Downloads.${RESET}"
    exit 1
fi

echo -e "     ${GREEN}✓ Source folder found: $SOURCE_DIR${RESET}"

# Clean and recreate work directory
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

# Copy all files
cp -r "$SOURCE_DIR"/. "$WORK_DIR/"
echo -e "     ${GREEN}✓ Files copied to work directory${RESET}"

# Count files
FILE_COUNT=$(find "$WORK_DIR" -type f | wc -l)
echo -e "     ${GREEN}✓ $FILE_COUNT files ready to push${RESET}"
echo ""

# Init git
cd "$WORK_DIR" || exit 1

git init -q
git config user.email "$GH_USERNAME@users.noreply.github.com"
git config user.name "$GH_USERNAME"

# Set remote with embedded token
REMOTE_URL="https://$GH_USERNAME:$GH_TOKEN@github.com/$GH_USERNAME/$REPO_NAME.git"
git remote add origin "$REMOTE_URL"

# Stage all files
git add -A

# Commit
COMMIT_MSG="🚀 CS 1.6 Sprite Generator API v2.0 — Advanced Edition

Features:
- REST API to convert images and videos to .spr format
- AI-powered background removal (black, white, green screen, auto)
- Smart auto-cropping and content centering
- Image enhancement (brightness, contrast, sharpness)
- Edge smoothing and anti-aliasing
- Noise reduction
- Color correction and gamma
- Duplicate frame removal for videos
- Docker deployment ready
- Full documentation and code examples"

git commit -q -m "$COMMIT_MSG"

echo -e "     ${GREEN}✓ Git commit created${RESET}"
echo ""

# ── Step 6: Push to GitHub ────────────────────────────────────
echo -e "${YELLOW}[6/6]${RESET} Pushing to GitHub..."
echo ""

PUSH_OUTPUT=$(git push -u origin main 2>&1)
PUSH_EXIT=$?

if [[ $PUSH_EXIT -ne 0 ]]; then
    # Try 'master' branch if 'main' fails
    PUSH_OUTPUT=$(git push -u origin master 2>&1)
    PUSH_EXIT=$?
fi

if [[ $PUSH_EXIT -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════╗${RESET}"
    echo -e "${GREEN}${BOLD}║            ✅  PUSH SUCCESSFUL!                  ║${RESET}"
    echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════╝${RESET}"
    echo ""
    echo -e "  ${BOLD}Repository URL:${RESET}"
    echo -e "  ${CYAN}${BOLD}$REPO_URL${RESET}"
    echo ""
    echo -e "  ${BOLD}Files pushed:${RESET} $FILE_COUNT files"
    echo ""
    echo -e "  ${BOLD}What's inside:${RESET}"
    echo -e "  ${GREEN}✓${RESET} advanced_processor.py  — AI processing engine"
    echo -e "  ${GREEN}✓${RESET} sprite_generator.py    — SPR format generator"
    echo -e "  ${GREEN}✓${RESET} main.py                — FastAPI application"
    echo -e "  ${GREEN}✓${RESET} Dockerfile             — Container definition"
    echo -e "  ${GREEN}✓${RESET} docker-compose.yml     — Local dev setup"
    echo -e "  ${GREEN}✓${RESET} render.yaml            — One-click Render deploy"
    echo -e "  ${GREEN}✓${RESET} requirements.txt       — Python dependencies"
    echo -e "  ${GREEN}✓${RESET} API_COMPLETE_REFERENCE.md — Full API docs"
    echo ""
    echo -e "  ${BOLD}Deploy to Render in 1 click:${RESET}"
    echo -e "  ${BLUE}https://render.com/deploy${RESET}"
    echo ""
else
    echo -e "${RED}${BOLD}  ✗ Push failed.${RESET}"
    echo -e "${RED}    $PUSH_OUTPUT${RESET}"
    echo ""
    echo -e "${YELLOW}  Possible fixes:${RESET}"
    echo -e "  • Make sure your token has the ${BOLD}'repo'${RESET} scope"
    echo -e "  • Token might be expired — create a new one"
    echo -e "  • Repo might have existing commits (try a different repo name)"
    cd "$HOME" && rm -rf "$WORK_DIR"
    exit 1
fi

# ── Cleanup ───────────────────────────────────────────────────
cd "$HOME" && rm -rf "$WORK_DIR"

echo -e "${GREEN}  ✓ Temporary files cleaned up${RESET}"
echo ""
echo -e "${MAGENTA}${BOLD}  Happy modding! 🎮${RESET}"
echo ""
