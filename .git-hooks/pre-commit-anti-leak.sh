#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
#
# Pre-commit hook: blocks private-layer references from entering the template repo.
set -euo pipefail

BLOCKED_PATTERNS=(
    "_private/"
    "my-robot-stack/"
    "proprietary_"
    "LicenseRef-Proprietary"
    "All Rights Reserved"
)

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

FOUND=0
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$STAGED_FILES" | grep -qF "$pattern" 2>/dev/null; then
        echo "ANTI-LEAK BLOCKED: filename matches '$pattern'"
        FOUND=1
    fi
    if git diff --cached -U0 2>/dev/null | grep -qF "$pattern" 2>/dev/null; then
        echo "ANTI-LEAK BLOCKED: content matches '$pattern' in staged diff"
        FOUND=1
    fi
done

if [ "$FOUND" -eq 1 ]; then
    echo ""
    echo "Commit blocked by ip-guardian anti-leak hook."
    echo "Remove all references to private-layer paths/terms before committing."
    exit 1
fi

echo "ip-guardian: anti-leak check passed."
exit 0
