# GitHub Actions request bridge

This bridge provides an auditable dispatch path when the GitHub connector can read and write repository files but cannot call the Actions workflow-dispatch endpoint directly.

## Operation

1. After this bridge and the target canary workflow are both present on the default branch, commit exactly one JSON request file under execution_requests/ on main.
2. The bridge accepts only the allowlisted canary workflow, ref main, a valid YYYY-MM month, and a boolean include_funding value.
3. It uses the run-scoped GITHUB_TOKEN with actions: write to call GitHub's workflow dispatch REST endpoint. No personal access token is needed.
4. The bridge records validation, HTTP status, UTC timestamps, run ID, and final status in a GitHub Actions artifact and Step Summary.
5. A successful dispatch means only that the target run was queued. The target workflow's logs and SHA-256 read-back checks determine whether persistence succeeded.

## Request shape

A request file should contain these fields:
- workflow: .github/workflows/btcusdt-supabase-upload-canary.yml
- ref: main
- inputs.month: YYYY-MM, for example 2026-09
- inputs.include_funding: true or false

Use a unique filename per request. Never put secrets, tokens, service-role keys, or command strings in request files. The bridge does not accept arbitrary workflow names or shell commands.

## Activation requirements

- This bridge must be merged to main.
- The canary workflow must also exist on main before it can be dispatched.
- GitHub Actions secrets SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY, the private storage bucket, and the catalog schema must be configured.
- Installing this bridge does not create a request file or trigger a data upload.
