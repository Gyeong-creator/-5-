const togglePassword = document.getElementById('toggle-password');
const passwordField = document.getElementById('password-field');
const loginBtn = document.getElementById('login-btn');
const idField = document.getElementById('id-field');


togglePassword.addEventListener('click', function () {
    // 비밀번호 필드의 타입을 'password'에서 'text'로, 또는 그 반대로 변경
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);

    // 텍스트 내용 변경
    this.textContent = type === 'password' ? '보기' : '숨김';
});

// 로그인 버튼 클릭
loginBtn.addEventListener('click', function (e) {
  e.preventDefault(); // 폼 새로고침 막기

  const id = idField.value.trim();
  const password = passwordField.value;

  if (!id || !password) {
    alert("아이디와 비밀번호를 입력하세요!");
    return;
  }

  fetch('/login_check', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ id, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("로그인 성공!");
      window.location.href = "/";
    } else {
      alert("로그인 실패!");
    }
  })
  .catch(err => {
    console.error("Error:", err);
    alert("서버 오류 발생");
  });
});
