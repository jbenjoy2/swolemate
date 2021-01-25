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

function generateMarkup(post) {
	return `<li class="list-group-item my-2 no-hover">
        

    
        <div class="post-area">
        <span class='text-danger'>${post.first} ${post.last} - @${post.username}</span>
        <span class="text-muted">${post.timestamp}</span>
        <p>${post.details}</p>
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
	console.log(posts);
	let markUp;
	for (let post of posts) {
		markUp = generateMarkup(post);
		$('#anon-posts').append(markUp);
	}
}

$(function() {
	addPosts();
	$('#loadMore').on('click', function() {
		addPosts();
	});
});
