#!/bin/bash
# Run this script once to initialize Git and push to GitHub

git init
git add .
git commit -m "Initial commit: BlogVerse - Online Blogging & Article Sharing System"

echo ""
echo "Now create a repo on GitHub named 'blogverse' and run:"
echo "  git remote add origin https://github.com/YOUR_USERNAME/blogverse.git"
echo "  git branch -M main"
echo "  git push -u origin main"
