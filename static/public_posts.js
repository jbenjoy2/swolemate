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
                <small class='text-success'>- ${post.muscles.join('- -')} -</small>
        </p>
        <p class="mt-2">Equipment:
            
        <small class='text-info'>- ${post.equipment.join('- -')} -</small>
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
	$('#topBtn').fadeOut(0);
	addPosts();
	$('#loadMore').on('click', function() {
		addPosts();
	});

	$(window).scroll(function() {
		if ($(this).scrollTop() > 300) {
			$('#topBtn').fadeIn(300);
		} else {
			$('#topBtn').fadeOut(300);
		}
	});

	$('#topBtn').click(function() {
		$('html, body').animate({ scrollTop: 0 }, 400);
	});
});
