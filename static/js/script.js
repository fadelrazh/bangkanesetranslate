window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const synth = window.speechSynthesis;
const recognition = new SpeechRecognition();
const fromText = document.querySelector(".from-text"),
toText = document.querySelector(".to-text"),
exchageIcon = document.querySelector(".exchange"),
selectTag = document.querySelectorAll("select"),
icons = document.querySelectorAll(".row i");
selectTag.forEach((tag, id) => {
    for (let country_code in countries) {
        let selected = id == 0 ? country_code == "id" ? "selected" : "" : country_code == "en" ? "selected" : "";
        let option = `<option ${selected} value="${country_code}">${countries[country_code]}</option>`;
        tag.insertAdjacentHTML("beforeend", option);
    }
});
exchageIcon.addEventListener("click", () => {
    let tempText = fromText.value,
    tempLang = selectTag[0].value;
    fromText.value = toText.value;
    toText.value = tempText;
    selectTag[0].value = selectTag[1].value;
    selectTag[1].value = tempLang;
});
fromText.addEventListener("keyup", () => {
    if(!fromText.value) {
        toText.value = "";
    }
});
icons.forEach(icon => {
    icon.addEventListener("click", ({target}) => {
        if(!fromText.value || !toText.value) return;
        if(target.classList.contains("fa-microphone")) {
            let paragraph = document.createElement('p');
            let container = document.querySelector('.text-box');
            container.appendChild(paragraph);
            sound.play();
            dictate();
        } else if (target.classList.contains("fa-copy")) {
            if(target.id == "from") {
                navigator.clipboard.writeText(fromText.value);
            } else {
                navigator.clipboard.writeText(toText.value);
            }
        } else {
            let utterance;
            if(target.id == "from") {
                utterance = new SpeechSynthesisUtterance(fromText.value);
                utterance.lang = selectTag[0].value;
            } else {
                utterance = new SpeechSynthesisUtterance(toText.value);
                utterance.lang = selectTag[1].value;
            }
            speechSynthesis.speak(utterance);
        }
    });
});
const dictate = () => {
    recognition.start();
    recognition.onresult = (event) => {
      const speechToText = event.results[0][0].transcript;
      
      paragraph.textContent = speechToText;
  
      if (event.results[0].isFinal) {
  
        if (speechToText.includes('what is the time')) {
            speak(getTime);
        };
        
        if (speechToText.includes('what is today\'s date')) {
            speak(getDate);
        };
        
        if (speechToText.includes('what is the weather in')) {
            getTheWeather(speechToText);
        };
      }
    }
  }
  const speak = (action) => {
    utterThis = new SpeechSynthesisUtterance(action());
    synth.speak(utterThis);
  };
  
  const getTime = () => {
    const time = new Date(Date.now());
    return `the time is ${time.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true })}`
  };
  
  const getDate = () => {
    const time = new Date(Date.now())
    return `today is ${time.toLocaleDateString()}`;
  };
  
  const getTheWeather = (speech) => {
    fetch(`http://api.openweathermap.org/data/2.5/weather?q=${speech.split(' ')[5]}&appid=58b6f7c78582bffab3936dac99c31b25&units=metric`) 
    .then(function(response){
      return response.json();
    })
    .then(function(weather){
      if (weather.cod === '404') {
        utterThis = new SpeechSynthesisUtterance(`I cannot find the weather for ${speech.split(' ')[5]}`);
        synth.speak(utterThis);
        return;
      }
      utterThis = new SpeechSynthesisUtterance(`the weather condition in ${weather.name} is mostly full of ${weather.weather[0].description} at a temperature of ${weather.main.temp} degrees Celcius`);
      synth.speak(utterThis);
    });
  };