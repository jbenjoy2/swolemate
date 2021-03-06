$(function() {
	let pageCounter = 1;

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
		return `<li class="list-group-item mb-2">
	<a href="/posts/${post.id}" class="post-link">
	<a href="/user/${post.user.id}">
		<img src="${post.user.image_url}" alt="user image" class="timeline-image" width="100px">
	</a>
	
		<div class="post-area w-75">
		<a href="/user/${post
			.user.id}">${post.user.first_name} ${post.user.last_name} - @${post.user.username}</a>
		<span class="text-muted">${post.timestamp}</span>
		<p class='text-center' style='text-decoration:underline'><b>${post.title}</b></p>
		<hr style='background-color:#D9534E'>
		<p class='text-light'>(CLICK FOR FULL DETAILS)</p>
		<p>
			Muscles:
				<small class='text-success'>- ${post.muscles.map((muscle) => muscle.name).join('-')} -</small>
		</p>
		<p class="mt-2">Equipment:
			
		<small class='text-info'>- ${post.equipment
			.map((equipment) => equipment.name)
			.join('-')}  -</small>
		</p>
		</div>
	</li>`;
	}

	function generatePrivateMarkup(post) {
		return `<li class="list-group-item mb-2">
	<a href="/posts/${post.id}" class="post-link">
	<a href="/user/${post.user.id}">
		<img src="${post.user.image_url}" alt="user image" class="timeline-image" width="100px">
	</a>
	
		<div class="post-area w-75">
		<a href="/user/${post
			.user.id}">${post.user.first_name} ${post.user.last_name} - @${post.user.username}</a>
		<span class="text-muted">${post.timestamp}<small class="ml-3 post-lock">Private<i class="fas fa-user-lock ml-1"></i></small></span>
		<p class='text-center' style='text-decoration:underline'><b>${post.title}</b></p>
		<hr style='background-color:#D9534E'>
		<p class='text-light'>(CLICK FOR FULL DETAILS)</p>
		<p>
			Muscles:
				<small class='text-success'>- ${post.muscles.map((muscle) => muscle.name).join('-')} -</small>
		</p>
		<p class="mt-2">Equipment:
			
		<small class='text-info'>- ${post.equipment
			.map((equipment) => equipment.name)
			.join('-')}  -</small>
		</p>
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
		$('#loadMore').fadeOut(0);
		addPosts();
		$('#loadMore').on('click', function() {
			addPosts();
		});

		$('#auth-posts').scroll(function() {
			if ($(this).scrollTop() > 10) {
				$('#loadMore').fadeIn(300);
			} else {
				$('#loadMore').fadeOut(300);
			}
		});

		$('#topBtn').click(function() {
			$('html, body').animate({ scrollTop: 0 }, 400);
			$('#auth-posts').animate({ scrollTop: 0 }, 400);
		});
	});
});
