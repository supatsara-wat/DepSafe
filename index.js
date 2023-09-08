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

        let changedJSfiles = [];
        let changedJsonfiles = [];

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
                    changedJSfiles.push(`:black_medium_small_square: ${numChangedLines.toString()} changes in \`${file.filename}\``);
                }
            }

            if (file.filename.includes('package.json')) {
                if (allEmpty === false) {
                    changedJsonfiles.push(`:black_medium_small_square: ${file.additions.toString()} changes in \`${file.filename}\``)
                }
            }
        }
        console.log(count)
        console.log(changedJSfiles.join('\n'))

        let combineMessage = [];
        combineMessage.push('# Please be aware!!')
        if (changedJsonfiles.length >= 1) {
            combineMessage.push(`## Changes have been made to **package.json** file :triangular_flag_on_post: \n:black_medium_small_square: \n${changedJsonfiles.join('\n')}`)
        }

        if (changedJSfiles.length >= 1) {
            combineMessage.push(`## Changes have been made to **require()** in .js file(s) :triangular_flag_on_post:  \n${changedJSfiles.join('\n')} `)
        }


        await octokit.rest.issues.createComment({
            owner,
            repo,
            issue_number: pr_number,
            body: `${combineMessage.join('\n')}`
        });


    } catch (error) {
        core.setFailed(error.message);
    }
}

// Call the main function to run the action
main();