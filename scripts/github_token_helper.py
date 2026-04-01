#!/usr/bin/env python
"""
GitHub Token Configuration Helper
Helps users understand and configure GitHub tokens for CI/CD workflows
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n▶ {title}")
    print("  " + "-"*66)


def check_environment():
    """Check current environment for GitHub token"""
    print_header("GITHUB TOKEN ENVIRONMENT CHECK")
    
    checks = {
        'GITHUB_TOKEN': False,
        'GHCR_TOKEN': False,
        'CODECOV_TOKEN': False,
    }
    
    for token_name, _ in checks.items():
        if os.environ.get(token_name):
            checks[token_name] = True
            masked = os.environ.get(token_name)[:10] + "***hidden***"
            print(f"✅ {token_name}: {masked}")
        else:
            print(f"❌ {token_name}: Not set")
    
    return checks


def explain_workflows():
    """Explain how each workflow uses the token"""
    print_header("WORKFLOWS USING GITHUB TOKEN")
    
    workflows = {
        "ci.yml": {
            "purpose": "Continuous Integration (Tests & Code Quality)",
            "uses": [
                "✅ Upload coverage to Codecov",
                "✅ Comment on pull requests",
                "✅ Access GitHub API for status reporting"
            ],
            "token": "GITHUB_TOKEN"
        },
        "model-validation.yml": {
            "purpose": "Model Validation Checks",
            "uses": [
                "✅ Verify models integrity",
                "✅ Test batch predictions",
                "✅ Validate API endpoints"
            ],
            "token": "GITHUB_TOKEN"
        },
        "deployment-ready.yml": {
            "purpose": "Pre-Deployment Verification",
            "uses": [
                "✅ Check deployment readiness",
                "✅ Verify all artifacts",
                "✅ Report status to GitHub"
            ],
            "token": "GITHUB_TOKEN"
        },
        "docker.yml (NEW)": {
            "purpose": "Build & Push Docker Images",
            "uses": [
                "✅ Login to GitHub Container Registry (ghcr.io)",
                "✅ Push Docker images",
                "✅ Generate SBOM",
                "✅ Report image status"
            ],
            "token": "GHCR_TOKEN (or GITHUB_TOKEN)"
        },
        "release.yml": {
            "purpose": "Release Management",
            "uses": [
                "✅ Create version tags",
                "✅ Generate release notes",
                "✅ Publish artifacts"
            ],
            "token": "GITHUB_TOKEN"
        }
    }
    
    for workflow_name, info in workflows.items():
        print_section(f"{workflow_name} - {info['purpose']}")
        print(f"  Token Used: {info['token']}")
        print(f"  Functions:")
        for use in info['uses']:
            print(f"    {use}")


def show_setup_steps():
    """Show step-by-step setup instructions"""
    print_header("SETUP STEPS - QUICK START")
    
    steps = [
        ("1. CREATE GITHUB TOKEN", [
            "Go to: https://github.com/settings/tokens",
            "Click: Tokens (classic) → Generate new token (classic)",
            "Set name: MLOps-CI-CD-Token",
            "Set expiration: 90 days",
            "Select scopes:",
            "  ☑️ repo (full control of repositories)",
            "  ☑️ workflow (GitHub Actions workflows)",
            "  ☑️ write:packages (push Docker images)",
            "  ☑️ read:org (read organization data)",
            "Click: Generate token",
            "Copy: Save token in safe place"
        ]),
        ("2. ADD TO GITHUB SECRETS", [
            "Go to your repository",
            "Click: Settings → Secrets and variables → Actions",
            "Click: New repository secret",
            "Add secret #1:",
            "  Name: GITHUB_TOKEN",
            "  Value: (paste your token)",
            "Click: Add secret",
            "Repeat for GHCR_TOKEN (same value)"
        ]),
        ("3. VERIFY TOKEN WORKS", [
            "Make a code change or commit",
            "Go to: Actions tab",
            "Watch: Workflows run automatically",
            "Check: Coverage uploaded to Codecov",
            "Confirm: Status comments on PRs"
        ]),
        ("4. TEST DOCKER PUSH", [
            "Trigger Docker workflow manually",
            "Or: Commit changes to docker/ directory",
            "Watch: Image build and push to ghcr.io",
            "Verify: Image available at",
            "  ghcr.io/YOUR_ORG/taxi-fare-api:latest"
        ])
    ]
    
    for step_title, step_items in steps:
        print_section(step_title)
        for item in step_items:
            if item.startswith("  "):
                print(f"    {item}")
            else:
                print(f"  {item}")


def show_scopes():
    """Show GitHub token scopes"""
    print_header("GITHUB TOKEN SCOPES EXPLAINED")
    
    scopes = {
        "repo": {
            "description": "Full control of private and public repositories",
            "includes": ["Read/write code", "Push/pull commits", "Manage issues/PRs"]
        },
        "workflow": {
            "description": "Update GitHub Actions workflows",
            "includes": ["Trigger workflows", "Modify workflow files", "View workflow runs"]
        },
        "write:packages": {
            "description": "Push packages/images to registry",
            "includes": ["Docker image push", "npm packages", "Maven packages"]
        },
        "read:org": {
            "description": "Read organization data",
            "includes": ["Read org teams", "Read org members", "Read org metadata"]
        }
    }
    
    for scope, info in scopes.items():
        print_section(f"{scope}")
        print(f"  Description: {info['description']}")
        print(f"  Includes:")
        for item in info['includes']:
            print(f"    • {item}")


def show_security_tips():
    """Show security best practices"""
    print_header("SECURITY BEST PRACTICES")
    
    print_section("✅ DO:")
    do_list = [
        "Store token ONLY in GitHub Secrets",
        "Use minimal required scopes",
        "Set expiration date (90 days recommended)",
        "Rotate token regularly",
        "Use different tokens for different services",
        "Check token in Personal access tokens after use",
        "Revoke immediately if exposed"
    ]
    for item in do_list:
        print(f"  ✅ {item}")
    
    print_section("❌ DON'T:")
    dont_list = [
        "Commit token to repository/files",
        "Share token in Slack/Email/Chat",
        "Use token in local scripts without protection",
        "Set expiration >1 year",
        "Log token in workflow output",
        "Use same token everywhere (prefer specific tokens)"
    ]
    for item in dont_list:
        print(f"  ❌ {item}")
    
    print_section("🔄 Token Rotation Schedule")
    print("  90 days: Rotate personal access tokens")
    print("  Check: GitHub Security log for suspicious activity")
    print("  Review: Which tokens are being used by which workflows")


def show_usage_examples():
    """Show practical usage examples"""
    print_header("PRACTICAL USAGE EXAMPLES")
    
    print_section("Example 1: Push Docker Image")
    print("""
  docker login ghcr.io -u YOUR_USERNAME -p YOUR_TOKEN
  docker tag taxi-fare:latest ghcr.io/YOUR_ORG/taxi-fare:latest
  docker push ghcr.io/YOUR_ORG/taxi-fare:latest
    """)
    
    print_section("Example 2: Clone Private Repository")
    print("""
  git clone https://USERNAME:YOUR_TOKEN@github.com/ORG/REPO.git
    """)
    
    print_section("Example 3: GitHub API Call")
    print("""
  curl -H "Authorization: token YOUR_TOKEN" \\
    https://api.github.com/user/repos
    """)
    
    print_section("Example 4: In GitHub Actions Workflow")
    print("""
  - name: Use GitHub token
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      # Token automatically available in workflows
      # Use it with GitHub CLI or API calls
    """)


def show_troubleshooting():
    """Show troubleshooting guide"""
    print_header("TROUBLESHOOTING GUIDE")
    
    issues = [
        ("Invalid token error", [
            "1. Go to GitHub Settings → Secrets",
            "2. Delete and recreate the secret",
            "3. Verify token has correct scopes",
            "4. Check token hasn't expired"
        ]),
        ("Docker push fails", [
            "1. Verify GHCR_TOKEN is in Secrets",
            "2. Check token has 'write:packages' scope",
            "3. Verify registry is 'ghcr.io'",
            "4. Check image tag format"
        ]),
        ("Codecov upload fails", [
            "1. Check CODECOV_TOKEN is set",
            "2. Or use GITHUB_TOKEN instead",
            "3. Verify coverage.xml exists",
            "4. Link codecov.io to your repo"
        ]),
        ("Token expired", [
            "1. Create new token (same process as before)",
            "2. Update GitHub Secrets with new token",
            "3. Delete old token from Personal access tokens"
        ]),
        ("Workflows not running", [
            "1. Check workflow files are in .github/workflows/",
            "2. Verify YAML syntax is correct",
            "3. Check branch triggers match your branches",
            "4. View Actions tab for error messages"
        ])
    ]
    
    for issue_title, solutions in issues:
        print_section(issue_title)
        for solution in solutions:
            print(f"  {solution}")


def main():
    """Main program"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                  GITHUB TOKEN CONFIGURATION HELPER                  ║
║                   For MLOps CI/CD Pipeline Setup                    ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Show all information
    check_environment()
    explain_workflows()
    show_setup_steps()
    show_scopes()
    show_security_tips()
    show_usage_examples()
    show_troubleshooting()
    
    # Final summary
    print_header("QUICK SUMMARY")
    
    print("""
✅ What you need to do:

1. Create Personal Access Token on GitHub
   → Scopes: repo, workflow, write:packages, read:org
   → Expiration: 90 days

2. Add token to Repository Secrets
   → GITHUB_TOKEN
   → GHCR_TOKEN

3. Your workflows automatically use them:
   → CI Pipeline runs tests
   → Docker workflow pushes images
   → Model validation checks models
   → Deployment checks verify readiness

4. Security:
   → Never commit token to repo
   → Rotate every 90 days
   → Grant minimal permissions needed

5. For more details:
   → See: GITHUB_TOKEN_SETUP_GUIDE.md
    """)
    
    print_header("STATUS: READY FOR CI/CD")
    
    print("""
Your MLOps project is configured for automated:
✅ Testing (Day 10)
✅ Docker push (Day 11)
✅ Kubernetes deployment (Day 12)
✅ Monitoring & alerts (Days 13-14)

Follow this guide to activate your token today!
    """)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
