// qcm.js — simple reader for decks (Markdown) and TSV answer keys
(function(){
  const deckSelect = document.getElementById('deckSelect');
  const startBtn = document.getElementById('startBtn');
  const player = document.getElementById('player');
  const questionArea = document.getElementById('questionArea');
  const choicesArea = document.getElementById('choicesArea');
  const progress = document.getElementById('progress');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const finishBtn = document.getElementById('finishBtn');
  const result = document.getElementById('result');
  const scoreDiv = document.getElementById('score');
  const revealBtn = document.getElementById('revealBtn');
  const reviewDiv = document.getElementById('review');

  const decks = window.decksRaw || {};
  const tsvFiles = window.tsvFiles || {};

  Object.keys(decks).forEach(name => {
    const opt = document.createElement('option'); opt.value = name; opt.textContent = name; deckSelect.appendChild(opt);
  });

  let questions = [];
  let answersMap = {};
  let userAnswers = {};
  let currentIndex = 0;

  function normalize(s){ return (s||'').replace(/\s+/g,' ').trim(); }

  function parseDeck(md){
    const q = [];
    const re = /(?m)(?:^|\n)(\d+)\)\s*([^\n]+)\n([\s\S]*?)(?=(?:\n\d+\)|$))/g;
    let m;
    while((m=re.exec(md)) !== null){
      const id = m[1];
      const prompt = m[2].trim();
      const optsBlock = m[3];
      const choices = [];
      const reOpt = /-\s*([A-D])[\.\)]?\s*(.+)/g;
      let mo;
      while((mo=reOpt.exec(optsBlock)) !== null){
        choices.push({key: mo[1], text: mo[2].trim()});
      }
      q.push({id, prompt, choices});
    }
    return q;
  }

  async function loadAnswersForDeck(name){
    answersMap = {};
    const path = tsvFiles[name];
    if(!path) return answersMap;
    try{
      const res = await fetch(path);
      if(!res.ok) throw new Error('HTTP '+res.status);
      const txt = await res.text();
      const lines = txt.split(/\r?\n/).map(l=>l.trim()).filter(Boolean);
      for(const line of lines){
        const parts = line.split(/\tRéponse:\s*/);
        if(parts.length<2) continue;
        let qtext = parts[0].replace(/^Q\d+:\s*/,'').trim();
        let letter = parts[1].trim().charAt(0);
        answersMap[normalize(qtext)] = letter;
      }
    }catch(err){
      console.warn('Impossible de charger TSV', path, err);
    }
    return answersMap;
  }

  function renderQuestion(i){
    const it = questions[i];
    if(!it) return;
    progress.textContent = `Question ${i+1} / ${questions.length}`;
    questionArea.textContent = it.prompt;
    choicesArea.innerHTML = '';
    const name = 'choice';
    it.choices.forEach(ch => {
      const id = `c_${i}_${ch.key}`;
      const div = document.createElement('div'); div.className='choice';
      const input = document.createElement('input'); input.type='radio'; input.name = name; input.id=id; input.value = ch.key;
      if(userAnswers[i] === ch.key) input.checked = true;
      input.addEventListener('change', ()=>{ userAnswers[i]=ch.key; });
      const label = document.createElement('label'); label.htmlFor = id; label.textContent = `${ch.key}. ${ch.text}`;
      div.appendChild(input); div.appendChild(label); choicesArea.appendChild(div);
    });
  }

  prevBtn.addEventListener('click', ()=>{ if(currentIndex>0){ currentIndex--; renderQuestion(currentIndex); }});
  nextBtn.addEventListener('click', ()=>{ if(currentIndex < questions.length-1){ currentIndex++; renderQuestion(currentIndex); }});

  finishBtn.addEventListener('click', ()=>{
    let known=0, correct=0;
    for(let i=0;i<questions.length;i++){
      const q = questions[i];
      const key = normalize(q.prompt);
      const correctLetter = answersMap[key];
      const user = userAnswers[i];
      if(correctLetter){ known++; if(user && user === correctLetter) correct++; }
    }
    const pct = known? Math.round(100*correct/known) : 0;
    scoreDiv.innerHTML = `<p>Questions avec clé connue: ${known} / ${questions.length}</p><p>Réponses correctes: ${correct}</p><p>Taux: ${pct}%</p>`;
    result.classList.remove('hidden');
    player.classList.add('hidden');
    reviewDiv.innerHTML = '';
    for(let i=0;i<questions.length;i++){
      const q = questions[i];
      const key = normalize(q.prompt);
      const correctLetter = answersMap[key] || null;
      const user = userAnswers[i] || null;
      const entry = document.createElement('div'); entry.className='review-item';
      const h = document.createElement('div'); h.className='qtext'; h.textContent = `${i+1}) ${q.prompt}`;
      const info = document.createElement('div'); info.className='meta';
      info.innerHTML = `Votre réponse: <b>${user||'-'}</b> — Clé: <b>${correctLetter||'-'}</b>`;
      entry.appendChild(h); entry.appendChild(info);
      reviewDiv.appendChild(entry);
    }
  });

  revealBtn.addEventListener('click', ()=>{
    Array.from(reviewDiv.querySelectorAll('.review-item')).forEach((el)=>{
      const meta = el.querySelector('.meta').textContent || '';
      if(meta.includes('Clé: -')) el.classList.add('unknown');
    });
  });

  startBtn.addEventListener('click', async ()=>{
    const name = deckSelect.value;
    if(!name) return alert('Choisir un deck');
    questions = parseDeck(decks[name]);
    userAnswers = {};
    currentIndex = 0;
    await loadAnswersForDeck(name);
    player.classList.remove('hidden'); result.classList.add('hidden');
    renderQuestion(0);
  });

})();
