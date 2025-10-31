console.log('statistics.js loaded');

(function () {
	// ---------- Helpers ----------
	const won = n => (Math.round(n)).toLocaleString('ko-KR') + '원';
	const sum = a => a.reduce((x,y)=>x+y,0);

	// ---------- State ----------
	const defaultState = {
		monthDaysLabels: Array.from({length:30}, (_,i)=> `${i+1}일`),
		monthThis: [0,12000,24000,38000,42000,54000,60000,71000,82000,86000,90000,97000,98000,101000,103000,108000,112000,118000,121000,127000,130000,133000,138000,142000,149000,153000,158000,165000,171000,180000],
		monthPrev:  [0, 8000,14000,19000,25000,29000,32000,37000,41000,43000,47000,50000,54000,59000,62000,64000,69000,73000,77000,80000,83000,86000,90000,94000,98000,100000,103000,106000,109000,112000],
		monthCats: { "식비":34, "주거/통신":12, "생활용품":8, "의복/미용":7, "건강/문화":8, "교육/육아":4, "교통/차량":14, "경조사/회비":3, "세금/이자":4, "용돈/기타":6 },
		weeksLabels: Array.from({length:10}, (_,i)=> `${i+1}주`),
		weeksTotals: [110000, 90000, 120000, 150000, 130000, 170000, 140000, 160000, 155000, 180000],
		incomeTotal: 568752,
		expense: { total: 958673, card: 656461, transfer: 302212, other: 0 },
		};
	let state = (typeof window.__STATS__ !== 'undefined' && window.__STATS__) || defaultState;

	// ---------- UI binds ----------
	function bindTabs(){
		document.querySelectorAll('.tab').forEach(t=>{
			t.addEventListener('click', ()=>{
			document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
			document.querySelectorAll('.panel').forEach(p=>p.classList.add('hidden'));
			t.classList.add('active');
			
			document.getElementById(t.dataset.panel).classList.remove('hidden');

			// balanceCard, don't remove
            const balanceCard = document.getElementById("balanceCard");
            if (t.dataset.panel === "monthlyTotal") {
                balanceCard.classList.remove("hidden");
            } else {
                balanceCard.classList.add("hidden");
            }
			
			});
		});
	}

	// ---------- Dates ----------
	function setRanges(){
		const now = new Date();
		const yyyy = now.getFullYear();
		const mm = (now.getMonth()+1).toString().padStart(2,'0');
		const last = new Date(yyyy, now.getMonth()+1, 0).getDate();
		document.getElementById('rangeMonthly').textContent = `${yyyy}.${mm}.01 ~ ${yyyy}.${mm}.${last}`;
		document.getElementById('rangeMonthlySpend').textContent = `${yyyy}.${mm}.01 ~ ${yyyy}.${mm}.${last}`;
		document.getElementById('balanceAsOf').textContent = `${mm}월 ${last}일 기준`;
	}

	// ---------- SVG Line Chart ----------
	function lineChart(el, series, labels){
		const w = el.clientWidth || 600, h = el.clientHeight||220;
		const pad = {l:28, r:12, t:12, b:24};
		const W = Math.max(320,w), H = Math.max(160,h);
		const NS='http://www.w3.org/2000/svg';
		el.innerHTML = '';
		const svg = document.createElementNS(NS,'svg'); svg.setAttribute('viewBox',`0 0 ${W} ${H}`); el.appendChild(svg);

		const ymax = Math.max(1, ...series.flat());
		const X = i => pad.l + (W-pad.l-pad.r) * (i/(labels.length-1 || 1));
		const Y = v => pad.t + (H-pad.t-pad.b) * (1 - (v/ymax));

		const grid = document.createElementNS(NS,'g'); grid.setAttribute('class','grid'); svg.appendChild(grid);
		for(let i=0;i<=5;i++){ const y=pad.t+(H-pad.t-pad.b)*i/5;
			const ln=document.createElementNS(NS,'line'); ln.setAttribute('x1',pad.l); ln.setAttribute('x2',W-pad.r); ln.setAttribute('y1',y); ln.setAttribute('y2',y); grid.appendChild(ln); }

		const axis=document.createElementNS(NS,'g'); axis.setAttribute('class','axis'); svg.appendChild(axis);
		const xt=(txt,x)=>{ const t=document.createElementNS(NS,'text'); t.setAttribute('x',x); t.setAttribute('y',H-6); t.setAttribute('text-anchor','middle'); t.textContent=txt; axis.appendChild(t); };
		xt(labels[0]||'', X(0)); xt(labels[labels.length-1]||'', X(labels.length-1));

		const colors=['var(--accent)','var(--accent2)'];
		series.forEach((arr,si)=>{
			const p=document.createElementNS(NS,'path'); let d='';
			arr.forEach((v,i)=>{ d+=(i?' L ':'M ')+X(i)+' '+Y(v); });
			p.setAttribute('d',d); p.setAttribute('fill','none'); p.setAttribute('stroke',colors[si%colors.length]); p.setAttribute('stroke-width','3'); p.setAttribute('stroke-linecap','round'); svg.appendChild(p);
			const dot=document.createElementNS(NS,'circle'); dot.setAttribute('cx',X(arr.length-1)); dot.setAttribute('cy',Y(arr[arr.length-1]||0)); dot.setAttribute('r',4); dot.setAttribute('fill',colors[si%colors.length]); svg.appendChild(dot);
		});
	}

  	// ---------- Renderers ----------
	function renderCharts(){
		const mt = state.monthThis;
		document.getElementById('mtSum').textContent = won(mt[mt.length-1]||0);
		const mtDelta = (mt[mt.length-1]||0) - (mt[mt.length-2]||0);
		document.getElementById('mtDelta').textContent = (mtDelta>=0?'+':'') + won(mtDelta) + ' (오늘 증감)';
		lineChart(document.getElementById('chartMonthlyTotal'), [mt], state.monthDaysLabels);

		const ms = state.monthThis, mp = state.monthPrev;
		const diff = (ms[ms.length-1]||0) - (mp[Math.min(mp.length-1, ms.length-1)]||0);
		document.getElementById('msSum').textContent = '오늘까지 ' + won(ms[ms.length-1]||0) + ' 썼어요';
		document.getElementById('msDelta').textContent =
		diff>=0 ? `지난달보다 ${won(diff)} 더 쓰는 중` : `지난달보다 ${won(-diff)} 덜 쓰는 중`;
		lineChart(document.getElementById('chartMonthlySpend'), [ms, mp], state.monthDaysLabels);

		const list = document.getElementById('categoryBreak'); list.innerHTML='';
		Object.entries(state.monthCats).forEach(([k,v])=>{
			const span=document.createElement('span'); span.className='pill'; span.textContent=`${k} ${v}%`; list.appendChild(span);
		});

		document.getElementById('wtSum').textContent = won(sum(state.weeksTotals));
		lineChart(document.getElementById('chartWeekly'), [state.weeksTotals], state.weeksLabels);
	}

	function renderBalance(){
		const inc = state.incomeTotal||0;
		const exp = state.expense?.total||0;
		const card = state.expense?.card||0;
		const transfer = state.expense?.transfer||0;
		const other = state.expense?.other ?? Math.max(0, exp - card - transfer);
		document.getElementById('incomeTotal').textContent = won(inc);
		document.getElementById('expenseTotal').textContent = won(exp);
		document.getElementById('expenseCard').textContent = won(card);
		document.getElementById('expenseTransfer').textContent = won(transfer);
		document.getElementById('expenseOther').textContent = won(other);
		const remain = inc - exp;
		const el = document.getElementById('remainAmount');
		el.textContent = (remain>=0?'':'-') + won(Math.abs(remain));
		el.style.color = remain>=0 ? 'var(--good)' : '#2563eb';
	}

  	function renderAll(){ setRanges(); renderBalance(); renderCharts(); }

	// ---------- Init ----------
	function init(){
		bindTabs();
		renderAll();
		window.addEventListener('resize', renderCharts);
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
})();
