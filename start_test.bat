@echo off
npx concurrently "cd frontend && npm run dev" "python server.py"