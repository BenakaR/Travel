function initial(){
    fetch("/chathistory", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then((response) => response.json())
    .then((data) => display(data));  
}

initial()

function display(dataset){
    let chats = document.getElementById("message-section")
    chats.innerHTML = ""
    dataset.forEach(element => {
        if (element.type == "user") {
            chats.innerHTML += `
            <div class="message user">
              <span id="user-response"> ${element.message} </span>
            </div>
            `;
        } else if (element.type == "assistant") {
            chats.innerHTML += `
            <div class="message bot">
            <span id="bot-response" >
                ${element.message}
            </span>
            </div>
            `;
        }
    });
    chats.scrollTop = chats.scrollHeight;

}

function submit(){
    let chats = document.getElementById("message-section")
    let input = document.getElementById("chatinput")
    let query = input.value
    input.value = ""
    chats.innerHTML += `
          <div class="message user">
            <span id="user-response">
            ${query}
            </span>
          </div>
          <div class="message bot" id="loading">
          <span id="bot-response" >
              Loading...
          </span>
          </div>
        `;
    chats.scrollTop = chats.scrollHeight;
    queries = new FormData()
    console.log(query)
    queries.append("input", query)
    fetch('/chatinput', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: queries
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        loading = document.getElementById("loading")
        chats.removeChild(loading)
        chats.innerHTML += `
          <div class="message bot">
          <span id="bot-response" >
              ${data.assistant}
          </span>
          </div>
        `;
        chats.scrollTop = chats.scrollHeight;
    });
}

