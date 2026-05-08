const socket = io();

if (Notification.permission !== 'granted') {

    Notification.requestPermission();
}

function sendMessage() {

    let messageInput =
        document.getElementById('message');

    let imageInput =
        document.getElementById('imageInput');

    let message =
        messageInput.value;

    let file =
        imageInput.files[0];

    if (file) {

        let formData = new FormData();

        formData.append(
            'image',
            file
        );

        formData.append(
            'text',
            message
        );

        fetch('/upload', {

            method: 'POST',

            body: formData

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                location.reload();
            }
        });

        return;
    }

    if (message.trim() !== '') {

        socket.send({

            username: USERNAME,

            text: message

        });

        messageInput.value = '';
    }
}

socket.on('message', function(data) {

    if (
        data.username !== USERNAME &&
        Notification.permission === 'granted'
    ) {

        new Notification(
            'New Message from ' + data.username,
            {
                body: data.text
            }
        );
    }

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