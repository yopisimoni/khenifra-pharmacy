import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const text = fs.readFileSync('index.html', 'utf8');
const scripts = [...text.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
assert.ok(scripts.length, 'Missing inline application JavaScript');
new vm.Script(scripts.at(-1)[1], { filename: 'index-inline.js' });

const tr = text.slice(text.indexOf('const tr = {'), text.indexOf('const extras = {'));
const extras = text.slice(text.indexOf('const extras = {'), text.indexOf('let lang ='));
for (const [name, block] of [['core', tr], ['legal', extras]]) {
  assert.ok(block && block.length, 'Translation object missing: ' + name);
  const ar = block.slice(block.indexOf('ar:{'), block.indexOf('fr:{'));
  const fr = block.slice(block.indexOf('fr:{'), block.indexOf('en:{'));
  const en = block.slice(block.indexOf('en:{'));
  const keys = str => [...str.matchAll(/(?:^|,)\s*([A-Za-z][A-Za-z0-9_]*):/g)].map(m => m[1]).filter(k => !['ar','fr','en'].includes(k));
  const expected = keys(ar);
  for (const [lang, value] of [['fr', fr], ['en', en]]) {
    assert.deepEqual(keys(value).sort(), expected.slice().sort(), name + ' translation mismatch: ' + lang);
  }
}
assert.ok(text.includes("timeZone:'Africa/Casablanca'"), 'Frontend must use Morocco local date');
assert.ok(text.includes("visibilitychange"), 'Returning from background must refresh duty');
assert.ok(!/AIza[0-9A-Za-z_-]{30,}/.test(text), 'Do not commit a Google browser API key');
const privacy = fs.readFileSync('privacy.html','utf8');
assert.ok(privacy.includes('id="policy"'), 'Privacy document must contain readable policy');
assert.ok(privacy.includes('langSelect.addEventListener'), 'Privacy language selector missing');
assert.ok(privacy.includes('Géolocalisation') && privacy.includes('معلومات الموقع') && privacy.includes('Location'), 'Privacy translations incomplete');
const privacyScript=[...privacy.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].at(-1);
assert.ok(privacyScript, 'Privacy page missing script');
new vm.Script(privacyScript[1], {filename:'privacy-inline.js'});
assert.ok(text.includes('href="/privacy.html"'), 'Footer must link to public privacy page');
assert.ok(text.includes("renderMap(); bindActions();"), 'Map controls must be rebound after rerender');
assert.ok(text.includes('${actionButtons(item)}${feedbackRow(item)}'), 'Night shift needs a report error action');
assert.ok(text.includes('${smallActions(p)}${feedbackRow(p)}'), 'Map entries need a report error action');
const shiftStart=text.indexOf('function casablancaHour(');
const shiftEnd=text.indexOf('function activeDutyPharmacies(',shiftStart);
assert.ok(shiftStart > 0 && shiftEnd > shiftStart,'Duty hours functions missing');
const shiftHelpers=vm.runInNewContext(text.slice(shiftStart,shiftEnd)+';({isNightHour,isNightShiftHours,casablancaHour})',{Intl,Date});
for(const [hour,night] of [[0,true],[8,true],[9,false],[20,false],[21,true],[23,true]]){
  assert.equal(shiftHelpers.isNightHour(hour),night,'Duty boundary at Casablanca local hour '+hour);
}
// Runtime date conversion is checked separately; do not assume every ICU build
// has identical future Morocco DST metadata when interpreting UTC instants.
for(const timestamp of ['2026-11-04T12:00:00Z','2026-11-04T22:00:00Z']){
  const instant=new Date(timestamp);
  const hour=shiftHelpers.casablancaHour(instant);
  assert.ok(Number.isInteger(hour) && hour>=0 && hour<=23,'Invalid Casablanca time');
  assert.equal(shiftHelpers.isNightShiftHours(instant),shiftHelpers.isNightHour(hour));
}
assert.ok(text.includes('const currentList = activeDutyPharmacies();'),'Map should show only active duty pharmacies');
assert.ok(text.includes('els.tabToday.hidden=nighttime'),'Day pharmacy tab must be hidden at night');
assert.ok(text.includes("if(tab==='today' && isNightShiftHours()) tab='night'"),'Night must not show daytime tab');
assert.ok(text.includes("lastDutyPeriod"),'Duty should refresh across shift changes');
const manifest=JSON.parse(fs.readFileSync('manifest.webmanifest','utf8'));
assert.equal(manifest.display,'standalone');
assert.equal(manifest.start_url,'/');
assert.ok(manifest.icons.some(i=>i.src==='/icons/icon-192.png' && i.sizes==='192x192'));
assert.ok(manifest.icons.some(i=>i.src==='/icons/icon-512.png' && i.sizes==='512x512'));
assert.ok(text.includes('rel="apple-touch-icon"'), 'iOS home screen icon missing');
assert.ok(fs.readFileSync('icons/pharmacy.svg','utf8').includes('<svg'));
const worker=fs.readFileSync('sw.js','utf8');
new vm.Script(worker,{filename:'sw.js'});
assert.ok(!worker.includes("cache.put(request"),'Never cache duty or map requests');
assert.ok(worker.includes("request.mode !== 'navigate'"),'Offline fallback applies only to navigations');
assert.ok(text.includes('rel="manifest"'), 'PWA manifest missing from HTML');
assert.ok(text.includes("serviceWorker.register('/sw.js')"),'Offline worker not registered');
assert.ok(fs.readFileSync('offline.html','utf8').includes('لا يمكن التأكد'), 'Offline warning must explain duty cannot be confirmed');
assert.ok(text.includes('class="owner-map-notice"'),'Owner map correction banner missing');
assert.ok(text.includes('updateOwnerMapNotice();'),'Owner map notice must update with language');
assert.ok(text.includes("simohamed.amara@gmail.com"),'Current contact email must be present');
for (const locale of ['ar:{text:', 'fr:{text:', 'en:{text:']) {
  assert.ok(text.includes(locale),'Owner map notice missing translation '+locale);
}
assert.ok(text.includes("link.href='mailto:'+email+'?subject='+encodeURIComponent(copy.subject)"),'Correction action should open email with localized subject');
// Navigation choices must only appear after an explicit start point is available.
assert.ok(text.includes('id="mapAppChooser" hidden'), 'Navigation apps shown before start point');
assert.ok(text.includes("if(!origin){clearNavigationChoices();"), 'Missing start point must prevent chooser');
assert.ok(text.includes("els.mapAppChooser.hidden=false;"), 'Navigation chooser should appear after origin');
assert.ok(text.includes('navigator.geolocation.getCurrentPosition(pos=>'), 'Location-on-demand action missing');
assert.ok(text.includes("els.startInput.addEventListener('input'"),'Manual start editing must reset stale options');
assert.ok(text.includes("phoneStatus(p)"), 'Missing phones must be clearly labeled');
assert.ok(text.includes("navigationMessage('search')") || text.includes("?'ready':'search'"),'Unverified pin warning missing');
const navStart=text.indexOf('function navUrls(');
const navEnd=text.indexOf('function reportMail(', navStart);
assert.ok(navStart>0 && navEnd>navStart, 'Nav functions missing');
const nav=vm.runInNewContext(text.slice(navStart,navEnd)+';navUrls',{pharmacyQuery:p=>[p.nameFr,p.address,'Khénifra, Morocco'].filter(Boolean).join(', ')});
const unknown={nameFr:'Pharmacie Exemple',address:'Khénifra',locationVerified:false};
const found=nav(unknown,'32.93,-5.66');
assert.ok(found.google.includes('/maps/search/'),'Unverified Google navigation must search');
assert.ok(found.waze.includes('waze.com/ul?q='),'Unverified Waze must search');
assert.ok(found.apple.includes('maps.apple.com/?q='),'Unverified Apple must search');
const confirmed={...unknown,locationVerified:true,lat:32.93,lng:-5.66};
const exact=nav(confirmed,'32.93,-5.65');
assert.ok(exact.google.includes('/maps/dir/')&&exact.google.includes('origin='),'Exact Google directions must include origin');
assert.ok(exact.waze.includes('ll='),'Verified Waze should use coordinates');
assert.ok(exact.apple.includes('daddr='),'Verified Apple directions must have destination');
assert.ok(text.includes('addressStatus(p)'), 'Missing pharmacy address must have a visible review label');
assert.ok(text.includes('phoneStatus(p)'), 'Missing pharmacy phone must have a visible review label');
assert.ok(text.includes('.owner-map-notice{display:flex') && text.includes('border:2px solid #c83737;border-radius:14px;background:#fff0f0'), 'Owner correction banner must be red');
assert.ok(!text.includes('.app > .banner{background:#fff0f0'), 'General schedule warning should retain its original color');
assert.ok(!text.includes('function candidatePhoneStatus(p){'), 'Do not display disputed candidate phone in public cards');
console.log('PASS: HTML JS, three-language key parity, privacy page, Morocco timezone, no embedded map key');
