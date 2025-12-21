const { firefox } = require('playwright');
const path = require('path');
(async ()=>{
  const fileUrl = 'file://' + path.resolve('web_qcm/offline_qcm.html');
  const browser = await firefox.launch();
  const page = await browser.newPage();
  try{
    await page.goto(fileUrl);
    await page.waitForSelector('#deckSelect');
    console.log('deckSelect exists');
    await page.selectOption('#deckSelect','Histologie_TC');
    await page.click('#loadBtn');
    await page.waitForTimeout(500);
    const status = await page.$eval('#status', el=>el.textContent);
    console.log('status->', status);
    const hidden = await page.$eval('#player', el=>el.classList.contains('hidden'));
    console.log('player hidden?', hidden);
  }catch(e){ console.error('ERR', e); }
  await browser.close();
})();
