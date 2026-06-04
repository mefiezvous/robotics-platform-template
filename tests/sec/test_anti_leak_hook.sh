#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
#
# Smoke test for .git-hooks/pre-commit-anti-leak.sh
# Synthesizes a fake staged diff containing each BLOCKED_PATTERNS entry
# and asserts the hook exits 1 (blocked).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOK="$REPO_ROOT/.git-hooks/pre-commit-anti-leak.sh"

if [ ! -f "$HOOK" ]; then
    echo "FAIL: hook not found at $HOOK"
    exit 1
fi

BLOCKED_PATTERNS=(
    "_private/"
    "my-robot-stack/"
    "proprietary_"
    "LicenseRef-Proprietary"
    "All Rights Reserved"
)

PASS=0
FAIL=0

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    # Create a temporary git repo with a staged diff that contains the blocked pattern
    TMPDIR_TEST="$(mktemp -d)"
    (
        cd "$TMPDIR_TEST"
        git init -q
        git config user.email "test@example.com"
        git config user.name "Test"
        # Create and stage a file whose content includes the blocked pattern
        echo "test content: $pattern" > test_file.txt
        git add test_file.txt

        # Run the hook — it must exit 1
        if bash "$HOOK" 2>/dev/null; then
            echo "FAIL: hook did NOT block pattern: '$pattern'"
            exit 1
        else
            echo "PASS: hook correctly blocked pattern: '$pattern'"
        fi
    )
    STATUS=$?
    rm -rf "$TMPDIR_TEST"
    if [ "$STATUS" -eq 0 ]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "Anti-leak smoke test results: $PASS passed, $FAIL failed out of ${#BLOCKED_PATTERNS[@]} patterns."

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
