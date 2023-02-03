const copyText = () => {
  let textArea = document.getElementById("target_text");
  textArea.select();
  try {
    let successful = document.execCommand('copy');
    let msg = successful ? 'successful' : 'unsuccessful';
    console.log('Copying text command was ' + msg);
    textArea.style.backgroundColor = "lightgreen";
    alert("Text copied to clipboard!");
  } catch (err) {
    console.log('Oops, unable to copy');
  }
}

const startSTT = () => {
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.start();
  recognition.onresult = (event) => {
    document.getElementById("source_text").value = event.results[0][0].transcript;
    recognition.stop();
    // send the transcribed text to the server
    fetch('/handle_transcription', {
        method: 'POST',
        body: JSON.stringify({'transcript': event.results[0][0].transcript}),
        headers: {
            'Content-Type': 'application/json'
        }
    });
  }
  recognition.onerror = (event) => {
    console.log(event.error);
  }
}
