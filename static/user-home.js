const createLeagueForm = document.querySelector('#create-league-form');
const createLeagueBtn = document.querySelector('#create-league-form-button');

const joinLeagueForm = document.querySelector('#join-league-form');
const joinLeagueBtn = document.querySelector('#join-league-form-button');

function createLeague() {
    console.log("HI")
    try {
        if (createLeagueForm.nextElementSibling.nodeName === "P") {
            createLeagueForm.nextElementSibling.remove()
        }
    }
    catch(err) {
        console.log(err)
    }

    const create_league_url = createLeagueForm.getAttribute('data-url');
    let data = new FormData(createLeagueForm, createLeagueBtn);

    fetch(create_league_url, {
        "method": "POST",
        "body": data,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const displayMessage = document.createElement('p');
        displayMessage.textContent = data['message'];
        createLeagueForm.insertAdjacentElement('afterend', displayMessage);
        createLeagueForm.reset()
    })
}

function joinLeague() {
    if (joinLeagueForm.nextElementSibling.nodeName === "P") {
        console.log("HI")
        p_element = joinLeagueForm.nextElementSibling
        console.log(p_element.textContent)
        p_element.remove()
    }

    const join_league_url = joinLeagueForm.getAttribute('data-url');
    let data = new FormData(joinLeagueForm, joinLeagueBtn);

    fetch(join_league_url, {
        "method": "POST",
        "body": data,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);

        if (data['message'] == "Successfully joined league") {
            location.reload();
        } else {
            const displayMessage = document.createElement('p');
            displayMessage.textContent = data['message'];
            joinLeagueForm.insertAdjacentElement('afterend', displayMessage);
        }
        joinLeagueForm.reset()
    })
}

createLeagueForm.addEventListener('submit', function(event) {
    event.preventDefault();

    createLeague();
})

joinLeagueForm.addEventListener('submit', function(event) {
    event.preventDefault();

    console.log("HI")

    joinLeague()
})


