// HTML 요소 가져오기
const calendarDiv = document.getElementById('calendar');
const inputTitle = document.getElementById('input-title');
const form = document.getElementById('entry-form');
const applyBtn = document.getElementById('apply-btn');
const listDiv = document.getElementById('transaction-list');
const prevMonthBtn = document.getElementById('prev-month-btn');
const nextMonthBtn = document.getElementById('next-month-btn');
const currentMonthTitle = document.getElementById('current-month');

// 상태 관리
let selectedDate = null;
let currentDate = new Date();
let allTransactions = [];

// 페이지가 처음 로드될 때 실행될 함수
document.addEventListener('DOMContentLoaded', async () => {
    renderCalendar(currentDate);
    await loadInitialData();
});

/**
 * 서버에서 모든 거래 내역을 불러와 allTransactions 배열에 저장합니다.
 */
async function loadInitialData() {
    const res = await fetch('/transactions');
    const data = await res.json();
    allTransactions = data.transactions || [];
}

/**
 * 달력을 생성하고 화면에 렌더링하는 함수
 * @param {Date} date - 달력을 생성할 기준 날짜
 */
function renderCalendar(date) {
    calendarDiv.innerHTML = '';
    const year = date.getFullYear();
    const month = date.getMonth();
    currentMonthTitle.textContent = `${year}년 ${month + 1}월`;
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const startDayOfWeek = firstDayOfMonth.getDay();
    const totalDays = lastDayOfMonth.getDate();

    for (let i = 0; i < startDayOfWeek; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.classList.add('day', 'empty');
        calendarDiv.appendChild(emptyDay);
    }
    for (let i = 1; i <= totalDays; i++) {
        const day = document.createElement('div');
        day.classList.add('day');
        day.textContent = i;
        day.onclick = () => selectDate(year, month, i);
        calendarDiv.appendChild(day);
    }
}

/**
 * 날짜를 선택했을 때 호출되는 함수
 */
function selectDate(year, month, day) {
  document.getElementById('input-container').classList.remove('centered-prompt');
  listDiv.style.display = 'block';

  const monthStr = String(month + 1).padStart(2, '0');
  const dayStr = String(day).padStart(2, '0');
  selectedDate = `${year}-${monthStr}-${dayStr}`;
  
  inputTitle.textContent = `${selectedDate} 내역 입력`;
  form.style.display = 'flex';

  const filteredTransactions = allTransactions.filter(t => t.date === selectedDate);
  updateList(filteredTransactions);
}

// "이전 달", "다음 달" 버튼 클릭 이벤트
prevMonthBtn.onclick = () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar(currentDate);
};
nextMonthBtn.onclick = () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar(currentDate);
};

// "적용" 버튼 클릭 시
applyBtn.onclick = async () => {
  const type = document.getElementById('type').value;
  const desc = document.getElementById('desc').value;
  const amount = document.getElementById('amount').value;

  if (!type || !desc || !amount || !selectedDate) {
      return alert('모든 항목을 입력하세요.');
  }

  const res = await fetch('/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ date: selectedDate, type, desc, amount })
  });
  
  const data = await res.json();
  allTransactions = data.transactions;

  const filteredTransactions = allTransactions.filter(t => t.date === selectedDate);
  updateList(filteredTransactions);
};

// 삭제 버튼 클릭을 감지하는 이벤트 리스너
listDiv.addEventListener('click', function(event) {
    if (event.target.classList.contains('delete-btn')) {
        const transactionString = event.target.dataset.transaction;
        const transactionToDelete = JSON.parse(transactionString);
        handleDelete(transactionToDelete);
    }
});

/**
 * 서버에 삭제 요청을 보내고, UI를 업데이트하는 함수
 * @param {object} transactionToDelete - 삭제할 거래 내역 객체
 */
async function handleDelete(transactionToDelete) {
    const res = await fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transactionToDelete)
    });
    const data = await res.json();
    allTransactions = data.transactions;

    const filtered = allTransactions.filter(t => t.date === selectedDate);
    updateList(filtered);
}

/**
 * 거래 내역 리스트 업데이트 함수
 * @param {Array} transactions - 화면에 표시할 거래 내역 배열
 */
function updateList(transactions) {
  if (transactions.length === 0) {
    listDiv.innerHTML = `<h3>거래 내역</h3><p>해당 날짜의 거래 내역이 없습니다.</p>`;
    return;
  }

  let html = `
    <h3>거래 내역</h3>
    <table>
      <thead><tr><th>날짜</th><th>유형</th><th>내역</th><th>금액</th><th></th></tr></thead>
      <tbody>
        ${transactions.map(t => {
          const transactionData = JSON.stringify(t);
          return `
            <tr>
              <td>${t.date}</td>
              <td>${t.type}</td>
              <td>${t.desc}</td>
              <td class="${t.type === '입금' ? 'deposit' : ''}">
                ${parseInt(t.amount).toLocaleString()} 원
              </td>
              <td>
                <button class="delete-btn" data-transaction='${transactionData}'>&times;</button>
              </td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;
  listDiv.innerHTML = html;
}