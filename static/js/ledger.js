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


// 페이지가 처음 로드될 때 실행될 함수
document.addEventListener('DOMContentLoaded', async () => {
    renderCalendar(currentDate);
});


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
 * (!!!) 날짜를 선택했을 때 호출되는 함수 (API 호출로 변경)
 */
async function selectDate(year, month, day) {
    document.getElementById('input-container').classList.remove('centered-prompt');
    listDiv.style.display = 'block';

    const monthStr = String(month + 1).padStart(2, '0');
    const dayStr = String(day).padStart(2, '0');
    selectedDate = `${year}-${monthStr}-${dayStr}`;
    
    inputTitle.textContent = `${selectedDate} 내역 입력`;
    form.style.display = 'flex';

    // (!!!) 기존 allTransactions.filter 대신 API를 직접 호출합니다.
    try {
        // app.py에 만든 새 API 경로를 호출합니다.
        const res = await fetch(`/transactions-by-date?date=${selectedDate}`);
        
        if (!res.ok) {
            // 서버가 401(로그인 필요) 등 에러를 보낸 경우
            const errorData = await res.json();
            throw new Error(errorData.message || '데이터를 불러오는 데 실패했습니다.');
        }

        const data = await res.json();
        
        // (!!!) API 응답 결과(해당 날짜의 내역)로 리스트를 바로 업데이트합니다.
        updateList(data.transactions || []); 

    } catch (error) {
        console.error('Error fetching date-specific transactions:', error);
        listDiv.innerHTML = `<h3>거래 내역</h3><p style="color: red;">${error.message}</p>`;
    }
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
  
  // (!!!) '날짜별 조회'로 변경되어 allTransactions 대신
  // (!!!) 현재 선택된 날짜의 목록만 다시 불러옵니다.
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth();
  const currentDay = parseInt(selectedDate.split('-')[2]);
  await selectDate(currentYear, currentMonth, currentDay);
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
 */
async function handleDelete(transactionToDelete) {
    const res = await fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transactionToDelete)
    });
    const data = await res.json();

    // (!!!) '날짜별 조회'로 변경되어 allTransactions 대신
    // (!!!) 현재 선택된 날짜의 목록만 다시 불러옵니다.
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();
    const currentDay = parseInt(selectedDate.split('-')[2]);
    await selectDate(currentYear, currentMonth, currentDay);
}

/**
 * 거래 내역 리스트 업데이트 함수
 * @param {Array} transactions - 화면에 표시할 거래 내역 배열
 */
function updateList(transactions) {
  console.log(transactions);
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
          // (!!!) 날짜 형식을 DB에서 온 그대로(ISO) 표시하지 않고,
          // (!!!) selectedDate (YYYY-MM-DD)를 사용합니다. (또는 t.date를 파싱)
          return `
            <tr>
              <td>${selectedDate}</td> 
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