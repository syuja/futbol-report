#!/bin/bash
# Builds a Lambda deployment zip for the futbol-report generator.
# Run from the futbol-report project root: ./build_lambda.sh

set -e  # stop on any error

echo "Cleaning previous build..."
rm -rf build lambda.zip

echo "Creating build folder..."
mkdir build

echo "Copying application code..."
cp main.py build/
cp -r prompts build/

echo "Installing dependencies (Linux-targeted for Lambda)..."
uv pip install \
  --target build \
  --python-platform x86_64-manylinux2014 \
  --python-version 3.12 \
  --only-binary :all: \
  "pydantic-core==2.46.4" \
  openai requests redis

echo "Zipping..."
cd build
zip -r ../lambda.zip . -x '*.pyc' -x '*__pycache__*'
cd ..

echo "Done. Created lambda.zip ($(du -h lambda.zip | cut -f1))"
