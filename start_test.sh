#!/bin/bash
set -e
npx concurrently "cd frontend && npm run dev" "python server.py"