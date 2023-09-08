file file
const github = require('@actions/github')
const github = require('@actions/github')
const github = require('@actions/github')

await octokit.rest.issues.createComment({
                owner,
                repo,
                issue_number: pr_number,
                body: `
            Pull Request #${pr_number} has been updated with the modification of [ package.json ]: \n
            - ${diffData.changes} changes \n
            - ${diffData.additions} additions \n
            - ${diffData.deletions} deletions \n
          `
            });
