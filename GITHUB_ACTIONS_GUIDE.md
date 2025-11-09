# GitHub Actions Setup Guide

This repository is configured to automatically build executables for both Windows and macOS using GitHub Actions.

## How to Use

### First Time Setup

1. **Create a GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/StardewModLoader.git
   git push -u origin main
   ```

2. **Builds happen automatically** when you:
   - Push to main/master branch
   - Create a pull request
   - Manually trigger from GitHub Actions tab

### Download Built Executables

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click on the latest workflow run
4. Scroll down to **Artifacts** section
5. Download:
   - `StardewModLoader-Windows` (contains the .exe)
   - `StardewModLoader-macOS` (contains the .app)

### Manual Build Trigger

1. Go to **Actions** tab on GitHub
2. Click **Build Executables** workflow
3. Click **Run workflow** button
4. Wait ~5 minutes for builds to complete
5. Download artifacts

## Creating Releases

To create a proper release with downloadable files:

1. Tag your commit:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. Go to GitHub → **Releases** → **Create a new release**
3. Select your tag
4. Download the artifacts from the latest Actions run
5. Upload them as release assets
6. Publish the release

## What Gets Built

- **Windows**: `StardewModLoader.exe` (single executable, ~30-40MB)
- **macOS**: `StardewModLoader.app` (application bundle, ~30-40MB)

Both are completely standalone and require no Python installation.

## Notes

- Builds are **completely free** (GitHub Actions free tier)
- Takes ~5 minutes per build
- Both platforms build in parallel
- No Mac hardware needed!
