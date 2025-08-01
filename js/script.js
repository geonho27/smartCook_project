// 로그인 기능
document.addEventListener('DOMContentLoaded', () => {
  const loginBtn = document.querySelector('.login-button');
  const isLoggedIn = localStorage.getItem('loggedIn') === 'true';

  loginBtn.textContent = isLoggedIn ? 'Logout' : 'Login';

  loginBtn.addEventListener('click', () => {
    const loggedInNow = loginBtn.textContent === 'Login';
    localStorage.setItem('loggedIn', loggedInNow ? 'true' : 'false');
    loginBtn.textContent = loggedInNow ? 'Logout' : 'Login';
  });
});

// 탐색 버튼 활성화
function showSection(type) {
    const foodSection = document.getElementById('food-section');
    const ingredientSection = document.getElementById('ingredient-section');

    if (type === 'food') {
    foodSection.style.display = 'block';
    ingredientSection.style.display = 'none';
    } else {
    foodSection.style.display = 'none';
    ingredientSection.style.display = 'block';
    }
}