const { chromium } = require('playwright');
const path = require('path');
(async ()=>{
  const fileUrl = 'file://' + path.resolve('web_qcm/offline_qcm.html');
  let browser;
  try{
    try{ browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] }); }
    catch(e){
      console.error('chromium.launch failed, trying system Chrome:', e.message||e);
      browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--no-sandbox'] });
    }
    const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
    await page.goto(fileUrl, { waitUntil: 'load' });
    const decks = ['Histologie_TC','Angiologie','Myologie','Plexus_Nerfs','Securite_IFEC'];
    const report = [];
    for(const deck of decks){
      await page.selectOption('#deckSelect', deck);
      await page.click('#loadBtn');
      await page.waitForTimeout(200);
      const qcount = await page.evaluate(()=> (typeof state !== 'undefined' && state.questions) ? state.questions.length : 0);
      const missing = await page.evaluate(()=>{
        const out = {missingCount:0, examples:[]};
        for(let i=0;i<state.questions.length;i++){
          const q=state.questions[i];
          const num = parseInt(q.num,10);
          const mapped = state.answersNumMap && state.answersNumMap.get(num);
          if(!mapped){ out.missingCount++; if(out.examples.length<6) out.examples.push({num:q.num, text:q.text}); }
        }
        return out;
      });
      report.push({deck, totalQuestions:qcount, missing: missing.missingCount, examples: missing.examples});
      // reset
      await page.click('#resetBtn');
      await page.waitForTimeout(100);
    }
    console.log('E2E Chromium report:\n', JSON.stringify(report,null,2));
  }catch(e){ console.error('E2E error', e); }
  finally{ if(browser) await browser.close(); }
})();
