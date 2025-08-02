// script.js

// ==================== cart ====================
if (document.getElementById('cartItemsContainer')) {
    const cartData = [
      { name: "통깨", count: 3 },
      { name: "소금", count: 1 },
      { name: "깻잎", count: 2 },
      { name: "설탕", count: 2 },
      { name: "후추", count: 1 }
    ];
  
    function createCartItem(item) {
      const wrapper = document.createElement('div');
      wrapper.className = 'cart-item-wrapper';
  
      wrapper.innerHTML = `
        <div class="cart-item">
          <span class="cart-item-name">${item.name}</span>
          <div class="cart-btn-group">
            <button class="cart-btn plus">+</button>
            <button class="cart-btn minus">-</button>
            <span class="cart-count">${item.count}</span>
          </div>
        </div>
        <img class="cart-trash" src="../images/cart/trash.png" alt="삭제">
      `;
  
      const plusBtn = wrapper.querySelector('.plus');
      const minusBtn = wrapper.querySelector('.minus');
      const countSpan = wrapper.querySelector('.cart-count');
  
      plusBtn.addEventListener('click', () => {
        let count = parseInt(countSpan.textContent);
        countSpan.textContent = count + 1;
      });
  
      minusBtn.addEventListener('click', () => {
        let count = parseInt(countSpan.textContent);
        if (count > 1) countSpan.textContent = count - 1;
      });
  
      const trashBtn = wrapper.querySelector('.cart-trash');
      trashBtn.addEventListener('click', () => {
        wrapper.remove();
      });
  
      return wrapper;
    }
  
    const container = document.getElementById('cartItemsContainer');
    cartData.forEach(item => {
      const element = createCartItem(item);
      container.appendChild(element);
    });
  
    const goBtn = document.querySelector('.cart-go-button');
    if (goBtn) {
      goBtn.addEventListener('click', () => {
        const cart = [];
        document.querySelectorAll('.cart-item-wrapper').forEach(wrapper => {
          const name = wrapper.querySelector('.cart-item-name').textContent;
          const count = parseInt(wrapper.querySelector('.cart-count').textContent);
          cart.push({ name, count });
        });
        window.location.href = "https://www.coupang.com/";
      });
    }
  }
  
  
  // ==================== login ====================
  if (document.getElementById('username') && document.getElementById('password')) {
    function handleLogin() {
      const username = document.getElementById('username')?.value.trim();
      const password = document.getElementById('password')?.value.trim();
  
      if (!username || !password) {
        alert("아이디와 비밀번호를 모두 입력해주세요!");
        return;
      }
  
      console.log("입력된 아이디:", username);
      console.log("입력된 비밀번호:", password);
  
      alert(`${username}님 환영합니다! 🎉`);
    }
  }
  
  
  // ==================== signup ====================
  if (document.querySelectorAll('.signup-check-btn').length > 0) {
    document.querySelectorAll('.signup-check-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const input = btn.previousElementSibling;
        const field = input.name === 'userid' ? '아이디' : '이메일';
        const value = input.value.trim();
  
        if (!value) {
          alert(`${field}를 입력해주세요.`);
        } else {
          alert(`${field} \"${value}\"는 사용 가능합니다! (임시)`);
        }
      });
    });
  }
  
  if (document.querySelector('form')) {
    document.querySelector('form').addEventListener('submit', (e) => {
      e.preventDefault();
  
      const userid = document.querySelector('input[name="userid"]').value.trim();
      const password = document.querySelector('input[name="password"]').value.trim();
      const password_confirm = document.querySelector('input[name="password_confirm"]').value.trim();
      const username = document.querySelector('input[name="username"]').value.trim();
      const email = document.querySelector('input[name="email"]').value.trim();
  
      if (!userid || !password || !password_confirm || !username || !email) {
        alert('모든 필수 항목을 입력해주세요!');
        return;
      }
  
      if (password !== password_confirm) {
        alert('비밀번호가 일치하지 않습니다!');
        return;
      }
  
      alert(`${username}님, 회원가입을 환영합니다! 🎉`);
    });
  }
  
  
  // ==================== menu1 ====================
  document.addEventListener('DOMContentLoaded', () => {
    const changeBtn = document.querySelector('.menu-password-change-box');
    if (changeBtn) {
      changeBtn.addEventListener('click', () => {
        const confirmed = confirm("비밀번호를 변경하시겠습니까?");
        if (confirmed) {
          alert("비밀번호 변경 페이지로 이동합니다! (임시)");
          window.location.href = 'change-password.html';
        }
      });
    }
  });
  
  
  // ==================== menu2 ====================

// 재료 추가 함수
function addIngredient(inputEl, containerEl) {
    const value = inputEl.value.trim();
    if (!value) return;
  
    const exists = Array.from(containerEl.children).some(child => child.textContent === value);
    if (exists) {
      alert(`이미 "${value}"은(는) 입력되어 있어요!`);
      inputEl.value = '';
      return;
    }
  
    const tag = document.createElement('div');
    tag.className = 'menu2-tag-button';
    tag.textContent = value;
    containerEl.appendChild(tag);
  
    inputEl.value = '';
  }
  
  // 엔터 입력 이벤트 등록
  document.addEventListener('DOMContentLoaded', () => {
    const preferInput = document.getElementById('prefer-input');
    const nonpreferInput = document.getElementById('nonprefer-input');
    const preferTags = document.getElementById('prefer-tags');
    const nonpreferTags = document.getElementById('nonprefer-tags');
  
    preferInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addIngredient(preferInput, preferTags);
      }
    });
  
    nonpreferInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addIngredient(nonpreferInput, nonpreferTags);
      }
    });
  });




// recipe


const recipeData = {
    "mukchi": {
      title: "묵은지 참치말이 레시피 (2인분)",
      ingredients: [
        "잡곡밥 1.5공기 (300g)",
        "참치 통조림 (소) 2개",
        "묵은지 6~8장",
        "마요네즈 2큰술",
        "후추 약간",
        "깻잎 10장 내외",
        "들기름 약간",
        "통깨 약간",
        "소금 약간"
      ],
      steps: [
        "묵은지는 물에 깨끗하게 씻은 후 체에 받쳐 물기를 제거해 주세요.",
        "참치 통조림은 기름을 쫙 따라낸 후, 마요네즈와 후추를 약간 넣고 골고루 섞어줍니다.",
        "따뜻한 잡곡밥에 소금과 들기름을 약간 넣고 골고루 비벼줍니다.",
        "김밥 위에 묵은지를 겹쳐서 넓게 펼칩니다.",
        "묵은지 위에 밥을 고르게 펴고, 깻잎을 올린 후 마요네즈에 버무린 참치를 올려 돌돌 말아주세요.",
        "묵은지 말이 겉면에 들기름을 살짝 바른 후 먹기 좋은 크기로 썰어줍니다.",
        "접시에 예쁘게 담고 통깨를 솔솔 뿌려주면 완성!"
      ],
      youtubeQuery: "묵은지 참치말이"
    },
  
    // 필요 시 더 추가 가능
  };
  
  async function fetchYoutubeVideos(query) {
    const apiKey = "API_KEY"; // 유튜브 API 키로 교체!
    const maxResults = 4;
  
    const apiUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=${maxResults}&key=${apiKey}`;
  
    try {
      const res = await fetch(apiUrl);
      const data = await res.json();
  
      if (!data.items) return [];
  
      return data.items.map(item => ({
        videoId: item.id.videoId,
        title: item.snippet.title,
        thumbnail: item.snippet.thumbnails.medium.url
      }));
    } catch (err) {
      console.error("YouTube API Error:", err);
      return [];
    }
  }
  
  function renderRecipe(recipe) {
    // 제목
    document.querySelector('.recipe-subheading').innerHTML = `<strong>🥢 ${recipe.title}</strong>`;
  
    // 재료
    const ingredientsHTML = recipe.ingredients.map(item => `<li>${item}</li>`).join('');
    document.querySelector('.recipe-subheading').nextElementSibling.nextElementSibling.innerHTML = ingredientsHTML;
  
    // 만드는 법
    const stepsHTML = recipe.steps.map(step => `<li>${step}</li>`).join('');
    document.querySelector('ol').innerHTML = stepsHTML;
  }
  
  function renderYoutubeThumbnails(videos) {
    const container = document.querySelector('.recipe-right-box');
    let html = `<h2>유튜브 영상 보러가기</h2>`;
  
    videos.forEach(video => {
      html += `
        <a href="https://www.youtube.com/watch?v=${video.videoId}" target="_blank">
          <img class="recipe-video-slot" src="${video.thumbnail}" alt="${video.title}" title="${video.title}">
        </a>
      `;
    });
  
    container.innerHTML = html;
  }
  
  async function loadRecipe() {
    const foodId = localStorage.getItem("selectedFood");
    const recipe = recipeData[foodId];
  
    if (!recipe) {
      alert("레시피 정보를 찾을 수 없습니다.");
      return;
    }
  
    renderRecipe(recipe);
  
    const youtubeResults = await fetchYoutubeVideos(recipe.youtubeQuery);
    renderYoutubeThumbnails(youtubeResults);
  }
  
  document.addEventListener("DOMContentLoaded", loadRecipe);
  
  
  