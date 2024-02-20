function sendRequest(userMessage, llmResponse, conversationsSummary) {
    // Show loading indicator
    showLoading();

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/conversation/start', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            // Hide loading indicator
            hideLoading();

            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.type === 'text') {
                    // If response type is text, update textarea with the text response
                    document.getElementById('generatedText').value = response.data;
                } else if (response.type === 'audio') {
                    // If response type is audio, set audio source and play
                    var audio = document.getElementById('response-audio');
                    audio.src = response.data;
                    audio.play();
                }
            } else {
                // Handle error
                console.error('Error:', xhr.status);
            }
        }
    };

    var requestBody = JSON.stringify({
        user_message: userMessage,
        llm_response: llmResponse,
        conversations_summary: conversationsSummary
    });

    xhr.send(requestBody);
}


// Function to show the loading indicator
function showLoading() {
    var loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'block';
}

// Function to hide the loading indicator
function hideLoading() {
    var loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'none';
}

// Add an event listener to the form for submitting
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('prompt-form').addEventListener('submit', function (e) {
        e.preventDefault();
        var userInput = document.getElementById('userInput').value; // Get text from the textarea
        sendRequest(userInput, '', ''); // Pass empty strings for llmResponse and conversationsSummary
    });

    // Add an event listener to the playback button
    document.getElementById('playbackButton').addEventListener('click', function () {
        // Use the SpeechSynthesis API to read the response aloud
        var speech = new SpeechSynthesisUtterance(document.getElementById('generatedText').value);

        // Get the active language button and set speech.lang based on its data-lang attribute
        var activeLanguageButton = document.querySelector('.language-btn.active');
        if (activeLanguageButton) {
            speech.lang = activeLanguageButton.getAttribute('data-lang');
        } else {
            speech.lang = 'es-ES'; // Default to Spanish if no language is selected
        }

        // Add <lang> tags with the xml:lang attribute to switch languages
        speech.text = document.getElementById('generatedText').value;

        window.speechSynthesis.speak(speech);
    });

    // Add an event listener to the audio element for playback
    document.getElementById('response-audio').onloadedmetadata = function () {
        this.play();
    };

    // Add an event listener to the playback button for audio
    document.getElementById('playAudioButton').addEventListener('click', function () {
        var audio = document.getElementById('response-audio');
        audio.play();
    });
});
