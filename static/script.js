const socket = io();

if (Notification.permission !== 'granted') {

    Notification.requestPermission();
}

function sendMessage() {

    let messageInput =
        document.getElementById('message');

    let message =
        messageInput.value;

    if (message.trim() !== '') {

        socket.send({

            username: USERNAME,

            text: message

        });

        messageInput.value = '';
    }
}

socket.on('message', function(data) {

    location.reload();
});

document.getElementById('message').addEventListener(

    'keypress',

    function(event) {

        if (event.key === 'Enter') {

            sendMessage();
        }
    }
);

function deleteMessage(messageId) {

    fetch('/delete_message/' + messageId, {

        method: 'POST'

    })

    .then(response => response.json())

    .then(data => {

        if (data.success) {

            location.reload();
        }
    });
}