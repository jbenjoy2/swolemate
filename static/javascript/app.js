const $signup = $('#signup');
const $registerModal = $('#registerModal');
const $loginModal = $('#loginModal');
const $loginEmail = $('#email');
const $loginPwd = $('#password');
const $regEmail = $('#new_email');
const $loginErrors = $('#login-errors');

if ($loginErrors.text()) {
	$loginModal.modal('show');
}
