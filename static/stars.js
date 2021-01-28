const $like = $('#like');

function handlerIn() {
	if ($('button#like > i').hasClass('no-like')) {
		$like.empty();
		$like.append('<i class="fas fa-star liked"></i>');
	}
}

function handlerOut() {
	$like.empty();
	$like.append('<i class="far fa-star no-like"></i>');
}

if ($('button#like > i').hasClass('no-like')) {
	$like.hover(handlerIn, handlerOut);
}
