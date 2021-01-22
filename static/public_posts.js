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

async function getUserInfo(id) {
	let response = await axios.get(`/api/users/${id}`);
	return response.data;
}

function generateMarkup(post, user) {
	return `<li class="list-group-item my-2">
<a href="/posts/${post.id}" class="post-link">
<a href="/user/${post.user_id}">
	<img src="${user.image_url}" alt="user image" class="timeline-image" width="100px">
</a>

	<div class="post-area">
	<a href="/user/${post.user_id}">${user.first_name} ${user.last_name} - @${user.username}</a>
	<span class="text-muted">${post.timestamp}</span>
	<p>${post.details}</p>
	
	</div>
</li>`;
}

async function addPosts() {
	let posts = await get_posts(pageCounter);
	console.log(posts);
	let markUp;
	let userInfo;
	for (let post of posts) {
		userInfo = await getUserInfo(post.user_id);
	}
	for (let post of posts) {
		let user = userInfo.user;
		console.log(user);
		markUp = generateMarkup(post, user);
		$('#anon-posts').append(markUp);
	}
}

$(function() {
	addPosts();
	$('#loadMore').on('click', function() {
		addPosts();
	});
});
