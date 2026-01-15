#!/usr/bin/env bash
#
# Install git hooks for the GADB project
# Run this script after cloning the repository
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Installing GADB git hooks...${NC}"

# Get the root directory of the git repository
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
HOOKS_DIR="$GIT_ROOT/.git/hooks"

# Ensure we're in a git repository
if [ ! -d "$GIT_ROOT/.git" ]; then
    echo -e "${YELLOW}ERROR: Not in a git repository${NC}"
    exit 1
fi

# Create the pre-commit hook
echo -e "${GREEN}Creating pre-commit hook...${NC}"

cat > "$HOOKS_DIR/pre-commit" << 'HOOK_EOF'
#!/usr/bin/env bash
#
# Pre-commit hook to prevent committing sensitive files and secrets
# Installed as part of Phase 1: Critical Security Remediation
#

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Files and patterns that should never be committed
FORBIDDEN_PATTERNS=(
    "\.env$"
    "\.env\.local$"
    "\.env\.production$"
    "\.env\.development$"
    "\.env\.test$"
    "\.env\.staging$"
    "id_rsa$"
    "id_rsa\.pub$"
    "\.pem$"
    "\.key$"
    "\.p12$"
    "\.pfx$"
    "secrets\.json$"
    "credentials\.json$"
    "\.aws/credentials$"
    "\.ssh/config$"
)

# Get list of files being committed
FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Check for forbidden file patterns
echo -e "${GREEN}Running pre-commit security checks...${NC}"

FOUND_ISSUES=0

for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    matches=$(echo "$FILES" | grep -E "$pattern" || true)
    if [ -n "$matches" ]; then
        echo -e "${RED}ERROR: Attempting to commit potentially sensitive files:${NC}"
        echo "$matches" | while read -r file; do
            echo -e "  ${RED}✗${NC} $file"
        done
        FOUND_ISSUES=1
    fi
done

# Check for hardcoded secrets in files
echo -e "${GREEN}Checking for hardcoded secrets...${NC}"

# Patterns that might indicate secrets
SECRET_PATTERNS=(
    "password\s*=\s*['\"].*['\"]"
    "api[_-]?key\s*=\s*['\"].*['\"]"
    "secret[_-]?key\s*=\s*['\"].*['\"]"
    "private[_-]?key\s*=\s*['\"].*['\"]"
    "token\s*=\s*['\"].*['\"]"
    "AKIA[0-9A-Z]{16}"  # AWS Access Key ID
    "-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    for file in $FILES; do
        if [ -f "$file" ]; then
            # Skip checking files in .example or documentation directories
            if [[ "$file" == *".example"* ]] || [[ "$file" == *"docs/"* ]] || [[ "$file" == *"README"* ]] || [[ "$file" == *"CREDENTIALS_ROTATION.md"* ]]; then
                continue
            fi

            matches=$(grep -nHE "$pattern" "$file" || true)
            if [ -n "$matches" ]; then
                echo -e "${YELLOW}WARNING: Possible hardcoded secret in $file:${NC}"
                echo "$matches" | while read -r line; do
                    echo -e "  ${YELLOW}⚠${NC} $line"
                done
                FOUND_ISSUES=1
            fi
        fi
    done
done

# If issues were found, block the commit
if [ $FOUND_ISSUES -eq 1 ]; then
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}COMMIT BLOCKED: Security issues found!${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "To fix:"
    echo "1. Remove sensitive files from the commit:"
    echo "   git reset HEAD <file>"
    echo ""
    echo "2. Ensure .gitignore includes:"
    echo "   .env"
    echo "   .env.*"
    echo "   *.key"
    echo "   *.pem"
    echo ""
    echo "3. Remove hardcoded secrets and use environment variables"
    echo ""
    echo "If this is a false positive, you can bypass this hook with:"
    echo "   git commit --no-verify"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ All security checks passed${NC}"
exit 0
HOOK_EOF

# Make the hook executable
chmod +x "$HOOKS_DIR/pre-commit"

echo -e "${GREEN}✓ Pre-commit hook installed successfully${NC}"
echo ""
echo "The hook will now:"
echo "  • Prevent committing .env files"
echo "  • Prevent committing private keys and certificates"
echo "  • Warn about hardcoded secrets"
echo ""
echo "To bypass the hook (not recommended):"
echo "  git commit --no-verify"
echo ""
echo -e "${GREEN}Done!${NC}"
