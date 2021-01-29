$(function() {
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
		return `<li class="list-group-item my-2 no-hover text-center">
        

    
        <div class="post-area w-75">
        <span class='text-danger'>${post
			.user.first_name} ${post.user.last_name} - @${post.user.username}</span>
        <span class="text-muted">${post.timestamp}</span>
        <p class='text-center' style='text-decoration:underline'><b>${post.title}</b></p>
		<hr style='background-color:#D9534E'>
		<p class='text-light'>(LOG IN FOR FULL DETAILS)</p>
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
});
