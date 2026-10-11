#!/bin/sh
set -e

# Helper entrypoint for container execution modes
case "$1" in
  demo|serve)
    exec python -m demo_app.app
    ;;
  test|pytest)
    shift
    exec python -m pytest "$@"
    ;;
  check-llm)
    shift
    exec python scripts/check_llm.py "$@"
    ;;
  dev-run)
    shift
    exec python scripts/dev_run.py "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
