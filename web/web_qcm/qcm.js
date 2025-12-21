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
  const GENERATED_QUIZ_VALUE = '__generated_quiz__';
  const generatedQuizUrl = window.generatedQuizUrl || '../bank/quiz.json';

  {
    const opt = document.createElement('option');
    opt.value = GENERATED_QUIZ_VALUE;
    opt.textContent = 'Quiz (généré)';
    deckSelect.appendChild(opt);
  }

  Object.keys(decks).forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    deckSelect.appendChild(opt);
  });

  let questions = [];
  let answersMap = {};
  let userAnswers = {};
  let currentIndex = 0;

  function normalizeWhitespace(s){ return (s||'').replace(/\s+/g,' ').trim(); }

  function normalizeKey(s){
    s = (s || '').toLowerCase();
    try { s = s.normalize('NFKD'); } catch(e) {}
    s = s.replace(/[\u0300-\u036f]/g, '');
    s = s.replace(/[^a-z0-9]+/g, ' ');
    return normalizeWhitespace(s);
  }

  function parseAnswerLetters(raw){
    raw = (raw||'').toUpperCase().trim().replace(/\s+/g,'');
    if(!raw) return [];
    let parts;
    if(raw.includes(',') || raw.includes(';')){
      parts = raw.split(/[;,]/g).filter(Boolean);
    }else{
      parts = raw.split('');
    }
    const seen = new Set();
    const out = [];
    for(const p of parts){
      const x = p.trim();
      if(!x) continue;
      if(!seen.has(x)){
        seen.add(x);
        out.push(x);
      }
    }
    return out;
  }

  function parseDeck(md){
    const q = [];
    const re = /(?:^|\n)(\d+)\)\s*([^\n]+)\n([\s\S]*?)(?=(?:\n\d+\)|$))/gm;
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
        let ansPart = parts[1].trim();
        let lettersRaw = ansPart.split('—', 1)[0].trim();
        let letters = parseAnswerLetters(lettersRaw);
        if(!letters.length){
          // Back-compat: take first char
          const c = ansPart.charAt(0).toUpperCase();
          if(c) letters = [c];
        }
        answersMap[normalizeKey(qtext)] = letters;
      }
    }catch(err){
      console.warn('Impossible de charger TSV', path, err);
    }
    return answersMap;
  }

  async function loadGeneratedQuiz(){
    const res = await fetch(generatedQuizUrl);
    if(!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    if(!data || !Array.isArray(data.questions)) throw new Error('Format quiz.json invalide');
    return data.questions;
  }

  function toBankQuestionFromLegacy(q, correctLetters){
    const answer = (correctLetters && correctLetters.length) ? { answers: correctLetters } : null;
    return {
      id: q.id,
      type: 'single_choice',
      prompt: q.prompt,
      choices: q.choices,
      answer,
      tags: [],
      source: { kind: 'deck_md', ref: '' }
    };
  }

  function ensureChoicesForQuestion(it){
    if(Array.isArray(it.choices) && it.choices.length) return it.choices;
    if(it.type === 'true_false'){
      return [
        { key: 'V', text: 'Vrai' },
        { key: 'F', text: 'Faux' }
      ];
    }
    return [];
  }

  function renderMedia(media){
    if(!Array.isArray(media) || !media.length) return;
    for(const m of media){
      if(!m || m.kind !== 'image' || !m.src) continue;
      const figure = document.createElement('figure');
      const img = document.createElement('img');
      img.src = m.src;
      img.alt = m.alt || '';
      img.loading = 'lazy';
      figure.appendChild(img);
      if(m.caption){
        const cap = document.createElement('figcaption');
        cap.textContent = m.caption;
        figure.appendChild(cap);
      }
      questionArea.appendChild(figure);
    }
  }

  function getUserAnswerForIndex(i){
    return userAnswers[i];
  }

  function setUserAnswerForIndex(i, value){
    userAnswers[i] = value;
  }

  function toSet(arr){
    return new Set((arr||[]).map(String));
  }

  function equalAnswerSets(a, b){
    const sa = toSet(a);
    const sb = toSet(b);
    if(sa.size !== sb.size) return false;
    for(const x of sa) if(!sb.has(x)) return false;
    return true;
  }

  function renderQuestion(i){
    const it = questions[i];
    if(!it) return;
    progress.textContent = `Question ${i+1} / ${questions.length}`;

    questionArea.innerHTML = '';
    const promptDiv = document.createElement('div');
    promptDiv.textContent = it.prompt || '';
    questionArea.appendChild(promptDiv);
    renderMedia(it.media);

    choicesArea.innerHTML = '';

    const choices = ensureChoicesForQuestion(it);
    const isMulti = it.type === 'multiple_choice';
    const inputType = isMulti ? 'checkbox' : 'radio';
    const name = `choice_${i}`;
    const current = getUserAnswerForIndex(i);
    const currentSet = Array.isArray(current) ? toSet(current) : new Set([String(current||'')]);

    choices.forEach(ch => {
      const id = `c_${i}_${ch.key}`;
      const div = document.createElement('div');
      div.className='choice';
      const input = document.createElement('input');
      input.type = inputType;
      input.name = name;
      input.id = id;
      input.value = ch.key;
      input.checked = currentSet.has(String(ch.key));

      input.addEventListener('change', ()=>{
        if(isMulti){
          const next = toSet(Array.isArray(getUserAnswerForIndex(i)) ? getUserAnswerForIndex(i) : []);
          if(input.checked) next.add(ch.key); else next.delete(ch.key);
          setUserAnswerForIndex(i, Array.from(next));
        }else{
          setUserAnswerForIndex(i, ch.key);
        }
      });

      const label = document.createElement('label');
      label.htmlFor = id;
      label.textContent = `${ch.key}. ${ch.text}`;
      div.appendChild(input);
      div.appendChild(label);
      choicesArea.appendChild(div);
    });
  }

  prevBtn.addEventListener('click', ()=>{ if(currentIndex>0){ currentIndex--; renderQuestion(currentIndex); }});
  nextBtn.addEventListener('click', ()=>{ if(currentIndex < questions.length-1){ currentIndex++; renderQuestion(currentIndex); }});

  finishBtn.addEventListener('click', ()=>{
    let known=0, correct=0;
    for(let i=0;i<questions.length;i++){
      const q = questions[i];
      const correctAns = q && q.answer && Array.isArray(q.answer.answers) ? q.answer.answers : null;
      const user = userAnswers[i];
      if(correctAns && correctAns.length){
        known++;
        if(Array.isArray(user)){
          if(equalAnswerSets(user, correctAns)) correct++;
        }else{
          if(user && correctAns.length === 1 && String(user) === String(correctAns[0])) correct++;
        }
      }
    }
    const pct = known? Math.round(100*correct/known) : 0;
    scoreDiv.innerHTML = `<p>Questions avec clé connue: ${known} / ${questions.length}</p><p>Réponses correctes: ${correct}</p><p>Taux: ${pct}%</p>`;
    result.classList.remove('hidden');
    player.classList.add('hidden');
    reviewDiv.innerHTML = '';
    for(let i=0;i<questions.length;i++){
      const q = questions[i];
      const correctLetters = q && q.answer && Array.isArray(q.answer.answers) ? q.answer.answers : null;
      const user = (userAnswers[i] !== undefined) ? userAnswers[i] : null;
      const entry = document.createElement('div'); entry.className='review-item';
      const h = document.createElement('div'); h.className='qtext'; h.textContent = `${i+1}) ${q.prompt}`;
      const info = document.createElement('div'); info.className='meta';
      const userTxt = Array.isArray(user) ? user.join(',') : (user||'-');
      const keyTxt = (correctLetters && correctLetters.length) ? correctLetters.join(',') : '-';
      info.innerHTML = `Votre réponse: <b>${userTxt}</b> — Clé: <b>${keyTxt}</b>`;
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
    userAnswers = {};
    currentIndex = 0;

    try{
      if(name === GENERATED_QUIZ_VALUE){
        questions = await loadGeneratedQuiz();
      }else{
        const legacy = parseDeck(decks[name] || '');
        await loadAnswersForDeck(name);
        questions = legacy.map(q => {
          const correctLetters = answersMap[normalizeKey(q.prompt)] || null;
          return toBankQuestionFromLegacy(q, correctLetters);
        });
      }
    }catch(err){
      console.warn('Erreur chargement quiz/deck', err);
      return alert('Impossible de charger le quiz. Utilisez un serveur local (RUN.md).');
    }

    player.classList.remove('hidden');
    result.classList.add('hidden');
    renderQuestion(0);
  });

})();
