const togglePassword = document.getElementById('toggle-password');
const passwordField = document.getElementById('password-field');

togglePassword.addEventListener('click', function () {
    // 비밀번호 필드의 타입을 'password'에서 'text'로, 또는 그 반대로 변경
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);

    // 텍스트 내용 변경
    this.textContent = type === 'password' ? '보기' : '숨김';
});