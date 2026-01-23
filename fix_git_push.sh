#!/bin/bash

# Fix git push issue - check current branch and push
echo "Checking current branch..."
git branch -a

echo "Checking git status..."
git status

echo "Fetching from origin..."
git fetch origin

echo "Checking remote branches..."
git branch -r

# Check if we're on master or main
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Push to the correct branch
if [ "$CURRENT_BRANCH" = "master" ]; then
    echo "Pushing to master branch..."
    git push origin master
elif [ "$CURRENT_BRANCH" = "main" ]; then
    echo "Pushing to main branch..."
    git push origin main
else
    echo "Creating and pushing main branch..."
    git checkout -b main
    git push -u origin main
fi