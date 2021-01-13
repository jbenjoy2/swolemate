const $signup = $('#signup');
const $registerModal = $('#registerModal');
const $loginEmail = $('#email');
const $loginPwd = $('#password');
const $regEmail = $('#new_email');
console.log($registerModal);

setTimeout(function() {
	if (!$loginEmail.val() && !$loginPwd.val()) {
		$regEmail.attr('autofocus', 'autofocus');
		$registerModal.modal('show');
		$('registerModal').on('shown.bs.modal', function() {
			// get the locator for an input in your modal. Here I'm focusing on
			// the element with the id of myInput
			$('#new_email').focus();
		});
	}
}, 3000);
