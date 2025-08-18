$(document).ready(function () {
    $('.alert').delay(5000).fadeOut(400);

    $('.confirm-delete').on('click', function (e) {
        if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
            e.preventDefault();
        }
    });

    $('main').hide().fadeIn(300);

    $('form input[type="text"], form input[type="email"], form input[type="password"]').first().focus();

    $('#contact-form').on('submit', function () {
        const name = $('#name').val().trim();
        const email = $('#email').val().trim();
        const message = $('#message').val().trim();

        if (!name || !email || !message) {
            alert('Пожалуйста, заполните все поля.');
            return false;
        }

        if (!email.includes('@')) {
            alert('Введите корректный email.');
            return false;
        }

        return true;
    });
});