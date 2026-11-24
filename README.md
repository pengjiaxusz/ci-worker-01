# ci-worker-01

Generic automated build and verification worker running on standard GitHub Actions runners.

## Configuration

Add the following repository Actions Secrets under **Settings → Secrets and variables → Actions**:

- `TARGET_REPO`: Target repository in `owner/repo` format.
- `TARGET_TOKEN`: Personal Access Token with `repo` and `workflow` permissions (for reading the target repository, dispatching runs, and reporting commit statuses).

## Workflows

- **`CI Auto Watcher` (`ci-watch.yml`)**: Polls open Pull Requests and `main` on the target repository every 10 minutes, automatically dispatching `Cloud CI Runner` for any unchecked commit and posting native commit statuses back to the target repository.
- **`Cloud CI Runner` (`ci-run.yml`)**: Executes the full verification matrix (`gate`, `dep-guard`, `non-ui-crates`, `shell-and-backend`, `windows-check`) dynamically derived from the target repository's own `.github/workflows/core.yml`, and writes live `pending` / `success` / `failure` commit statuses back to the target commit.

## Instant Trigger

To trigger immediately without waiting for the watcher schedule:

```bash
GH_TOKEN=<your_token> ./scripts/trigger-ci.sh all
```
