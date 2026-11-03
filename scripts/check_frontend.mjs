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
console.log('PASS: HTML JS, three-language key parity, privacy page, Morocco timezone, no embedded map key');
