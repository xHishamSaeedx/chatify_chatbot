#!/bin/bash
set -euo pipefail

# ============================================================================
# Inputs
# ============================================================================
GITHUB_USERNAME="MustafaIdrisHasan"
FORK_REPO_NAME="chatify_chatbot"
UPSTREAM_URL="https://github.com/xHishamSaeedx/chatify_chatbot.git"
BRANCH_NAME="feat/in-memory-queue-system"
COMMIT_MSG="feat: implement in-memory queue system with AI fallback and personality verification"
OPEN_PR="yes"

# ============================================================================
# 1) Safety & Visibility
# ============================================================================
echo "============================================================================"
echo "Git Workflow Script"
echo "============================================================================"
echo ""

echo "=== Initial Git Status ==="
git status -sb || true
echo ""

echo "=== Initial Git Remotes ==="
git remote -v || echo "No remotes configured"
echo ""

# ============================================================================
# 2) Identity Check (non-fatal)
# ============================================================================
echo "=== Git Identity Check ==="
USER_NAME=$(git config user.name || echo "")
USER_EMAIL=$(git config user.email || echo "")

if [ -z "$USER_NAME" ] || [ -z "$USER_EMAIL" ]; then
    echo "⚠️  Git identity not fully configured:"
    [ -z "$USER_NAME" ] && echo "   Missing: user.name"
    [ -z "$USER_EMAIL" ] && echo "   Missing: user.email"
    echo ""
    echo "To set identity, run:"
    [ -z "$USER_NAME" ] && echo "   git config user.name 'Your Name'"
    [ -z "$USER_EMAIL" ] && echo "   git config user.email 'your.email@example.com'"
    echo ""
else
    echo "✓ Git identity configured:"
    echo "   Name:  $USER_NAME"
    echo "   Email: $USER_EMAIL"
    echo ""
fi

# ============================================================================
# 3) Remotes Setup
# ============================================================================
echo "=== Configuring Remotes ==="

HAS_ORIGIN=false
HAS_UPSTREAM=false
ORIGIN_URL=""
UPSTREAM_URL_CURRENT=""

# Check existing remotes
if git remote | grep -q "^origin$"; then
    HAS_ORIGIN=true
    ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")
fi

if git remote | grep -q "^upstream$"; then
    HAS_UPSTREAM=true
    UPSTREAM_URL_CURRENT=$(git remote get-url upstream 2>/dev/null || echo "")
fi

EXPECTED_ORIGIN="https://github.com/$GITHUB_USERNAME/$FORK_REPO_NAME.git"

# Handle origin
if [ "$HAS_ORIGIN" = true ]; then
    if [ "$ORIGIN_URL" = "$UPSTREAM_URL" ]; then
        echo "⚠️  Origin points to upstream. Renaming origin to upstream..."
        if [ "$HAS_UPSTREAM" = false ]; then
            git remote rename origin upstream
            HAS_UPSTREAM=true
            HAS_ORIGIN=false
        else
            git remote remove origin
            HAS_ORIGIN=false
        fi
    elif [ "$ORIGIN_URL" != "$EXPECTED_ORIGIN" ]; then
        echo "⚠️  Origin exists but points elsewhere: $ORIGIN_URL"
        echo "   Updating to: $EXPECTED_ORIGIN"
        git remote set-url origin "$EXPECTED_ORIGIN"
    else
        echo "✓ Origin already configured correctly"
    fi
else
    echo "➕ Adding origin: $EXPECTED_ORIGIN"
    git remote add origin "$EXPECTED_ORIGIN"
fi

# Handle upstream
if [ "$HAS_UPSTREAM" = true ]; then
    if [ "$UPSTREAM_URL_CURRENT" != "$UPSTREAM_URL" ]; then
        echo "⚠️  Upstream exists but points elsewhere. Updating..."
        git remote set-url upstream "$UPSTREAM_URL"
    else
        echo "✓ Upstream already configured correctly"
    fi
else
    echo "➕ Adding upstream: $UPSTREAM_URL"
    git remote add upstream "$UPSTREAM_URL"
fi

echo ""
echo "=== Updated Git Remotes ==="
git remote -v
echo ""

# ============================================================================
# 4) Sync with Upstream/Main
# ============================================================================
echo "=== Syncing with Upstream ==="

if git remote | grep -q "^upstream$"; then
    echo "Fetching from upstream..."
    git fetch upstream || echo "⚠️  Failed to fetch upstream (non-fatal)"
    
    if git show-ref --verify --quiet refs/remotes/upstream/main; then
        if ! git show-ref --verify --quiet refs/heads/main; then
            echo "Creating local main branch tracking upstream/main..."
            git checkout -b main upstream/main || git checkout main
        else
            echo "Local main branch exists"
            CURRENT_BRANCH=$(git branch --show-current)
            if [ "$CURRENT_BRANCH" != "main" ]; then
                git checkout main
            fi
            echo "Merging upstream/main into main..."
            git merge upstream/main || echo "⚠️  Merge had conflicts or issues (non-fatal)"
        fi
    else
        echo "⚠️  upstream/main not found, keeping current state"
    fi
else
    echo "⚠️  No upstream remote found, skipping sync"
fi

echo ""

# ============================================================================
# 5) Branch Handling
# ============================================================================
echo "=== Branch Handling ==="

if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME"; then
    echo "Branch '$BRANCH_NAME' exists, checking out..."
    git checkout "$BRANCH_NAME"
else
    echo "Creating new branch '$BRANCH_NAME' from current HEAD..."
    git checkout -b "$BRANCH_NAME"
fi

echo ""
echo "=== Staging Changes ==="
git add -A

if git diff --staged --quiet; then
    echo "⚠️  No changes to commit, skipping commit step"
else
    echo "Committing changes with message: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG" || {
        echo "⚠️  Commit failed (might be empty or already committed)"
    }
fi

echo ""
echo "=== Current Git Status ==="
git status -sb
echo ""

# ============================================================================
# 6) Push to Fork
# ============================================================================
echo "=== Pushing to Fork ==="

echo "Pushing branch '$BRANCH_NAME' to origin..."
if git push -u origin "$BRANCH_NAME" 2>&1; then
    echo "✓ Successfully pushed to origin"
else
    echo "⚠️  Push failed or branch already exists remotely"
    # Try to push anyway (might be force-push needed, but we don't auto-force)
    git push -u origin "$BRANCH_NAME" || true
fi

PR_URL="https://github.com/$GITHUB_USERNAME/$FORK_REPO_NAME/compare/main...$GITHUB_USERNAME:$BRANCH_NAME"
echo ""
echo "📋 PR URL: $PR_URL"
echo ""

# ============================================================================
# 7) Optional PR Creation
# ============================================================================
if [ "$OPEN_PR" = "yes" ]; then
    echo "=== Creating Pull Request ==="
    
    if command -v gh >/dev/null 2>&1; then
        if gh auth status >/dev/null 2>&1; then
            echo "GitHub CLI detected and authenticated"
            echo "Creating PR..."
            if gh pr create --fill --base main --head "$GITHUB_USERNAME:$BRANCH_NAME" 2>&1; then
                echo "✓ PR created successfully"
            else
                echo "⚠️  PR creation with --fill failed, trying with explicit title/body..."
                gh pr create \
                    --title "$COMMIT_MSG" \
                    --body "Auto-created from Cursor." \
                    --base main \
                    --head "$GITHUB_USERNAME:$BRANCH_NAME" || {
                    echo "⚠️  PR creation failed"
                    echo "📋 Please create PR manually: $PR_URL"
                }
            fi
        else
            echo "⚠️  GitHub CLI not authenticated"
            echo "   Run: gh auth login"
            echo "📋 Please create PR manually: $PR_URL"
        fi
    else
        echo "⚠️  GitHub CLI (gh) not found"
        echo "📋 Please create PR manually: $PR_URL"
    fi
else
    echo "PR creation skipped (OPEN_PR=no)"
fi

echo ""
echo "============================================================================"
echo "Workflow Complete"
echo "============================================================================"

# ============================================================================
# 8) Windows Detection
# ============================================================================
if [ -n "${OS:-}" ] && [ "$OS" = "Windows_NT" ]; then
    echo ""
    echo "=== PowerShell Equivalent (for reference) ==="
    echo "# Run these commands in PowerShell:"
    echo "# git checkout -b $BRANCH_NAME"
    echo "# git add -A"
    echo "# git commit -m '$COMMIT_MSG'"
    echo "# git push -u origin $BRANCH_NAME"
    echo "# Then open: $PR_URL"
fi

