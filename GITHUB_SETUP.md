# Git Commands to Publish to GitHub

This document contains the exact commands to initialize git, push to GitHub, and create your first release.

## Prerequisites

1. Create a GitHub account if you don't have one: https://github.com/join
2. You already have a repository at: https://github.com/czeyi0725-alt/Gait-Complexity-Analysis
   (If not created yet, go to https://github.com/new and create it)
3. Install Git LFS (optional but recommended for figures):
   ```bash
   # On Linux (if not already installed)
   git lfs install
   ```

## Step-by-Step Publishing

### 1. Initialize Git Repository

```bash
cd /groups/jgoodwin/czeyi/balance

# Initialize git (if not already done)
git init

# Add all files (respecting .gitignore)
git add .

# Make initial commit
git commit -m "Initial commit: gait entropy analysis code and documentation"
```

### 2. Connect to GitHub

```bash
# Add GitHub remote
git remote add origin https://github.com/czeyi0725-alt/Gait-Complexity-Analysis.git

# Verify remote
git remote -v
```

### 3. Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

**Authentication**: GitHub will prompt for credentials. Use a Personal Access Token (PAT) instead of password:
- Generate PAT: https://github.com/settings/tokens
- Scopes needed: `repo`, `workflow`
- Save it securely and use it as password when prompted

### 4. Verify Upload

Visit your repository: `https://github.com/czeyi0725-alt/Gait-Complexity-Analysis`

Check that you see:
- ✅ README.md is displayed
- ✅ LICENSE file
- ✅ All Python scripts in root or organized folders
- ✅ Figures directory
- ✅ docs/ and data/ directories

### 5. Create a Release (Optional but Recommended)

Creating a release gives your code a permanent DOI (via Zenodo):

```bash
# Tag your first release
git tag -a v1.0.0 -m "First release: complete analysis pipeline"
git push origin v1.0.0
```

Then on GitHub:
1. Go to your repository → "Releases" → "Create a new release"
2. Choose tag: `v1.0.0`
3. Release title: "v1.0.0 - Initial Release"
4. Description: Brief summary of what's included
5. Click "Publish release"

### 6. Link to Zenodo for DOI (Optional)

To get a permanent DOI for your code:

1. Go to https://zenodo.org/
2. Log in with your GitHub account
3. Go to Settings → GitHub
4. Find your `balance` repository and toggle it ON
5. Create a new release on GitHub (step 5 above)
6. Zenodo will automatically archive it and assign a DOI
7. Add the DOI badge to your README

## Updating the Repository

After making changes:

```bash
# Check what changed
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "Fix: description of what you fixed"

# Push to GitHub
git push
```

## Common Issues

### Authentication Failed
- Use Personal Access Token instead of password
- Generate new token: https://github.com/settings/tokens

### Large Files Warning
- Files > 50MB should use Git LFS
- Already configured in `.gitattributes`
- Install: `git lfs install`

### Permission Denied
- Check SSH keys: `ssh -T git@github.com`
- Or use HTTPS URL (easier for first-time users)

## What Gets Uploaded

✅ **Included** (via .gitignore):
- All Python scripts (`.py`)
- MATLAB scripts (`.m`)
- Documentation (README, LICENSE, docs/)
- Small figures (PNG via Git LFS)
- Sample data (`data/sample_small.csv`)
- Requirements and configuration files

❌ **Excluded** (via .gitignore):
- Virtual environment (`.venv/`)
- Raw data directories (`gait_old_full/`, `gait_young_full/`)
- Large output files (`*.log`, `*.mat`)
- Temporary files and caches
- Job submission scripts with personal paths

## Next Steps

After publishing:

1. **Update README.md**: Replace `[YOUR-USERNAME]` with your actual GitHub username
2. **Update CITATION.cff**: Add your name, ORCID, and institution
3. **Update LICENSE**: Add your name and year
4. **Test reproduction**: Clone your repo in a fresh location and run `bash run_all.sh`
5. **Add collaborators**: Repository Settings → Collaborators
6. **Enable Discussions**: Repository Settings → Features → Discussions (for Q&A)

## Questions?

- GitHub Guides: https://guides.github.com/
- Git LFS: https://git-lfs.github.com/
- Zenodo-GitHub integration: https://guides.github.com/activities/citable-code/
