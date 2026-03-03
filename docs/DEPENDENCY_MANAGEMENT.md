# Dependency Management

This project uses automated tools to keep dependencies up-to-date and secure.

## Automated Dependency Updates

### Dependabot
GitHub's Dependabot automatically checks for dependency updates and creates pull requests.

**Configuration**: `.github/dependabot.yml`

**What it does:**
- ✅ Checks for Python package updates (weekly on Mondays)
- ✅ Checks for GitHub Actions updates (weekly on Mondays)
- ✅ Groups minor and patch updates together
- ✅ Creates separate PRs for major version updates
- ✅ Automatically labels PRs for easy filtering

**How it works:**
1. Dependabot scans `requirements.txt` every Monday at 9 AM UTC
2. If updates are available, it creates pull requests
3. Each PR includes changelog and compatibility info
4. You review and merge the PR
5. CI/CD automatically tests the changes

### Dependency Review
Prevents vulnerable dependencies from being added via pull requests.

**Configuration**: `.github/workflows/dependency-review.yml`

**What it does:**
- ✅ Scans PRs for new dependencies
- ✅ Blocks PRs with moderate+ severity vulnerabilities
- ✅ Posts security findings as PR comments

### Security Scanning (CodeQL)
Analyzes code for security vulnerabilities.

**Configuration**: `.github/workflows/codeql-analysis.yml`

**What it does:**
- ✅ Scans Python code for security issues
- ✅ Runs on every push and PR
- ✅ Weekly scheduled scans (Monday 9 AM UTC)
- ✅ Results appear in GitHub Security tab

### Dependency Health Check
Regular monitoring of dependency health.

**Configuration**: `.github/workflows/dependency-check.yml`

**What it does:**
- ✅ Lists outdated packages weekly
- ✅ Scans for security vulnerabilities using pip-audit
- ✅ Creates GitHub issues if vulnerabilities found
- ✅ Can be triggered manually

## How to Handle Dependency Updates

### Automated Dependabot PRs

When Dependabot creates a PR:

1. **Review the PR**
   - Check the changelog link in the PR description
   - Look for breaking changes
   - Review the compatibility score

2. **Automatic Tests**
   - CI/CD automatically runs tests
   - Check if tests pass

3. **Merge or Close**
   - ✅ If tests pass and changes look good → Merge
   - ❌ If breaking changes → Close and investigate
   - ⏸️ If unsure → Request review or test locally

### Manual Dependency Updates

To update dependencies manually:

```bash
# Check for outdated packages
pip list --outdated

# Update a specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt

# Or update specific package in requirements.txt
# Edit the version in requirements.txt, then:
pip install -r requirements.txt

# Test the application
python3 src/capture_app.py
pytest tests/

# If all works, commit the changes
git add requirements.txt
git commit -m "deps: update package-name to v1.2.3"
```

### Security Vulnerabilities

When a security issue is found:

1. **GitHub creates an alert** in the Security tab
2. **Dependabot may auto-create a PR** with the fix
3. **Review and merge urgently** if it's a critical vulnerability
4. **Test thoroughly** after merging

### Ignoring Updates

To ignore specific dependency updates, edit `.github/dependabot.yml`:

```yaml
ignore:
  - dependency-name: "package-name"
    versions: ["1.x", "2.x"]  # Ignore these versions
```

## Dependency Pinning Strategy

Current strategy in `requirements.txt`:

```
opencv-python>=4.8.0    # Allow minor/patch updates
PyQt5>=5.15.0           # Allow minor/patch updates
numpy>=1.24.0           # Allow minor/patch updates
pyaudio>=0.2.13         # Allow minor/patch updates
```

**Why this approach:**
- ✅ Get security patches automatically
- ✅ Get bug fixes automatically
- ⚠️ Review major version updates manually

**Alternative strategies:**

1. **Strict pinning** (exact versions):
   ```
   opencv-python==4.8.0
   ```
   - Pro: Completely reproducible builds
   - Con: Miss security patches

2. **Lock files** (use pip-tools):
   ```bash
   pip install pip-tools
   pip-compile requirements.in -o requirements.txt
   ```
   - Pro: Exact versions with automatic resolution
   - Con: More complex workflow

## Monitoring

### GitHub Security Tab
View all security alerts and advisories:
`https://github.com/your-username/YatsurugiCapture/security`

### Dependabot Dashboard
View all Dependabot PRs:
`https://github.com/your-username/YatsurugiCapture/pulls?q=is:pr+author:app/dependabot`

### Actions Workflows
Monitor dependency checks:
`https://github.com/your-username/YatsurugiCapture/actions`

## Notifications

Configure notification preferences:
1. Go to GitHub Settings → Notifications
2. Under "Dependabot alerts" → Enable email notifications
3. Under "Actions" → Choose notification preferences

## Best Practices

✅ **Review Dependabot PRs weekly** - Don't let them pile up
✅ **Merge security updates ASAP** - Especially critical/high severity
✅ **Test locally for major updates** - Breaking changes need investigation
✅ **Keep Python version updated** - Update in CI/CD workflows too
✅ **Monitor the Security tab** - Check weekly for new advisories

## Troubleshooting

### Dependabot PRs not appearing
- Check `.github/dependabot.yml` syntax
- Ensure Dependabot is enabled in repo settings
- Check if updates are being ignored

### Merge conflicts in Dependabot PRs
- Rebase the PR or close and let Dependabot recreate it
- Or manually update and close the PR

### Test failures after dependency update
- Review changelog for breaking changes
- Update code to handle API changes
- Pin the previous version temporarily if needed

## Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [Python Packaging Guide](https://packaging.python.org/)
