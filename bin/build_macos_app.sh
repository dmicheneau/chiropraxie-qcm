#!/bin/bash
#
# Build QCM Chiropraxie standalone macOS app
# Usage: ./bin/build_macos_app.sh [--universal]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$REPO_ROOT/build"
DIST_DIR="$REPO_ROOT/dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🦴 QCM Chiropraxie - macOS Build${NC}"
echo "=================================="

# Parse arguments
UNIVERSAL=false
for arg in "$@"; do
    case $arg in
        --universal)
            UNIVERSAL=true
            shift
            ;;
    esac
done

# Check Python version
echo -e "\n${YELLOW}[1/5] Vérification de Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 non trouvé. Installez Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python version: $PYTHON_VERSION"

# Create/activate virtual environment
echo -e "\n${YELLOW}[2/5] Configuration de l'environnement...${NC}"
VENV_DIR="$REPO_ROOT/.venv-build"
if [ ! -d "$VENV_DIR" ]; then
    echo "Création du virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Install dependencies
echo -e "\n${YELLOW}[3/5] Installation des dépendances...${NC}"
pip install --upgrade pip wheel
pip install -r "$REPO_ROOT/requirements.txt"

# Rebuild bank.json
echo -e "\n${YELLOW}[4/5] Reconstruction de la banque de questions...${NC}"
cd "$REPO_ROOT"
python3 - <<'PY'
from pathlib import Path
from bank.build_bank import build_from_existing_decks, build_from_generate_qcm_400
import json
from datetime import datetime, timezone

repo_root = Path('.')
deck_questions = build_from_existing_decks(repo_root)
gen_questions = build_from_generate_qcm_400(repo_root)
all_questions = deck_questions + gen_questions

bank = {
    'version': '2.1.0',
    'generated': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    'metadata': {'questions_count': len(all_questions)},
    'questions': all_questions
}

out_path = Path('web/bank/bank.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"✅ {len(all_questions)} questions générées → {out_path}")
PY

# Build with PyInstaller
echo -e "\n${YELLOW}[5/5] Build de l'application...${NC}"
cd "$REPO_ROOT"

# Clean previous builds
rm -rf "$BUILD_DIR" "$DIST_DIR"

# Build options
PYINSTALLER_OPTS="--clean --noconfirm"
if [ "$UNIVERSAL" = true ]; then
    echo "🍎 Build Universal (Intel + Apple Silicon)..."
    PYINSTALLER_OPTS="$PYINSTALLER_OPTS --target-arch universal2"
fi

pyinstaller $PYINSTALLER_OPTS qcm_chiropraxie.spec

# Check result
APP_PATH="$DIST_DIR/QCM Chiropraxie.app"
if [ -d "$APP_PATH" ]; then
    echo -e "\n${GREEN}✅ Build réussi!${NC}"
    echo -e "Application: ${GREEN}$APP_PATH${NC}"
    
    # Show app size
    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
    echo "Taille: $APP_SIZE"
    
    # Optional: Create DMG
    if command -v create-dmg &> /dev/null; then
        echo -e "\n${YELLOW}Création du DMG...${NC}"
        DMG_PATH="$DIST_DIR/QCM_Chiropraxie.dmg"
        create-dmg \
            --volname "QCM Chiropraxie" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --app-drop-link 450 185 \
            "$DMG_PATH" \
            "$APP_PATH" || echo "⚠️  DMG creation skipped (install create-dmg: brew install create-dmg)"
    fi
else
    echo -e "${RED}❌ Build échoué${NC}"
    exit 1
fi

# Deactivate venv
deactivate

echo -e "\n${GREEN}🎉 Terminé!${NC}"
echo "Pour tester: open \"$APP_PATH\""
