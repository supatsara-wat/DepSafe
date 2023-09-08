let combineMessage = [];
        combineMessage.push('Please be aware!!')
        if (found_packageJson === true) {
            combineMessage.push(`${diffData.additions} changes have been made to [ package.json ] file`)
        }

        if (changedJSfiles.length >= 1) {
            joinText = changedJSfiles.join('\n')
            combineMessage.push(` 
            ${countChangedLines} changes have been made to [ require() ] in .js file:  \n${joinText} 
           `)
        }
