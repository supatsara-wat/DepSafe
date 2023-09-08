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
    let numLines = 0;
    const regex = new RegExp("require\\s*\\(.+\\)");
    for (const line of addedLines) {
        const match = line.match(regex);
        if (match) {
            numLines += 1;
        }
    }

    return numLines;
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
        let changedJSfiles = [];
        let countChangedLines = 0;

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
                const numChangedLines = detectJSChange(changedLines.added)
                if (numChangedLines >= 1) {
                    changedJSfiles.push('- ' + file.filename + ': ' + numChangedLines.toString() + ' changes');
                    countChangedLines += numChangedLines;
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
        console.log(changedJSfiles.join('\n'))
        /**
         * Create a comment on the PR with the information we compiled from the
         * list of changed files.
         */
        let jsonComment = '';
        let jsComment = '';
        if (found_packageJson === true) {
            jsonComment = `${diffData.additions} changes have been made to [ package.json ]`
        }

        if (changedJSfiles.length >= 1) {
            let combinedString = changedJSfiles.join('\n');
            jsComment = ` 
            ${countChangedLines} changes have been made to [ require() ]:  \n
            ${combinedString} 
           `
        }

        await octokit.rest.issues.createComment({
            owner,
            repo,
            issue_number: pr_number,
            body: `
            Please be aware!! \n
            ${jsonComment} \n
            ${jsComment}
      `
        });


    } catch (error) {
        core.setFailed(error.message);
    }
}

// Call the main function to run the action
main();