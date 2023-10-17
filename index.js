const core = require('@actions/core');
const github = require('@actions/github');
const helloWorldModule = require('./module.js');

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

async function alertMessages(owner, repo, pr_number, octokit, changedJsonfiles, changedJSfiles) {
    let combineMessage = [];
    combineMessage.push('# Please be aware!!');
    if (changedJsonfiles.length >= 1) {
        combineMessage.push(`## Changes have been made to **package.json** file :triangular_flag_on_post: \n${changedJsonfiles.join('\n')}`)
    }

    if (changedJSfiles.length >= 1) {
        combineMessage.push(`## Changes have been made to **require()** in .js file(s) :triangular_flag_on_post: \n${changedJSfiles.join('\n')} `)
    }

    await octokit.rest.issues.createComment({
        owner,
        repo,
        issue_number: pr_number,
        body: combineMessage.join('\n')
    });
}

async function setLabels(owner, repo, pr_number, octokit, changedJsonfiles, changedJSfiles) {
    const labels = [];
    if (changedJsonfiles.length >= 1) labels.push(':warning: unsafe [ package.json ]');
    if (changedJSfiles.length >= 1) labels.push(':warning: unsafe [ .js ]');

    if (labels.length) {
        await octokit.rest.issues.addLabels({
            owner,
            repo,
            issue_number: pr_number,
            labels
        });
    }
}

const main = async () => {
    try {

        const owner = core.getInput('owner', { required: true });
        const repo = core.getInput('repo', { required: true });
        const token = core.getInput('token', { required: true });
        const triggerType = core.getInput('type', { required: true });
        const octokit = new github.getOctokit(token);
        let alertType = core.getInput('alert_type', { required: true });
        alertType = alertType.split(',');
        alertType = alertType.map(element => element.trim());

        const pullRequests = await octokit.paginate("GET /repos/:owner/:repo/pulls", {
            owner: owner,
            repo: repo,
            state: "open"
        });

        let prNums = triggerType === 'check_pr'
            ? [core.getInput('pr_number', { required: false })] : pullRequests.map(pr => pr.number);

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
                if (alertType.includes("comment")) {
                    alertMessages(owner, repo, num, octokit, changedJsonfiles, changedJSfiles);
                }
                if (alertType.includes("label")) {
                    setLabels(owner, repo, num, octokit, changedJsonfiles, changedJSfiles);
                }
            }

        }

    } catch (error) {
        core.setFailed(error.message);
    }
}

// Call the main function to run the action
main();
