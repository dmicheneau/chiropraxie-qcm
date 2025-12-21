const { chromium } = require('playwright');
const path = require('path');
(async ()=>{
  const fileUrl = 'file://' + path.resolve('web_qcm/offline_qcm.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const decks = ['Histologie_TC','Angiologie','Myologie','Plexus_Nerfs','Securite_IFEC'];
  const results = [];
  try{
    await page.goto(fileUrl);
    for(const deck of decks){
      const res = {deck, loaded:false, questionCount:0, choicesFound:false, submitEnabled:false, showAnswersEnabled:false};
      await page.selectOption('#deckSelect', deck);
      await page.click('#loadBtn');
      // wait for status text to include chargé
      await page.waitForFunction((d)=> document.getElementById('status').textContent.includes(d) , {}, deck);
      res.loaded = true;
      const qcount = await page.evaluate(()=> state.questions.length);
      res.questionCount = qcount;
      // ensure first question has choices
      await page.waitForSelector('#choices .choice');
      const choices = await page.$$('#choices .choice');
      res.choicesFound = choices.length >= 1;
      // click first available radio
      if(choices.length){
        const input = await choices[0].$('input[type=radio]');
        if(input) await input.check();
      }
      // check submit enabled
      res.submitEnabled = await page.$eval('#submitBtn', b => !b.disabled);
      // click submit and read result
      if(res.submitEnabled){
        await page.click('#submitBtn');
        await page.waitForTimeout(200);
      }
      // check showAnswers enabled (only after all answered)
      res.showAnswersEnabled = await page.$eval('#showAnswersBtn', b => !b.disabled);
      // store result
      results.push(res);
      // reset
      await page.click('#resetBtn');
      await page.waitForTimeout(100);
    }
  }catch(e){
    console.error('Test error', e);
  } finally{
    console.log('RESULTS:\n', JSON.stringify(results, null, 2));
    await browser.close();
    process.exit(0);
  }
})();
