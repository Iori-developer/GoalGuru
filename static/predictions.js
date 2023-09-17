const filterForm = document.querySelector("#game-week-filter")
const filterFormBtn = document.querySelector("game-week-filter-submit")
const fixturesContainer = document.getElementById('fixtures')
const fixturesFieldSet = document.getElementById('fixtures-fieldset')
const predictionsTitle = document.getElementById('predictions-title')

let titleText = predictionsTitle.textContent

function filterGameWeek() {
    console.log("hi")

    const filter_form_url = filterForm.getAttribute('data-url');
    const filter_form_user = filterForm.getAttribute('data-user');
    let data = new FormData(filterForm, filterFormBtn);
    data.append("user", filter_form_user);

    fetch(filter_form_url, {
        "method": "POST",
        "body": data,
    })
    .then(response => response.json())
    .then(data => {
        message = data.pop()

        console.log(data)

        switch(message['message']) {
            case 'future':
                futureUsername = data.pop()['username']
                predictionsTitle.textContent = `${futureUsername}'s Predictions`
                let futureHtmlContent = ''
                data.forEach(fixture => {
                    homeTeam = fixture['home_team']
                    formattedHomeTeam = `"${homeTeam}"`
                    awayTeam = fixture['away_team']
                    formattedAwayTeam = `"${awayTeam}"`
                    futureHtmlContent += `
                        <div class="grid-future">
                          <p class="grid-item grid-item-1">${homeTeam}</p>
                          <p class="grid-item">Vs</p>
                          <p class="grid-item grid-item-2">${awayTeam}</p>
                        </div>
                    `
                })

                fixturesContainer.innerHTML = futureHtmlContent
                break;
            case 'active':
                activeUsername = data.pop()['username']
                predictionsTitle.textContent = `${activeUsername}'s Predictions`
                let activeHtmlContent = ''
                data.forEach(fixture => {
                    homeTeam = fixture['home_team']
                    formattedHomeTeam = `"${homeTeam}"`
                    awayTeam = fixture['away_team']
                    formattedAwayTeam = `"${awayTeam}"`
                    activeHtmlContent += `
                        <div class="grid-active">
                          <label class="fixture-form-label item grid-item-1" for=${formattedHomeTeam}>${homeTeam}</label>
                          <p class="grid-item">Vs</p>
                          <label class="fixture-form-label item grid-item-2" for=${formattedAwayTeam}>${awayTeam}</label>
                          <input
                            class="fixture-form-input item grid-item-4"
                            type="number"
                            min="0"
                            oninput="restrictInputToInteger(event)"
                            id= ${formattedHomeTeam}
                            name=${formattedHomeTeam}
                          />
                          <input
                            class="fixture-form-input item grid-item-5"
                            type="number"
                            min="0"
                            oninput="restrictInputToInteger(event)"
                            id= ${formattedAwayTeam}
                            name=${formattedAwayTeam}
                          />
                        </div>
                    `
                })

                activeHtmlContent += `
                    <input id="predictions-form-submit" class="grid-item grid-item-last" type="submit" value="Submit" />
                `

                fixturesContainer.innerHTML = activeHtmlContent
                break;
            case 'past-predictions':
                results = data.pop()
                weekly_score = data.pop()['score']
                username = data.pop()['username']
                predictionsTitle.textContent = `${username}'s Predictions - Total Game Week Score: ${weekly_score}`
                let pastPredictionsHtmlContent = ''
                for (let i=0; i < data.length; i++) {
                    homeTeam = data[i]['home_team']
                    formattedHomeTeam = `"${homeTeam}"`
                    awayTeam = data[i]['away_team']
                    formattedAwayTeam = `"${awayTeam}"`
                    pastPredictionsHtmlContent += `
                        <div class="grid">
                          <p class="grid-item grid-item-1">${homeTeam}</p>
                          <p class="grid-item grid-item-2">${awayTeam}</p>
                          <p class="grid-item grid-item-3">Result</p>
                          <p class="grid-item grid-item-4">${results[i]['home_score']}</p>
                          <p class="grid-item grid-item-5">${results[i]['away_score']}</p>
                          <p class="grid-item grid-item-6">Prediction</p>
                          <p class="grid-item grid-item-7">${data[i]['home_score']}</p>
                          <p class="grid-item grid-item-8">${data[i]['away_score']}</p>
                        </div>
                    `
                }


                fixturesContainer.innerHTML = pastPredictionsHtmlContent
                break;
            case 'past-no-predictions':
                results = data.pop()
                console.log(results)
                pastUsername = data.pop()['username']
                predictionsTitle.textContent = `${pastUsername}'s Predictions`
                let pastNoPredictionsHtmlContent = ''
                for (let i = 0; i < data.length; i++) {
                    homeTeam = data[i]['home_team']
                    formattedHomeTeam = `"${homeTeam}"`
                    awayTeam = data[i]['away_team']
                    formattedAwayTeam = `"${awayTeam}"`
                    pastNoPredictionsHtmlContent += `
                        <div class="grid">
                          <p class="grid-item grid-item-1">${homeTeam}</p>
                          <p class="grid-item grid-item-2">${awayTeam}</p>
                          <p class="grid-item grid-item-3">Result</p>
                          <p class="grid-item grid-item-4">${results[i]['home_score']}</p>
                          <p class="grid-item grid-item-5">${results[i]['away_score']}</p>
                          <p class="grid-item grid-item-6">Prediction</p>
                          <p class="grid-item grid-item-7">N/A</p>
                          <p class="grid-item grid-item-8">N/A</p>
                        </div>
                    `
                }



                fixturesContainer.innerHTML = pastNoPredictionsHtmlContent
                break;
            default:
                break;
        }
    })
}

filterForm.addEventListener('submit', function(event) {
    event.preventDefault();

    filterGameWeek();
})

 // JavaScript function to restrict input to integers
function restrictInputToInteger(event) {
    const input = event.target;
    const value = input.value;

    // Remove non-numeric characters using a regular expression
    const integerValue = value.replace(/[^0-9]/g, '');

    // Update the input field with the cleaned integer value
    input.value = integerValue;
}