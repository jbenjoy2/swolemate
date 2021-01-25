pageCounter = 1;

async function get_posts(page) {
	let response = await axios.get(`/api/posts?page=${page}`);
	let posts = response.data.posts;
	if (response.data.has_next) {
		pageCounter++;
	} else {
		$('#loadMore').remove();
	}
	return posts;
}

function generatePublicMarkup(post) {
	return `<li class="list-group-item my-2">
<a href="/posts/${post.id}" class="post-link">
<a href="/user/${post.user_id}">
	<img src="${post.image}" alt="user image" class="timeline-image" width="100px">
</a>

	<div class="post-area">
	<a href="/user/${post.user_id}">${post.first} ${post.last} - @${post.username}</a>
	<span class="text-muted">${post.timestamp}</span>
	<p>${post.details}</p>
	
	</div>
</li>`;
}

function generatePrivateMarkup(post) {
	return `<li class="list-group-item my-2">
<a href="/posts/${post.id}" class="post-link">
<a href="/user/${post.user_id}">
	<img src="${post.image}" alt="user image" class="timeline-image" width="100px">
</a>

	<div class="post-area">
	<a href="/user/${post.user_id}">${post.first} ${post.last} - @${post.username}</a>
	<span class="text-muted">${post.timestamp}<small class="ml-3 post-lock">Private<i class="fas fa-user-lock ml-1"></i></small></span>
	<p>${post.details}</p>
	
	</div>
</li>`;
}

async function addPosts() {
	let posts = await get_posts(pageCounter);
	console.log(posts);
	let markUp;
	for (let post of posts) {
		if (post.is_private) {
			markUp = generatePrivateMarkup(post);
		} else markUp = generatePublicMarkup(post);
		$('#all-posts').append(markUp);
	}
}

$(function() {
	addPosts();
	$('#loadMore').on('click', function() {
		addPosts();
	});
});
