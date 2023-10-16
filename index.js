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

function alertMessages(changedJsonfiles, changedJSfiles) {
    let combineMessage = [];
    combineMessage.push('# Please be aware!!');
    if (changedJsonfiles.length >= 1) {
        combineMessage.push(`## Changes have been made to **package.json** file :triangular_flag_on_post: \n${changedJsonfiles.join('\n')}`)
    }

    if (changedJSfiles.length >= 1) {
        combineMessage.push(`## Changes have been made to **require()** in .js file(s) :triangular_flag_on_post: \n${changedJSfiles.join('\n')} `)
    }

    return combineMessage;
}

async function checkLabelExists(owner, repo, labelName, octokit) {
    try {
        // Fetching all labels in the repository
        const labels = await octokit.paginate(octokit.rest.issues.listLabelsForRepo, {
            owner,
            repo
        });

        // Checking if the label exists in the fetched labels
        const labelExists = labels.some(label => label.name === labelName);
        console.log(labels)
        console.log(labelExists)

        if (labelExists) {
            await octokit.rest.issues.updateLabel({
                owner,
                repo,
                name: labelName,
                color: '#CD5C5C'
            });
            console.log('create new label');
        }
        else {
            await octokit.rest.issues.createLabel({
                owner,
                repo,
                name: labelName,
                color: '#CD5C5C'
            });
            console.log('update label');
        }
    }
    catch (error) {
        core.setFailed(error.message);
    }
}

const main = async () => {
    try {

        /**
         * Now we need to create an instance of Octokit which will use to call
         * GitHub's REST API endpoints.
         * We will pass the token as an argument to the constructor. This token
         * will be used to authenticate our requests.
         * You can find all the information about how to use Octokit here:
         * https://octokit.github.io/rest.js/v18
         **/

        /**
         * We need to fetch the list of files that were changes in the Pull Request
         * and store them in a variable.
         * We use octokit.paginate() to automatically loop over all the pages of the
         * results.
         * Reference: https://octokit.github.io/rest.js/v18#pulls-list-files
         */

        const owner = core.getInput('owner', { required: true });
        const repo = core.getInput('repo', { required: true });
        const pr_number = core.getInput('pr_number', { required: true });
        const token = core.getInput('token', { required: true });
        const triggerType = core.getInput('type', { required: true });

        const octokit = new github.getOctokit(token);


        const pullRequests = await octokit.paginate("GET /repos/:owner/:repo/pulls", {
            owner: owner,
            repo: repo,
            state: "open"
        });

        let prNums = triggerType === 'PR'
            ? pullRequests.map(pr => pr.number) : [pr_number];

        for (const num of prNums) {
            const changedFiles = await octokit.paginate("GET /repos/:owner/:repo/pulls/:pull_number/files", {
                owner: owner,
                repo: repo,
                pull_number: num
            });

            let changedJSfiles = [];
            let changedJsonfiles = [];

            for (const file of changedFiles) {

                const changedLines = parsePatch(file.patch)

                if (changedLines.added.every(item => item.trim() === "")) {
                    continue;
                }

                const fileExtension = getFileExtension(file.filename)
                if (fileExtension === 'js') {
                    const numChangedLines = detectJSChange(changedLines.added)
                    if (numChangedLines >= 1) {
                        changedJSfiles.push(`:black_medium_small_square: ${numChangedLines.toString()} changes in \`${file.filename}\``);
                    }
                }

                if (file.filename.includes('package.json')) {
                    changedJsonfiles.push(`:black_medium_small_square: ${file.additions.toString()} changes in \`${file.filename}\``)
                }
            }

            if (changedJsonfiles.length >= 1 || changedJSfiles.length >= 1) {
                if (triggerType === 'PR') {
                    const combineMessage = alertMessages(changedJsonfiles, changedJSfiles);
                    await octokit.rest.issues.createComment({
                        owner,
                        repo,
                        issue_number: pr_number,
                        body: combineMessage.join('\n')
                    });

                    const label = ':warning: unsafe'
                    checkLabelExists(owner, repo, label, octokit);
                    await octokit.rest.issues.addLabels({
                        owner,
                        repo,
                        issue_number: pr_number,
                        labels: [label],
                    });
                }
            }

        }


    } catch (error) {
        core.setFailed(error.message);
    }
}

// Call the main function to run the action
main();
