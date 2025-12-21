const { chromium } = require('playwright');
const path = require('path');
(async ()=>{
  const fileUrl = 'file://' + path.resolve('web_qcm/offline_qcm.html');
  let browser;
  try{
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  }catch(err){
    console.error('Initial chromium.launch failed:', err.message || err);
    // try launching system Chrome as fallback
    const systemChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    try{
      console.log('Attempting fallback executablePath:', systemChrome);
      browser = await chromium.launch({ headless: true, executablePath: systemChrome, args: ['--no-sandbox'] });
    }catch(err2){
      console.error('Fallback launch failed:', err2.message || err2);
      throw err2;
    }
  }
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });

  page.on('console', msg => console.log('PAGE console:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGE error:', err.toString()));
  page.on('requestfailed', req => console.log('REQUEST failed:', req.url(), req.failure() && req.failure().errorText));
  page.on('framenavigated', frame => console.log('Frame navigated to', frame.url()));

  try{
    console.log('Opening', fileUrl);
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.waitForSelector('#deckSelect');
    console.log('Selecting Histologie_TC');
    await page.selectOption('#deckSelect','Histologie_TC');
    console.log('Click loadBtn');
    await page.click('#loadBtn');
    // observe navigation events for 1s
    await page.waitForTimeout(1000);
    const status = await page.$eval('#status', el=>el.textContent);
    console.log('status:', status);
    const resultHtml = await page.$eval('#result', el=>el.innerText);
    console.log('result area:', resultHtml);
    // dump first 6 questions + match result for debugging
    const qcount = await page.evaluate(()=> (typeof state !== 'undefined' && state.questions) ? state.questions.length : 0);
    console.log('question count in state:', qcount);
    for(let i=0;i<6 && i<qcount;i++){
      const q = await page.evaluate((i)=> state.questions[i], i);
      const key = await page.evaluate((i)=> { const q=state.questions[i]; return (state.answersNumMap && state.answersNumMap.get(parseInt(q.num,10))) || null; }, i);
      console.log(`Q${q.num}:`, (q.text||'').slice(0,120), '=> mapped letter:', key);
    }
    // For the first question, compute top candidate matches from answersTextMap
    const topMatches = await page.evaluate(()=>{
      const i=0; const q = state.questions[i]; const qtokens = tokensOf(q.text);
      const scores = [];
      for(const [k,v] of state.answersTextMap){
        const ktoks = Array.from(k.split(/\s+/).filter(Boolean));
        let common=0;
        for(const qt of qtokens){
          for(const kt of ktoks){
            if(qt === kt){ common++; break; }
            if(qt.startsWith(kt) || kt.startsWith(qt)){ common++; break; }
            if(qt.length>4 && (qt.includes(kt) || kt.includes(qt))){ common++; break; }
          }
        }
        const denom = Math.min(qtokens.length, ktoks.length) || 1; const score = common/denom;
        scores.push({k,kdisplay:k.slice(0,140), v, score});
      }
      scores.sort((a,b)=>b.score-a.score);
      return scores.slice(0,8);
    });
    console.log('Top matches for Q1:', JSON.stringify(topMatches,null,2));
  }catch(e){
    console.error('ERROR running debug:', e);
  } finally{
    await browser.close();
  }
})();
