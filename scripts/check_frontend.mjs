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
const shiftHelpers=vm.runInNewContext(text.slice(shiftStart,shiftEnd)+';({isNightShiftHours})',{Intl,Date});
for(const [timestamp,night] of [
 ['2026-11-04T07:59:00Z',true],  // 08:59 Morocco
 ['2026-11-04T08:00:00Z',false], // 09:00 Morocco
 ['2026-11-04T19:59:00Z',false],// 20:59 Morocco
 ['2026-11-04T20:00:00Z',true], // 21:00 Morocco
 ['2026-11-04T23:15:00Z',true], // after midnight Morocco
]) assert.equal(shiftHelpers.isNightShiftHours(new Date(timestamp)),night,'Duty boundary '+timestamp);
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
console.log('PASS: HTML JS, three-language key parity, privacy page, Morocco timezone, no embedded map key');
