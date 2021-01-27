pageCounter = 1;

async function get_posts(page) {
	let response = await axios.get(`/api/posts?page=${page}`);
	let posts = response.data.posts;
	if (response.data.has_next) {
		$('#loadMore').show();
		pageCounter++;
	} else {
		$('#loadMore').hide();
	}
	return posts;
}

function generatePublicMarkup(post) {
	return `<li class="list-group-item mb-2">
<a href="/posts/${post.id}" class="post-link">
<a href="/user/${post.user_id}">
	<img src="${post.image}" alt="user image" class="timeline-image" width="100px">
</a>

	<div class="post-area w-75">
	<a href="/user/${post.user_id}">${post.first} ${post.last} - @${post.username}</a>
	<span class="text-muted">${post.timestamp}</span>
	<p class='text-center' style='text-decoration:underline'><b>${post.title}</b></p>
	<hr style='background-color:#D9534E'>
	<p class='text-light'>(CLICK FOR FULL DETAILS)</p>
	<p>
		Muscles:
			<small>- ${post.muscles.join('- -')} -</small>
	</p>
	<p class="mt-2">Equipment:
		
	<small>- ${post.equipment.join('- -')} -</small>
	</p>
	</div>
</li>`;
}

function generatePrivateMarkup(post) {
	return `<li class="list-group-item mb-2">
<a href="/posts/${post.id}" class="post-link">
<a href="/user/${post.user_id}">
	<img src="${post.image}" alt="user image" class="timeline-image" width="100px">
</a>

	<div class="post-area w-75">
	<a href="/user/${post.user_id}">${post.first} ${post.last} - @${post.username}</a>
	<span class="text-muted">${post.timestamp}<small class="ml-3 post-lock">Private<i class="fas fa-user-lock ml-1"></i></small></span>
	<p class='text-center' style='text-decoration:underline'><b>${post.title}</b></p>
	<hr style='background-color:#D9534E'>
	<p class='text-light'>(CLICK FOR FULL DETAILS)</p>
	<p>
		Muscles:
			<small>- ${post.muscles.join('- -')} -</small>
	</p>
	<p class="mt-2">Equipment:
		
	<small>- ${post.equipment.join('- -')} -</small>
	</p>
	</div>
</li>`;
}

async function addPosts() {
	let posts = await get_posts(pageCounter);
	let markUp;
	if (posts.length > 0) {
		for (let post of posts) {
			if (post.is_private) {
				markUp = generatePrivateMarkup(post);
			} else markUp = generatePublicMarkup(post);

			$('#posts').append(markUp);
		}
	} else {
		$('#posts').append(`<h1 class='text-center'>No Posts To Show</h1>`);
	}
}

$(function() {
	if ($(window).width() <= 374) {
		$('#topBtn').remove();
	} else {
		$('#topBtn').fadeOut(0);
	}

	addPosts();
	$('#loadMore').on('click', function() {
		addPosts();
	});

	$(window).scroll(function() {
		if ($(this).scrollTop() > $(window).height() - 80) {
			$('#topBtn').fadeIn(300);
		} else {
			$('#topBtn').fadeOut(300);
		}
	});

	$('#topBtn').click(function() {
		$('html, body').animate({ scrollTop: $(window).height() }, 400);
	});
});
