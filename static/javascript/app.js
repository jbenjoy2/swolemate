const $signup = $('#signup');
const $registerModal = $('#registerModal');
const $loginModal = $('#loginModal');
const $loginEmail = $('#email');
const $loginPwd = $('#password');
const $regEmail = $('#new_email');
const $loginErrors = $('#login-errors');
const $registerErrors = $('#register-errors');

if ($loginErrors.text()) {
	$loginModal.modal('show');
}

if ($registerErrors.text()) {
	$registerModal.modal('show');
}
