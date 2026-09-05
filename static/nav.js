    //click sign_in_btn -> window.popup-> popup.innerHTML -> 表格 fetch post /api/sign_in -> ///token or + logout button 
    //                                                       sign_up_btn -> window.popup-> popup.innerHTML
document.addEventListener("DOMContentLoaded", () => {
    const navAndAuthHTML = `
    <nav class="navbar">
      <div class="navbar-section">
        <a href="/" class="logo">台北一日遊</a>
        <ul class="navbar-links">
          <a href="#">預定行程</a>
          <button id="nav-auth-btn">登入/註冊</button>
        </ul>
      </div>
    </nav>
    <div id="auth-popup" style="display: none;"></div>
    <div id="auth-overlay" style="display: none;"></div>
  `;
    document.body.insertAdjacentHTML('afterbegin', navAndAuthHTML);

    const navAuthBtn = document.getElementById('nav-auth-btn');
    const authPopup = document.getElementById('auth-popup');
    const authOverlay = document.getElementById('auth-overlay'); // 遮罩

    const bookingLink = document.querySelector('.navbar-links a');
    
    bookingLink.addEventListener('click', (e) => {
        e.preventDefault();
        
        const token = localStorage.getItem('token');
        if (token) {
            window.location.href = '/booking';
        } else {
            openPopup();
        }
    });

    const signInTemplate = `
        <div class="decorator-bar"></div>
        <div class="auth-popup-content">
        <span class="close-btn" id="close-popup-btn">&times;</span>
        <h2>登入會員帳號</h2>
        <form id="signin-form">
            <input type="email" name="email" placeholder="輸入電子信箱" required>
            <input type="password" name="password" placeholder="輸入密碼" required>
            <button type="submit">登入帳戶</button>
        </form>
        <div id="auth-message" style="text-align: center; margin-top: 10px; font-size: 16px;"></div>
        <p class="switch-form-text" id="go-to-signup" style="cursor: pointer;">還沒有帳戶?點此註冊</p>
        </div>
    `;

    const signUpTemplate = `
        <div class="decorator-bar"></div>
        <div class="auth-popup-content">
        <span class="close-btn" id="close-popup-btn">&times;</span>
        <h2>註冊會員帳號</h2>
        <form id="signup-form">
            <input type="text" name="name" placeholder="輸入姓名" required>
            <input type="email" name="email" placeholder="輸入電子郵件" required>
            <input type="password" name="password" placeholder="輸入密碼" required>
            <button type="submit">註冊新帳戶</button>
        </form>
        <div id="auth-message" style="text-align: center; margin-top: 10px; font-size: 16px;"></div>
        <p class="switch-form-text" id="go-to-signin" style="cursor: pointer;">已經有帳戶了?點此登入</p>
        </div>
    `;

    function openPopup() {
        authPopup.style.display = 'block';
        if (authOverlay) authOverlay.style.display = 'block';
        renderSignIn();
    }

    window.openAuthPopup = openPopup;

    function closePopup() {
        authPopup.style.display = 'none';
        if (authOverlay) authOverlay.style.display = 'none';
        authPopup.innerHTML = ''; 
    }

    function renderSignIn() {
        authPopup.innerHTML = signInTemplate;
        
        document.getElementById('close-popup-btn').addEventListener('click', closePopup); //
        document.getElementById('go-to-signup').addEventListener('click', renderSignUp);
        document.getElementById('signin-form').addEventListener('submit', handleSignIn);
    }

    function renderSignUp() {
        authPopup.innerHTML = signUpTemplate;

        document.getElementById('close-popup-btn').addEventListener('click', closePopup);//
        document.getElementById('go-to-signin').addEventListener('click', renderSignIn);
        document.getElementById('signup-form').addEventListener('submit', handleSignUp);
    }

    async function handleSignIn(event) {
        event.preventDefault();
        const form = event.target;
        const email = form.email.value;
        const password = form.password.value;
        const msgBox = document.getElementById('auth-message');

        try {
        const response = await fetch('/api/sign_in', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const result = await response.json();

        if (response.ok && result.token) {
            localStorage.setItem('token', result.token);
            window.location.reload();
        } else {
        msgBox.style.color = 'red';
        msgBox.textContent = result.message;
        }
        } catch (error) {
        console.error('登入發生錯誤:', error);
        }
    }

    async function handleSignUp(event) {
        event.preventDefault();
        const form = event.target;
        const name = form.name.value;
        const email = form.email.value;
        const password = form.password.value;
        const msgBox = document.getElementById('auth-message');

        try {
        const response = await fetch('/api/sign_up', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const result = await response.json();

        if (response.ok && result.ok) {
            //alert('註冊成功！請重新登入。');
            //renderSignIn();
            msgBox.style.color = 'green';
            msgBox.textContent = '註冊成功！請重新登入。';
        } else {
            msgBox.style.color = 'red';
            msgBox.textContent = result.message;
        }
        } catch (error) {
        console.error('註冊發生錯誤:', error);
        }
    }

    async function handleSignOut() {
        localStorage.removeItem('token');
        window.location.reload();
    }

    async function checkAuthStatus() {
        const token = localStorage.getItem('token');
        
        if (!token) {
        navAuthBtn.textContent = '登入/註冊';
        navAuthBtn.onclick = openPopup;
        return;
        }

        try {
        const response = await fetch('/api/auth', {
            method: 'GET',
            headers: {
            'Authorization': `Bearer ${token}`
            }
        });
        const result = await response.json();

        if (result.data) {
            navAuthBtn.textContent = '登出系統';
            navAuthBtn.onclick = handleSignOut;
        } else {
            localStorage.removeItem('token');
            navAuthBtn.textContent = '登入/註冊';
            navAuthBtn.onclick = openPopup;
        }
        } catch (error) {
        console.error('驗證狀態錯誤:', error);
        localStorage.removeItem('token');
        navAuthBtn.textContent = '登入/註冊';
        navAuthBtn.onclick = openPopup;
        }
    }

    window.addEventListener('click', (event) => {
        if (event.target === authOverlay) {
        closePopup();
        }
    });
    checkAuthStatus();
});