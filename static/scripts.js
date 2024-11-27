document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('chat-form');
    const messageInput = document.getElementById('message');
    const chatbox = document.getElementById('chatbox');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const userMessage = messageInput.value;
        addMessage(userMessage, 'user');

        // Send the message to the server and get a response
        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'message': userMessage
            })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.response, 'bot');
        });

        messageInput.value = '';
        chatbox.scrollTop = chatbox.scrollHeight;
    });

    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        messageElement.textContent = message;
        chatbox.appendChild(messageElement);
    }
});
