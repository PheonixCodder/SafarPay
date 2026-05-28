# Unsplit Residual Recovery Plan (079)

## Plan

1. **State Discovery**: List all files that are different between the current `master` and the backup snapshot commit `0340005` (pre-split snapshot).
2. **Sequential Recovery Branch**:
   - Create a new branch `feature/079-unsplit-residual-recovery`.
   - Restore all the differing files from `0340005`.
   - Commit the restored files.
   - Push the branch to remote origin.
   - Open a PR (`gh pr create`).
   - Merge the PR (`gh pr merge`) and delete the branch.
3. **Verify compilation**: Trigger a Flutter code check or build verification if applicable.
