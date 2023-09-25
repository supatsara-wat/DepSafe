# DepSafe

DepSafe can automatically detect `updates in package.json` and `require() in .js files` in a pull request. These updates are identified as unsafe dependency updates in **[Lessons from the Long Tail: Analysing Unsafe Dependency Updates across Software Ecosystems](https://arxiv.org/abs/2309.04197)** paper.

## Paper Abstract 

A risk in adopting third-party dependencies into an application is their potential to serve as a doorway for malicious code to be injected (most often unknowingly). While many initiatives from both industry and research communities focus on the most critical dependencies (i.e., those most depended upon within the ecosystem), little is known about whether the rest of the ecosystem suffers the same fate. Our vision is to promote and establish safer practises throughout the ecosystem. To motivate our vision, in this paper, we present preliminary data based on three representative samples from a population of 88,416 pull requests (PRs) and identify unsafe dependency updates (i.e., any pull request that risks being unsafe during runtime), which clearly shows that unsafe dependency updates are not limited to highly impactful libraries. To draw attention to the long tail, we propose a research agenda comprising six key research questions that further explore how to safeguard against these unsafe activities. This includes developing best practises to address unsafe dependency updates not only in top-tier libraries but throughout the entire ecosystem.

![Frequency of unsafe dependency updates](./images/RQ1_keyword_new.png)
---

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

## References
```
[1] 
```
