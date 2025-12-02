# Instructions to Push to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `memory_hierarchy_edu`
3. Description: "Educational repository on memory hierarchy: Caches, TLBs, Page Walks, VIPT, and Synonym Problems"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Push to GitHub

After creating the repository, run these commands (replace YOUR_USERNAME with your GitHub username):

```bash
cd memory_hierarchy_edu

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/memory_hierarchy_edu.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Alternative: Using SSH

If you have SSH keys set up:

```bash
git remote add origin git@github.com:YOUR_USERNAME/memory_hierarchy_edu.git
git branch -M main
git push -u origin main
```

## Troubleshooting

If you get authentication errors:
- Use GitHub CLI: `gh auth login`
- Or use a Personal Access Token instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

