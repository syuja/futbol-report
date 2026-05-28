#!/bin/bash
set -e

echo "Cleaning previous build..."
rm -rf build lambda.zip

echo "Creating build folder..."
mkdir build

echo "Copying application code..."
cp main.py build/
cp -r prompts build/

echo "Installing dependencies (Linux-targeted for Lambda)..."
python3 -m pip install \
  --target build \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  --upgrade \
  openai requests redis

echo "Zipping..."
cd build
zip -r ../lambda.zip . -x '*.pyc' -x '*__pycache__*'
cd ..

echo "Done. Created lambda.zip ($(du -h lambda.zip | cut -f1))"