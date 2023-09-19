# Unsafe PR Detector

This Github action will detect updates in package.json and `require()` in .js files in a pull request.

In order to use this action:
1. Create a folder `.github/workflows`
2. Create a file with .yaml extension
3. Put this code in the file:

```
name: Unsafe PR Detector

on: 
  pull_request:
    types: [opened, reopened, synchronize]

jobs:

  detect-unsafe:
    runs-on: ubuntu-latest
    name: Check pull request with changes
    steps:
      - name: Check PR
        uses: supatsara-wat/Unsafe-PR-Detector@v1.0.0
        with:
          owner: ${{ github.repository_owner }}
          repo: ${{ github.event.repository.name }}
          pr_number: ${{ github.event.number }}
          token: ${{ secrets.GITHUB_TOKEN }}
```

4. Don't forget to allow write permission for the GitHub workflow!!
`Settings tab > Actions > General and scroll down to the “Workflow permissions” section.`

