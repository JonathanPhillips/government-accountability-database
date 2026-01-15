# GitHub Repository Setup Guide

**Created**: 2026-01-14
**Purpose**: Guide for publishing GADB to GitHub

---

## Repository Visibility Decision

### Public Repository (Recommended) ✅

**Pros**:
- Demonstrates commitment to transparency and accountability
- Allows community contributions and collaboration
- Free unlimited GitHub Actions minutes
- Can showcase your work to potential employers/collaborators
- Helps others build similar accountability systems
- Aligns with project mission (government accountability through transparency)

**Cons**:
- Code is visible to everyone
- Requires maintaining public issue tracker
- May attract unwanted attention

**Recommendation**: **Public** - The project's mission is government accountability and transparency, so a public repository aligns with those values. The codebase contains no proprietary technology and could benefit from community contributions.

### Private Repository

**Use Case**: If you're developing this for a specific organization that requires privacy, or if you want to test/polish before going public.

**Note**: You can always start private and make it public later.

---

## Licensing (Already Configured) ✅

**Current License**: MIT License

**What This Means**:
- ✅ Anyone can use, modify, and distribute the code
- ✅ Commercial use is allowed
- ✅ No warranty or liability
- ✅ Must include copyright notice and license

**Why MIT**:
- Most permissive open source license
- Encourages adoption and contribution
- Simple and well-understood
- Compatible with most other licenses

**Alternative Licenses to Consider**:
- **GPL v3**: Requires derivatives to also be open source (more restrictive)
- **Apache 2.0**: Similar to MIT but includes patent protection
- **AGPL v3**: Like GPL but also covers network use (strongest copyleft)

**Decision**: Keep MIT unless you have specific reasons to change.

---

## Pre-Push Checklist ✅

### Security Review
- [x] No secrets in git history (verified - .env files never committed)
- [x] .gitignore properly configured
- [x] Pre-commit hook installed and tested
- [x] Credentials rotation documentation created
- [x] Rate limiting implemented and tested
- [x] Default admin password change enforced
- [ ] Review all .env.example files for sensitive info
- [ ] Ensure no hardcoded credentials in code

### Code Quality
- [x] All tests passing (126 tests)
- [x] Documentation complete (README, DEPLOYMENT, CONTRIBUTING, SECURITY)
- [x] Code follows consistent style
- [ ] Run final linting check
- [ ] Remove any debug print statements
- [ ] Remove commented-out code

### Repository Setup
- [ ] Create GitHub repository (public/private)
- [ ] Add repository description
- [ ] Add topics/tags (government, accountability, fastapi, react, typescript)
- [ ] Configure branch protection rules
- [ ] Set up GitHub Actions workflows (already in .github/workflows/)
- [ ] Add issue templates (already in .github/ISSUE_TEMPLATE/)
- [ ] Add pull request template (already in .github/)

### Documentation Updates
- [x] Update README with accurate GitHub URLs
- [x] Security features documented
- [ ] Replace placeholder URLs with actual repository URL
- [ ] Add contributors section (optional)
- [ ] Add shields/badges with actual values

---

## Step-by-Step GitHub Setup

### 1. Create GitHub Repository

```bash
# Option A: Using GitHub CLI
gh repo create govt_accountability --public --description "Government accountability incident tracking database"

# Option B: Using web interface
# Go to https://github.com/new
# Repository name: govt_accountability
# Description: Government accountability incident tracking database
# Visibility: Public
# Do NOT initialize with README (you already have one)
```

### 2. Update Repository URLs in Documentation

Replace these placeholder URLs in your files:
- `README.md`: Line 110, 476
- `.github/ISSUE_TEMPLATE/*.yml`: Update repository references
- Any other files referencing `JonathanPhillips/government-accountability-database`

**Find and replace**:
```bash
# Find all occurrences
grep -r "JonathanPhillips/government-accountability-database" .
grep -r "yourdomain.com" .

# Replace with your actual GitHub username/org
# Example: github.com/yourusername/govt_accountability
```

### 3. Add Remote and Push

```bash
# Add GitHub remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/govt_accountability.git

# Or use SSH
git remote add origin git@github.com:USERNAME/govt_accountability.git

# Verify remote
git remote -v

# Push all branches and tags
git push -u origin main
git push --tags
```

### 4. Configure Repository Settings

**General Settings**:
- Description: "Comprehensive database system for tracking government accountability incidents"
- Website: (Your deployment URL if you have one)
- Topics: `government`, `accountability`, `fastapi`, `react`, `typescript`, `postgresql`, `docker`, `kubernetes`
- Features: Enable Issues, Discussions (optional), Projects (optional)

**Branch Protection** (Settings → Branches → Add rule):
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators (optional)

**GitHub Actions** (Settings → Actions):
- ✅ Allow all actions and reusable workflows
- Your workflows are in `.github/workflows/` and will run automatically

**Secrets** (Settings → Secrets and variables → Actions):
Add these secrets for CI/CD if needed:
- `DOCKER_USERNAME`: For Docker Hub (if building/pushing images)
- `DOCKER_PASSWORD`: Docker Hub token
- `SENTRY_DSN`: For error tracking (optional)

### 5. Create Initial Release (Optional)

```bash
# Tag your current version
git tag -a v1.0.0 -m "Release v1.0.0 - Production Ready"
git push origin v1.0.0

# Create release on GitHub
gh release create v1.0.0 \
  --title "v1.0.0 - Production Ready" \
  --notes "First production release with complete feature set"
```

### 6. Add Repository Badges

Add these to the top of README.md (update USERNAME):

```markdown
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-blue.svg)](https://react.dev)
[![Tests](https://github.com/USERNAME/govt_accountability/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/govt_accountability/actions)
[![Coverage](https://img.shields.io/badge/coverage-44%25-yellow.svg)](https://github.com/USERNAME/govt_accountability)
```

---

## Post-Push Actions

### Enable GitHub Features

**Issues**:
- Issue templates are already configured in `.github/ISSUE_TEMPLATE/`
- Users can report bugs, request features, or ask questions

**Discussions** (Optional but Recommended):
- Good for community Q&A
- Feature discussions
- General announcements
- Settings → Features → Enable Discussions

**Projects** (Optional):
- Track ongoing work with Kanban boards
- Useful if you want community to see roadmap

**Security**:
- Settings → Security → Enable Dependabot alerts
- Settings → Security → Enable Dependabot security updates
- GitHub will automatically scan for vulnerable dependencies

### Set Up GitHub Pages (Optional)

If you want to host documentation:
- Settings → Pages
- Source: Deploy from a branch
- Branch: main, folder: /docs (create docs folder)
- Your site will be at: https://USERNAME.github.io/govt_accountability

### Add Community Files

These are already included:
- ✅ LICENSE
- ✅ README.md
- ✅ CONTRIBUTING.md
- ✅ SECURITY.md
- ✅ CHANGELOG.md
- ✅ CODE_OF_CONDUCT (create if needed for community projects)

---

## Community & Contributions

### If You Want Contributors

**Add to README**:
- Contributor guidelines (already in CONTRIBUTING.md)
- Code of conduct
- Communication channels (Discord, Slack, etc.)

**Be Responsive**:
- Respond to issues within 48 hours
- Review pull requests promptly
- Be welcoming to new contributors

### If You Don't Want Contributors

**Add to README**:
```markdown
## Contributing

This is a personal project and I'm not accepting contributions at this time.
However, feel free to fork and modify for your own use under the MIT license.
```

---

## Final Verification

Before making repository public:

```bash
# 1. Ensure all tests pass
cd backend && pytest tests/ -v
cd ../frontend && npm test

# 2. Verify no secrets
git log --all --full-history -- "*.env"  # Should be empty

# 3. Check for hardcoded secrets
grep -r "password.*=.*['\"].*['\"]" backend/app/ frontend/src/ || echo "No hardcoded passwords found"

# 4. Verify pre-commit hook works
cd backend && ./scripts/install-hooks.sh
# Try committing a .env file to test the hook blocks it

# 5. Build Docker images to ensure they work
docker-compose build

# 6. Run full CI/CD pipeline locally (if you have act installed)
act -l  # List workflows
```

---

## Maintenance After Publishing

**Weekly**:
- Check for new issues
- Review dependabot alerts
- Update dependencies if needed

**Monthly**:
- Review open issues and PRs
- Update documentation if needed
- Check GitHub Actions usage (if using paid features)

**Quarterly**:
- Review security policies
- Update roadmap
- Consider writing a blog post about progress

---

## Example GitHub Profile README Badge

If you want to showcase this project in your GitHub profile:

```markdown
### 🏛️ Government Accountability Database

A production-ready full-stack application for tracking government accountability incidents.
Built with FastAPI, React, PostgreSQL, and Docker.

[View Repository](https://github.com/USERNAME/govt_accountability) |
[Live Demo](your-deployment-url) |
[Documentation](your-docs-url)

**Tech Stack**: Python, FastAPI, React, TypeScript, PostgreSQL, Redis, Docker, Kubernetes
```

---

## Questions to Consider

1. **Repository Name**: Keep `govt_accountability` or rename?
   - Current name is clear and descriptive ✅
   - Consider: `government-accountability-db`, `gadb`, `accountability-tracker`

2. **Visibility**: Public or Private?
   - **Recommendation**: Public (aligns with transparency mission)

3. **Contributors**: Open to contributions?
   - **Decide**: Yes (community-driven) or No (personal project)

4. **Hosting**: Where will you deploy?
   - VPS, AWS, Heroku, Vercel, etc.
   - Update README with deployment URL after deploying

5. **Domain**: Do you want a custom domain?
   - Example: accountability-db.org
   - Can set up after GitHub push

---

**Last Updated**: 2026-01-14
**Status**: Ready for GitHub push after final review
