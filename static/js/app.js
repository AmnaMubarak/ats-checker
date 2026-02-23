/* ===== Theme Toggle ===== */
(function(){
    const saved = localStorage.getItem('theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
    else if (window.matchMedia('(prefers-color-scheme: light)').matches) document.documentElement.setAttribute('data-theme','light');
})();

document.getElementById('themeToggle').addEventListener('click', () => {
    const html = document.documentElement;
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
});

/* ===== Upload Logic ===== */
const dropZone=document.getElementById('dropZone'),fileInput=document.getElementById('fileInput'),fileRow=document.getElementById('fileRow'),fileNameEl=document.getElementById('fileName'),fileExtEl=document.getElementById('fileExt'),removeFile=document.getElementById('removeFile'),btnAnalyze=document.getElementById('btnAnalyze'),uploadView=document.getElementById('uploadView'),loader=document.getElementById('loader'),resultsView=document.getElementById('resultsView'),errorMsg=document.getElementById('errorMsg');
let selectedFile=null;

dropZone.addEventListener('click',()=>fileInput.click());
dropZone.addEventListener('dragover',e=>{e.preventDefault();dropZone.classList.add('drag-over')});
dropZone.addEventListener('dragleave',()=>dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop',e=>{e.preventDefault();dropZone.classList.remove('drag-over');if(e.dataTransfer.files.length)handleFile(e.dataTransfer.files[0])});
fileInput.addEventListener('change',()=>{if(fileInput.files.length)handleFile(fileInput.files[0])});

function handleFile(f){
    const ext=f.name.split('.').pop().toLowerCase();
    if(!['pdf','docx'].includes(ext)){showError('Please upload a PDF or DOCX file.');return}
    if(f.size>5*1024*1024){showError('File too large. Max 5 MB.');return}
    selectedFile=f;
    fileExtEl.textContent=ext.toUpperCase();
    fileExtEl.style.background=ext==='pdf'?'var(--danger-bg)':'var(--info-bg)';
    fileExtEl.style.color=ext==='pdf'?'var(--danger)':'var(--info)';
    fileNameEl.textContent=f.name;
    fileRow.classList.add('visible');
    btnAnalyze.classList.add('visible');
    hideError();
}

removeFile.addEventListener('click',()=>{selectedFile=null;fileInput.value='';fileRow.classList.remove('visible');btnAnalyze.classList.remove('visible')});
function showError(m){errorMsg.textContent=m;errorMsg.classList.add('visible')}
function hideError(){errorMsg.classList.remove('visible')}

btnAnalyze.addEventListener('click',async()=>{
    if(!selectedFile)return;
    hideError();btnAnalyze.disabled=true;
    uploadView.classList.add('hidden');loader.classList.add('visible');resultsView.classList.remove('visible');
    const form=new FormData();form.append('resume',selectedFile);
    try{
        const res=await fetch('/api/check',{method:'POST',body:form});
        const data=await res.json();
        loader.classList.remove('visible');
        if(!res.ok){showError(data.error||'Something went wrong.');uploadView.classList.remove('hidden');btnAnalyze.disabled=false;return}
        renderResults(data);
    }catch{loader.classList.remove('visible');uploadView.classList.remove('hidden');document.getElementById('btnBack').classList.remove('visible');showError('Network error. Please try again.')}
    btnAnalyze.disabled=false;
});

/* Tabs */
document.querySelectorAll('.tab-btn').forEach(b=>{b.addEventListener('click',()=>{
    document.querySelectorAll('.tab-btn').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');document.getElementById('tab-'+b.dataset.tab).classList.add('active');
})});

function scoreColor(p){return p>=80?'var(--success)':p>=60?'var(--info)':p>=40?'var(--warning)':'var(--danger)'}
function badgeFor(p){return p>=80?['badge-excellent','Excellent']:p>=60?['badge-good','Good']:p>=40?['badge-fair','Fair']:['badge-poor','Needs Work']}

const CAT_ICONS={'Contact Information':'&#9993;','Resume Sections':'&#9776;','Work Experience':'&#9733;','Education':'&#127891;','Formatting & Structure':'&#9638;','ATS Compatibility':'&#10004;','Action Verbs':'&#9889;','Measurable Results':'&#9650;','Hard Skills':'&#9881;','Readability':'&#9998;','Writing Consistency':'&#8801;','Keyword Optimization':'&#9906;'};

function goBack(){
    resultsView.classList.remove('visible');uploadView.classList.remove('hidden');
    document.getElementById('btnBack').classList.remove('visible');
    selectedFile=null;fileInput.value='';fileRow.classList.remove('visible');btnAnalyze.classList.remove('visible');
    document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active',i===0));
    document.querySelectorAll('.tab-panel').forEach((p,i)=>p.classList.toggle('active',i===0));
}

document.getElementById('btnBack').addEventListener('click',goBack);

function renderResults(data){
    resultsView.classList.add('visible');
    document.getElementById('btnBack').classList.add('visible');
    const R=60,C=2*Math.PI*R,arc=document.getElementById('scoreArc');
    arc.style.strokeDasharray=C;arc.style.strokeDashoffset=C;
    const sc=data.overall_score;
    const col=sc>=80?'var(--success)':sc>=60?'var(--info)':sc>=40?'var(--warning)':'var(--danger)';
    arc.style.stroke=col;
    const sn=document.getElementById('scoreNum');sn.style.color=col;
    setTimeout(()=>{arc.style.strokeDashoffset=C-(sc/100)*C},80);
    animateNum(sn,0,sc,1100);
    document.getElementById('verdict').textContent=data.verdict;
    document.getElementById('metaChips').innerHTML=`<span class="meta-chip">${data.file_type}</span><span class="meta-chip">${data.word_count} words</span><span class="meta-chip">${data.page_count} page${data.page_count>1?'s':''}</span><span class="meta-chip">${data.categories.length} checks</span>`;
    const ss=data.summary_stats||{};
    animateNum(document.getElementById('statPass'),0,ss.passed||0,800);
    animateNum(document.getElementById('statWarn'),0,ss.warnings||0,800);
    animateNum(document.getElementById('statFail'),0,ss.failed||0,800);

    const ov=document.getElementById('catOverview');ov.innerHTML='<div class="cat-overview-title">Category Breakdown</div>';
    data.categories.forEach((cat,i)=>{const c=scoreColor(cat.percentage);const it=document.createElement('div');it.className='cat-bar-item';it.innerHTML=`<div class="cat-bar-top"><span class="cat-bar-name">${cat.name}</span><span class="cat-bar-pct" style="color:${c}">${cat.percentage}%</span></div><div class="cat-bar-track"><div class="cat-bar-fill" style="width:0;background:${c}"></div></div>`;ov.appendChild(it);setTimeout(()=>{it.querySelector('.cat-bar-fill').style.width=cat.percentage+'%'},100+i*60)});

    const det=document.getElementById('tab-details');det.innerHTML='';
    data.categories.forEach(cat=>{const[bc,bt]=badgeFor(cat.percentage);const d=document.createElement('div');d.className='category';d.innerHTML=`<div class="cat-head"><div class="left"><div class="cat-icon-sm" style="background:${scoreColor(cat.percentage)}18;color:${scoreColor(cat.percentage)}">${CAT_ICONS[cat.name]||'&#9632;'}</div><h3>${cat.name}<span class="score-sm">${cat.score}/${cat.max_score}</span></h3></div><div class="right"><span class="badge ${bc}">${bt}</span><span class="chevron">&#9662;</span></div></div><div class="cat-body"><div class="findings">${cat.findings.map(f=>`<div class="finding finding-${f.type}"><div class="f-dot">${f.type==='pass'?'&#10003;':f.type==='fail'?'&#10007;':f.type==='warning'?'!':'i'}</div><span>${f.message}</span></div>`).join('')}</div></div>`;det.appendChild(d);d.querySelector('.cat-head').addEventListener('click',()=>d.classList.toggle('open'))});

    const tips=document.getElementById('tab-tips');tips.innerHTML='';
    if(data.tips&&data.tips.length){data.tips.forEach(tip=>{const t=document.createElement('div');t.className='tip-card';t.innerHTML=`<span class="tip-priority tip-${tip.priority}">${tip.priority} priority</span><h4>${tip.title}</h4><p class="tip-desc">${tip.description}</p><p class="tip-impact">${tip.impact}</p>`;tips.appendChild(t)})}
    else{tips.innerHTML='<p style="color:var(--text-3);text-align:center;padding:40px">No improvement tips — your resume is well optimized!</p>'}
}

function animateNum(el,from,to,dur){const st=performance.now();(function u(n){const p=Math.min((n-st)/dur,1);el.textContent=Math.round(from+(to-from)*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(u)})(st)}

document.getElementById('btnNew').addEventListener('click',goBack);
