const core = require('@actions/core');
const github = require('@actions/github');

function parsePatch(patch) {
    const added = [];
    const removed = [];

    const lines = patch.split('\n');
    for (const line of lines) {
        if (line.startsWith('+')) {
            added.push(line.substring(1));
        } else if (line.startsWith('-')) {
            removed.push(line.substring(1));
        }
    }

    return {
        added,
        removed
    };
}

function getFileExtension(filename) {
    const parts = filename.split('.');
    // Return null if there's no extension or if it's a hidden file (e.g., .gitignore)
    if (parts.length <= 1 || (parts.length === 2 && parts[0] === '')) {
        return null;
    }
    return parts.pop();
}

function detectJSChange(addedLines) {
    const regex = new RegExp("require\\s*\\(.+\\)");
    addedLines.forEach(line => {
        const match = line.match(regex);
        if (match) {
            console.log('Match found:', match[0]);
            return true;
        }

    });

    return false;
}


const main = async () => {
    try {
        /**
         * We need to fetch all the inputs that were provided to our action
         * and store them in variables for us to use.
         **/
        const owner = core.getInput('owner', { required: true });
        const repo = core.getInput('repo', { required: true });
        const pr_number = core.getInput('pr_number', { required: true });
        const token = core.getInput('token', { required: true });

        /**
         * Now we need to create an instance of Octokit which will use to call
         * GitHub's REST API endpoints.
         * We will pass the token as an argument to the constructor. This token
         * will be used to authenticate our requests.
         * You can find all the information about how to use Octokit here:
         * https://octokit.github.io/rest.js/v18
         **/
        const octokit = new github.getOctokit(token);

        /**
         * We need to fetch the list of files that were changes in the Pull Request
         * and store them in a variable.
         * We use octokit.paginate() to automatically loop over all the pages of the
         * results.
         * Reference: https://octokit.github.io/rest.js/v18#pulls-list-files
         */

        const changedFiles = await octokit.paginate("GET /repos/:owner/:repo/pulls/:pull_number/files", {
            owner: owner,
            repo: repo,
            pull_number: pr_number
        });

        /**
         * Contains the sum of all the additions, deletions, and changes
         * in all the files in the Pull Request.
         **/
        let diffData = {
            additions: 0,
            deletions: 0,
            changes: 0
        };
        let found_packageJson = false;

        /**
         * Loop over all the files changed in the PR and add labels according 
         * to files types.
         **/
        let count = 0;
        for (const file of changedFiles) {

            count += 1;
            const changedLines = parsePatch(file.patch)

            console.log(`${file.filename} ${getFileExtension(file.filename)}`)

            const allEmpty = changedLines.added.every(item => item.trim() === "");
            console.log(changedLines.added);

            const fileExtension = getFileExtension(file.filename)
            if (fileExtension === 'js') {
                if (detectJSChange(changedLines.added) === true) {
                    console.log('found');
                }
            }

            if (file.filename === "package.json") {
                if (allEmpty === false) {
                    found_packageJson = true;
                    diffData.additions += file.additions;
                    diffData.deletions += file.deletions;
                    diffData.changes += file.changes;
                }
            }
        }
        console.log(count)
        /**
         * Create a comment on the PR with the information we compiled from the
         * list of changed files.
         */
        if (found_packageJson === true) {
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
        }

    } catch (error) {
        core.setFailed(error.message);
    }
}

// Call the main function to run the action
main();