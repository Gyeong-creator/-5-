console.log('statistics.js loaded');

(function () {

	// ---------- Helpers ----------
	const won = n => (Math.round(n)).toLocaleString('ko-KR') + '원';
	const sum = a => a.reduce((x, y) => x + y, 0);
	const lastDay = (y, m) => new Date(y, m, 0).getDate(); // m: 1~12

	function setRangeFor(elId, year, month){
		const mm = String(month).padStart(2, '0');
		const last = lastDay(year, month);
		const el = document.getElementById(elId);
		if (el) el.textContent = `${year}.${mm}.01 ~ ${year}.${mm}.${last}`;
	}

	function prevYM(year, month){ // month: 1~12
		return month === 1 ? {year: year-1, month: 12} : {year, month: month-1};
	}

	function alignToLen(arr, len){
		if (arr.length === len) return arr.slice();
		if (arr.length > len)   return arr.slice(0, len);
		const out = arr.slice();
		const last = out[out.length-1] || 0;
		while(out.length < len) out.push(last);
		return out;
	}

	// ---------- 기본 상태(주간/카테고리용 더미) ----------
	const defaultState = {
		weeksLabels: Array.from({ length: 10 }, (_, i) => `${i + 1}주`),
		weeksTotals: [110000, 90000, 120000, 150000, 130000, 170000, 140000, 160000, 155000, 180000],
		monthCats: { "식비": 34, "주거/통신": 12, "생활용품": 8, "의복/미용": 7, "건강/문화": 8, "교육/육아": 4, "교통/차량": 14, "경조사/회비": 3, "세금/이자": 4, "용돈/기타": 6 },
		incomeTotal: 568752,
		expense: { total: 958673, card: 656461, transfer: 302212, other: 0 },
	};
	let state = (typeof window.__STATS__ !== 'undefined' && window.__STATS__) || defaultState;

	// ---------- Tabs ----------
	function bindTabs() {
		document.querySelectorAll('.tab').forEach(t => {
		t.addEventListener('click', () => {
			document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
			document.querySelectorAll('.panel').forEach(p => p.classList.add('hidden'));
			t.classList.add('active');

			const target = document.getElementById(t.dataset.panel);
			if (target) target.classList.remove('hidden');

			const balanceCard = document.getElementById("balanceCard");
			if (t.dataset.panel === "monthlyTotal") balanceCard.classList.remove("hidden");
			else balanceCard.classList.add("hidden");
		});
		});
	}

	// ---------- 공통 Chart.js 렌더 ----------
	function renderChart(canvas, datasets, labels) {
		const ctx = canvas.getContext('2d');
		if (canvas._chartInstance) canvas._chartInstance.destroy();
		const chart = new Chart(ctx, {
		type: 'line',
		data: { labels, datasets },
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: { legend: { display: true, position: 'top' } },
			scales: { y: { beginAtZero: true } }
		}
		});
		canvas._chartInstance = chart;
	}

	// ---------- 데이터 요청 ----------
	async function fetchMonthlySpend(year, month) {
		const res = await fetch(`/api/stats/monthly-spend?year=${year}&month=${month}`);
		if (!res.ok) throw new Error('monthly-spend api failed');
		return res.json(); // { labels, dailySpend, dailyIncome, cumSpend, cumIncome, totalSpend, totalIncome }
	}

	// ---------- 월간 합계 (수입 - 지출 = 순변화) ----------
	async function updateMonthlyTotalSection() {
		const now = new Date();
		const yyyy = now.getFullYear();
		const mm = now.getMonth() + 1;
	
		// 기존 기간 라벨 함수 그대로 사용
		setRangeFor('rangeMonthly', yyyy, mm);
	
		// ⚠️ 이 함수가 {labels, cumSpend, cumIncome}를 반환해야 해요.
		//   (백엔드의 /api/stats/monthly-total 응답에 맞춰주세요)
		const { labels = [], cumSpend = [], cumIncome = [] } =
		await fetchMonthlySpend(yyyy, mm);
	
		// 누적 순변화 = 누적수입 − 누적지출
		const len = Math.max(cumIncome.length, cumSpend.length);
		const cumNet = Array.from({ length: len }, (_, i) =>
		(cumIncome[i] || 0) - (cumSpend[i] || 0)
		);
	
		// KPI (오늘 값/증감)
		const lastVal = cumNet.at(-1) || 0;
		const prevVal = cumNet.at(-2) || 0;
		const delta = lastVal - prevVal;
	
		document.getElementById('mtSum').textContent = won(lastVal);
		const deltaEl = document.getElementById('mtDelta');
		deltaEl.textContent = (delta >= 0 ? '+' : '') + won(delta) + ' (오늘 증감)';
		deltaEl.style.color = delta >= 0 ? 'var(--good)' : '#ef4444';
	
		// 차트: 기존 renderChart 유틸 유지
		// (renderChart(canvasEl, datasets[], labels) 형태였죠)
		const canvas = document.getElementById('chartMonthlyTotal');
		renderChart(
		canvas,
		[
			{
			label: '이달 누적 순변화 (수입 − 지출)',
			data: cumNet,
			borderColor: '#3b82f6',
			backgroundColor: 'rgba(59,130,246,0.15)',
			borderWidth: 3,
			tension: 0.3,
			fill: true,
			pointRadius: 0
			}
		],
		labels
		);
	}

	// --- 이번 달 남은 돈 카드 업데이트 ---
	async function updateBalanceCard() {
		const now = new Date();
		const y = now.getFullYear();
		const m = now.getMonth() + 1;
	
		// 이번 달 데이터 한 번만 호출
		const d = await fetchMonthlySpend(y, m);
	
		// API가 totals를 주면 그걸 쓰고, 없으면 누적 마지막 값을 fallback
		const income   = (d.totalIncome   ?? (d.cumIncome?.at(-1)   || 0)) | 0;
		const spend    = (d.totalSpend    ?? (d.cumSpend?.at(-1)    || 0)) | 0;
		const card     = (d.totalCard     ?? (d.cumCard?.at(-1)     || 0)) | 0;
		const transfer = (d.totalTransfer ?? (d.cumTransfer?.at(-1) || 0)) | 0;
	
		// 페이/기타는 서버에서 오면 사용, 없으면 (총지출 - 카드 - 이체)로 계산
		const otherRaw = (d.totalOther ?? (d.cumOther?.at(-1)));
		const other    = Number.isFinite(otherRaw) ? otherRaw : Math.max(0, spend - card - transfer);
	
		// DOM 반영
		document.getElementById('incomeTotal').textContent   = won(income);
		document.getElementById('expenseTotal').textContent  = won(spend);
		document.getElementById('expenseCard').textContent   = won(card);
		document.getElementById('expenseTransfer').textContent = won(transfer);
		document.getElementById('expenseOther').textContent  = won(other);
	
		const remain = income - spend;
		const el = document.getElementById('remainAmount');
		el.textContent = (remain >= 0 ? '' : '-') + won(Math.abs(remain));
		el.style.color = remain >= 0 ? 'var(--good)' : '#2563eb'; // 파랑(마이너스)
	}
  
  
  

	// ---------- 월간 지출 (이번달 지출 vs 지난달 지출 비교) ----------
	async function updateMonthlySpendSection() {
		const now = new Date();
		const y = now.getFullYear();
		const m = now.getMonth() + 1;
		const {year: py, month: pm} = prevYM(y, m);

		setRangeFor('rangeMonthlySpend', y, m);

		// 이번달/지난달 각각 요청
		const [{ labels: labelsCur = [], cumSpend: cumSpendCur = [] },
			{ labels: labelsPrev = [], cumSpend: cumSpendPrev = [] }] =
		await Promise.all([ fetchMonthlySpend(y, m), fetchMonthlySpend(py, pm) ]);

		// 라벨은 이번달 기준, 지난달 누적은 길이 맞춰 정렬
		const labels = labelsCur;
		const prevAligned = alignToLen(cumSpendPrev, labels.length);

		// KPI: 이번달 총 지출 + 지난달 대비 증감
		const curTotal = (cumSpendCur.at(-1) || 0);
		const prevSameDay = (prevAligned.at(-1) || 0);
		const diff = curTotal - prevSameDay;
		document.getElementById('msSum').textContent = `오늘까지 ${won(curTotal)} 썼어요`;
		document.getElementById('msDelta').textContent =
		diff >= 0 ? `지난달보다 ${won(diff)} 더 쓰는 중` : `지난달보다 ${won(-diff)} 덜 쓰는 중`;

		// Chart.js 두 줄(이번달/지난달 지출 누적)
		const canvas = document.getElementById('chartMonthlySpend'); // <canvas>
		renderChart(canvas, [
		{
			label: '이번달 누적 지출',
			data: cumSpendCur,
			borderColor: '#ef4444',               // 빨강
			backgroundColor: 'rgba(239,68,68,0.12)',
			borderWidth: 3,
			tension: 0.3,
			fill: true,
			pointRadius: 0
		},
		{
			label: '지난달 누적 지출',
			data: prevAligned,
			borderColor: '#9ca3af',               // 회색
			backgroundColor: 'rgba(156,163,175,0.12)',
			borderWidth: 2,
			tension: 0.3,
			fill: true,
			pointRadius: 0
		}
		], labels);
	}



	// ---------- 주간 합계----------
	function lineChart(el, series, labels) {
		const w = el.clientWidth || 600, h = el.clientHeight || 220;
		const pad = { l: 28, r: 12, t: 12, b: 24 };
		const W = Math.max(320, w), H = Math.max(160, h);
		const NS = 'http://www.w3.org/2000/svg';
		el.innerHTML = '';
		const svg = document.createElementNS(NS, 'svg');
		svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
		el.appendChild(svg);

		const ymax = Math.max(1, ...series.flat());
		const X = i => pad.l + (W - pad.l - pad.r) * (i / (labels.length - 1 || 1));
		const Y = v => pad.t + (H - pad.t - pad.b) * (1 - (v / ymax));

		const grid = document.createElementNS(NS, 'g');
		grid.setAttribute('class', 'grid');
		svg.appendChild(grid);
		for (let i = 0; i <= 5; i++) {
		const y = pad.t + (H - pad.t - pad.b) * i / 5;
		const ln = document.createElementNS(NS, 'line');
		ln.setAttribute('x1', pad.l);
		ln.setAttribute('x2', W - pad.r);
		ln.setAttribute('y1', y);
		ln.setAttribute('y2', y);
		grid.appendChild(ln);
		}

		const colors = ['var(--accent)'];
		series.forEach((arr, si) => {
		const p = document.createElementNS(NS, 'path');
		let d = '';
		arr.forEach((v, i) => { d += (i ? ' L ' : 'M ') + X(i) + ' ' + Y(v); });
		p.setAttribute('d', d);
		p.setAttribute('fill', 'none');
		p.setAttribute('stroke', colors[si % colors.length]);
		p.setAttribute('stroke-width', '3');
		p.setAttribute('stroke-linecap', 'round');
		svg.appendChild(p);
		});
	}

	// ---------- 주간/카테고리/잔액  ----------
	function renderChartsExceptMonthly() {
		// 카테고리 pills
		const list = document.getElementById('categoryBreak');
		list.innerHTML = '';
		Object.entries(state.monthCats).forEach(([k, v]) => {
		const span = document.createElement('span');
		span.className = 'pill';
		span.textContent = `${k} ${v}%`;
		list.appendChild(span);
		});

		// 주간 합계
		document.getElementById('wtSum').textContent = won(sum(state.weeksTotals));
		lineChart(document.getElementById('chartWeekly'), [state.weeksTotals], state.weeksLabels);
	}

	function renderBalance() {
		const inc = state.incomeTotal || 0;
		const exp = state.expense?.total || 0;
		const card = state.expense?.card || 0;
		const transfer = state.expense?.transfer || 0;
		const other = state.expense?.other ?? Math.max(0, exp - card - transfer);
		document.getElementById('incomeTotal').textContent = won(inc);
		document.getElementById('expenseTotal').textContent = won(exp);
		document.getElementById('expenseCard').textContent = won(card);
		document.getElementById('expenseTransfer').textContent = won(transfer);
		document.getElementById('expenseOther').textContent = won(other);
		const remain = inc - exp;
		const el = document.getElementById('remainAmount');
		el.textContent = (remain >= 0 ? '' : '-') + won(Math.abs(remain));
		el.style.color = remain >= 0 ? 'var(--good)' : '#2563eb';
	}

	// ---------- 초기화 ----------
	async function init() {
		bindTabs();
		renderBalance();
		await updateMonthlyTotalSection();  // Chart.js (합계 = 지출+수입)
		await updateMonthlySpendSection();  // Chart.js (이번달 vs 지난달 지출)
		updateBalanceCard();
		renderChartsExceptMonthly();        // 주간/카테고리 유지
	}

	if (document.readyState === 'loading')
		document.addEventListener('DOMContentLoaded', init);
	else
		init();

})();
