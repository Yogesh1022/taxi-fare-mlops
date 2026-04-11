# GitHub Token Setup & Configuration Guide

**Document Version**: 1.0
**Date**: April 1, 2026
**Status**: Complete

---

## 📋 Overview

This guide shows you how to:
1. ✅ Create a GitHub Personal Access Token
2. ✅ Add it to GitHub Secrets
3. ✅ Use it in CI/CD workflows
4. ✅ Verify token functionality

---

## 🔑 Part 1: Create GitHub Personal Access Token

### Step 1: Go to GitHub Settings

1. Open GitHub: https://github.com
2. Click your **profile picture** (top right)
3. Click **Settings**
4. Scroll down to **Developer settings** (left sidebar)
5. Click **Personal access tokens**
6. Click **Tokens (classic)**

### Step 2: Generate New Token

1. Click **Generate new token**
2. Click **Generate new token (classic)**

### Step 3: Configure Token Permissions

**Fill in the form:**

```
Token name: MLOps-CI-CD-Token
Expiration: 90 days (recommended)
```

**Select scopes (check boxes):**

```
☑️ repo              - Full control of private repositories
☑️ workflow          - Update GitHub Actions workflows
☑️ write:packages    - Push Docker images to registry
☑️ read:org          - Read organization data (optional)
☑️ admin:org_hook    - Admin webhooks (optional)
```

### Step 4: Generate & Copy Token

1. Click **Generate token**
2. **Copy the token immediately** (you won't see it again!)
3. Save it somewhere safe temporarily

**Token format**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🔐 Part 2: Add Token to GitHub Secrets

### Step 1: Go to Repository Settings

1. Open your repository on GitHub
2. Click **Settings** (in navigation)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions**

### Step 2: Create Secrets

Create the following secrets:

#### Secret 1: GITHUB_TOKEN (Primary)

```
Name:  GITHUB_TOKEN
Value: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Click **Add secret**

#### Secret 2: GHCR_TOKEN (Docker Registry)

```
Name:  GHCR_TOKEN
Value: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx  (same token)
```

Click **Add secret**

#### Secret 3: CODECOV_TOKEN (Optional - for codecov.io)

```
Name:  CODECOV_TOKEN
Value: (Get from codecov.io dashboard, OR use GITHUB_TOKEN)
```

Click **Add secret**

### Step 3: Verify Secrets Added

You should see in your repository settings:

```
✅ GITHUB_TOKEN      Added a few seconds ago
✅ GHCR_TOKEN        Added a few seconds ago
✅ CODECOV_TOKEN     Added a few seconds ago (optional)
```

---

## 🚀 Part 3: How Token is Used in Workflows

### In CI Pipeline (`ci.yml`)

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  - name: Upload coverage to Codecov
    uses: codecov/codecov-action@v3
    with:
      token: ${{ secrets.GITHUB_TOKEN }}
      
  - name: Create workflow status comment (GitHub API)
    uses: actions/github-script@v7
    with:
      github-token: ${{ secrets.GITHUB_TOKEN }}
```

**What it does:**
- ✅ Authenticates with Codecov
- ✅ Uses GitHub API to comment on PRs
- ✅ Reports workflow status

### In Docker Workflow (`docker.yml`) - NEW

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/taxi-fare-api

  - name: Login to GitHub Container Registry
    uses: docker/login-action@v2
    with:
      registry: ghcr.io
      username: ${{ github.actor }}
      password: ${{ secrets.GITHUB_TOKEN }}
      
  - name: Build and push Docker image
    uses: docker/build-push-action@v4
    with:
      push: true
      tags: ghcr.io/${{ env.IMAGE_NAME }}:latest
```

**What it does:**
- ✅ Authenticates with GitHub Container Registry
- ✅ Pushes Docker images to `ghcr.io`
- ✅ Makes images available for Kubernetes (Day 12)

---

## 📊 Part 4: Workflow Diagram - Token Flow

```
┌─────────────────────────────────────────────────────────┐
│ Your GitHub Repository                                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Push code → Triggers GitHub Actions                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Workflow reads GITHUB_TOKEN from Secrets                │
├─────────────────────────────────────────────────────────┤
│ Available Actions:                                      │
│ ✅ Run tests                                            │
│ ✅ Push to Docker registry                              │
│ ✅ Comment on PRs                                       │
│ ✅ Create releases                                      │
│ ✅ Upload coverage                                      │
└─────────────────────────────────────────────────────────┘
                          │
                ┌─────────┴──────────┬─────────────┐
                │                    │             │
                ▼                    ▼             ▼
        ┌──────────────┐    ┌──────────────┐  ┌──────────────┐
        │ GitHub API   │    │ Docker Reg   │  │ Codecov      │
        │ (Comments)   │    │ (ghcr.io)    │  │ (Coverage)   │
        └──────────────┘    └──────────────┘  └──────────────┘
```

---

## ✅ Part 5: Verify Token Works

### Test 1: Check Token in GitHub

1. Go to GitHub Settings → Personal access tokens
2. Click your `MLOps-CI-CD-Token`
3. You should see:
   - ✅ Scopes listed
   - ✅ Last used: Recently (after first workflow run)
   - ✅ Expiration date

### Test 2: Run CI Pipeline

1. Make a code change or commit to main
2. Go to GitHub → **Actions**
3. Watch the workflow run
4. Check for:
   - ✅ Tests passed
   - ✅ Coverage uploaded to Codecov
   - ✅ Status comments on PRs (if PR)

### Test 3: Manual Workflow Trigger

1. Go to **Actions** tab
2. Click **CI Pipeline**
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**
6. Monitor execution

### Test 4: Docker Push (Day 11)

```bash
# After docker.yml runs:
docker pull ghcr.io/YOUR_ORG/taxi-fare-api:latest

# Should work without manual authentication
```

---

## 🔄 Part 6: Token Rotation & Security

### When to Rotate Token

- ✅ Every 90 days (recommended)
- ✅ If accidentally exposed
- ✅ When team member leaves
- ✅ Before major security updates

### How to Rotate

1. Create new token (repeat Part 1)
2. Update GitHub Secrets with new token (Part 2)
3. Delete old token from Personal access tokens

### Security Best Practices

```
✅ DO:
  - Store token only in GitHub Secrets
  - Use narrow scopes (only what's needed)
  - Set expiration date
  - Rotate regularly
  - Use different tokens for different services

❌ DON'T:
  - Commit token to repository
  - Share token in Slack/Email
  - Use in local scripts
  - Set expiration >1 year
  - Log token in output
```

---

## 📝 Part 7: Troubleshooting

### Issue 1: "Invalid token" error

**Symptom**: Workflow fails with authentication error

**Solution**:
1. Go to GitHub Settings → Secrets
2. Delete and recreate the secret
3. Make sure token has correct scopes
4. Check token hasn't expired

### Issue 2: Docker push fails

**Symptom**: Can't push to ghcr.io

**Solution**:
1. Verify GHCR_TOKEN is added to Secrets
2. Check token has `write:packages` scope
3. Ensure Docker registry is `ghcr.io`
4. Check image tag format

### Issue 3: Codecov upload fails

**Symptom**: Coverage not appearing on codecov.io

**Solution**:
1. Check CODECOV_TOKEN is set
2. Or use GITHUB_TOKEN instead
3. Make sure `coverage.xml` file exists
4. Check codecov.io is linked to repo

### Issue 4: Token expired

**Symptom**: All workflows start failing

**Solution**:
1. Create new token (Part 1)
2. Update GitHub Secrets (Part 2)
3. Delete old token from Personal access tokens

---

## 📚 Part 8: Available Workflows Using Token

### Current Workflows (Days 1-10)

| Workflow | Token Use | Status |
|----------|-----------|--------|
| **ci.yml** | Coverage upload, PR comments | ✅ Active |
| **model-validation.yml** | GitHub API access | ✅ Active |
| **deployment-ready.yml** | Status reporting | ✅ Active |
| **release.yml** | Create releases | ✅ Active |

### Future Workflows (Days 11-14)

| Workflow | Token Use | Status |
|----------|-----------|--------|
| **docker.yml** | Push to ghcr.io | 🔄 Ready |
| **kubernetes.yml** | Deploy to cluster | 📋 Day 12 |
| **monitoring.yml** | Webhook/API calls | 📋 Days 13-14 |

---

## 🎯 Quick Reference

### Common Token Commands

```bash
# Check if token works
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user

# Get token rate limits
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit

# List your personal access tokens
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user/app_authorizations

# Docker login
echo "YOUR_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin

# Git clone with token
git clone https://USERNAME:YOUR_TOKEN@github.com/ORG/REPO.git
```

---

## ✨ Summary Checklist

- [ ] Created GitHub Personal Access Token
- [ ] Selected correct scopes (repo, workflow, write:packages)
- [ ] Copied token to secure location
- [ ] Added GITHUB_TOKEN to Repository Secrets
- [ ] Added GHCR_TOKEN to Repository Secrets
- [ ] Tested CI pipeline with workflow run
- [ ] Verified coverage uploads to Codecov
- [ ] Checked token appears in Personal access tokens
- [ ] Set calendar reminder to rotate token in 90 days
- [ ] Documented token rotation process for team

---

## 📞 Support

If you encounter issues:

1. **Check GitHub Status**: https://www.githubstatus.com/
2. **Review workflow logs**: Actions → Workflow → Run details
3. **Check token scopes**: GitHub Settings → Personal access tokens
4. **Verify secrets**: Repository Settings → Secrets

---

## 🎓 Next Steps

1. ✅ **Now**: Follow this guide to set up token
2. ✅ **Day 11**: Use token for Docker push
3. ✅ **Day 12**: Use token for Kubernetes secrets
4. ✅ **Days 13-14**: Use token for monitoring/webhooks
5. ✅ **Ongoing**: Rotate token every 90 days

---

**Document Status**: ✅ Complete
**Last Updated**: April 1, 2026
**Next Review**: June 30, 2026 (Token Rotation)
