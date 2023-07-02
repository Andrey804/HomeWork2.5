console.log('Hello world!')

const ws = new WebSocket('ws://localhost:8080')

formChat.addEventListener('submit', (e) => {
    e.preventDefault()
    ws.send(textField.value)
    textField.value = null
})

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
}

ws.onmessage = (e) => {
    let text = e.data

    if (typeof(text) == typeof(new Blob())) {

        let dataDict = 0

        let reader = new FileReader()
        reader.readAsDataURL(text)
        reader.onloadend = function () {
            let b64 = reader.result.replace(/^data:.+;base64,/, '')
            let html = atob(b64);
            dataDict = JSON.parse(html)
            text = dataDict[0] + ': Currency in ' + dataDict[1].length + ' day:'

            write(text, 0)
            moreDiv(dataDict[1], dataDict[0].length * 8)
        }
    }
    else {
        write(text, 0)
    }
}


function moreDiv(listsOfCurrents, margUser) {
    for (let i = 0; i < listsOfCurrents.length; i++) {
        let dictionary = listsOfCurrents[i]

        for (const data in dictionary) {
            if (dictionary.hasOwnProperty(data)) {
                let text = data + ':'
                let marg = margUser + 30
                write(text, marg)

                for (const current in dictionary[data]) {
                    if (dictionary[data].hasOwnProperty(current)) {
                        text = current + ': '
                        marg = margUser + 120

                        for (const key in dictionary[data][current]) {
                            if (dictionary[data][current].hasOwnProperty(key)) {
                                text = text + key + ': ' + dictionary[data][current][key] + ' '
                            }
                        }

                        write(text, marg)
                    }
                } 
            }
        }
    }
}

function write(text, marg) {
    const elMsg = document.createElement('div')

    if (marg > 0) {
        elMsg.style.marginLeft = marg + 'px'
    }

    elMsg.textContent = text
    console.log(elMsg)
    subscribe.appendChild(elMsg)
}