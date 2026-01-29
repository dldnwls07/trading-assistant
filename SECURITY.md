# Security & Secrets Handling 🔐

Please follow these steps to keep secrets out of the repository:

1. Do NOT commit any real secret values (API keys, passwords, private keys, tokens).
2. Use a `.env` file locally for secrets and **do not** commit it. Use `.env.example` as a template.
3. Install `pre-commit` hooks to run basic checks and `detect-secrets` before each commit.

**참고:** 개발 원칙은 `DEVELOPMENT_GUIDELINES.md`에 정리되어 있으며, 보안/설정 분리는 해당 문서를 따릅니다.

Useful commands:
- Install hooks: `pip install pre-commit detect-secrets && pre-commit install`
- Initialize baseline (run locally, review results): `detect-secrets scan > .secrets.baseline`
- Run pre-commit on all files: `pre-commit run --all-files`

If you find an accidental secret committed, rotate the secret immediately and remove it from the repo history (use `git filter-repo` or `bfg`).

Report security issues privately instead of opening public issues.
