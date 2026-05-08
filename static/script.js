const socket = io();

window.onload = function () {

    const messageInput =
        document.getElementById('message');

    if (Notification.permission !== 'granted') {

        Notification.requestPermission();
    }

    messageInput.addEventListener(

        'input',

        () => {

            socket.emit(

                'typing',

                {
                    username: USERNAME
                }
            );
        }
    );

    messageInput.addEventListener(

        'keypress',

        function(event) {

            if (event.key === 'Enter') {

                sendMessage();
            }
        }
    );
};

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

            data.username,

            {

                body: data.text,

                icon: '/static/icon.png'

            }
        );
    }

    location.reload();
});

socket.on(

    'typing',

    function(data) {

        if (data.username !== USERNAME) {

            document.getElementById(
                'typing'
            ).innerHTML =

                data.username +
                ' is typing...';

            setTimeout(() => {

                document.getElementById(
                    'typing'
                ).innerHTML = '';

            }, 1500);
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

function toggleDarkMode() {

    document.body.classList.toggle(
        'dark-mode'
    );
}