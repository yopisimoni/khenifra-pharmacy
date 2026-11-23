/* Privacy-first GA4: replace GA4_ID after creating your GA4 web stream.
   No analytics requests occur without a valid ID and affirmative consent. */
(() => {
  'use strict';
  const GA4_ID = ''; // Set to your public GA4 Measurement ID, e.g. G-XXXXXXXXXX
  if (!/^G-[A-Z0-9]{6,15}$/.test(GA4_ID)) return;
  const consentKey = 'khenifra-analytics-consent-v1';
  const params = new URLSearchParams(location.search);
  const qr = params.get('src') === 'qr-share' || params.get('utm_source') === 'qr';
  const locale = (document.documentElement.lang || 'ar').slice(0, 2);
  const msg = locale === 'fr'
    ? ['Acceptez-vous des statistiques de visite anonymisées ?', 'Accepter', 'Refuser']
    : locale === 'en'
      ? ['Allow optional visitor analytics?', 'Allow', 'Decline']
      : ['هل توافق على إحصاءات الزيارات الاختيارية؟', 'موافق', 'لا أوافق'];
  const start = () => {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA4_ID, { send_page_view: true, anonymize_ip: true });
    if (qr) window.gtag('event', 'qr_visit', { source: 'qr-share' });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_ID);
    document.head.appendChild(tag);
  };
  try {
    const existing = localStorage.getItem(consentKey);
    if (existing === 'yes') { start(); return; }
    if (existing === 'no') return;
  } catch (_) { return; }
  const banner = document.createElement('aside');
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', msg[0]);
  banner.style.cssText = 'position:fixed;bottom:12px;left:12px;right:12px;z-index:9999;max-width:520px;margin:auto;background:#fff;color:#18332d;border:1px solid #d8e6df;border-radius:14px;box-shadow:0 8px 28px #0002;padding:15px;font:14px system-ui';
  const label = document.createElement('p');
  label.textContent = msg[0];
  const buttons = document.createElement('div');
  buttons.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap';
  [true, false].forEach((allowed, i) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = msg[i + 1];
    button.style.cssText = 'min-height:44px;padding:8px 14px;border-radius:9px;border:1px solid #0d5948;background:' + (allowed ? '#0d5948;color:white' : '#fff;color:#0d5948');
    button.addEventListener('click', () => {
      try { localStorage.setItem(consentKey, allowed ? 'yes' : 'no'); } catch (_) {}
      banner.remove();
      if (allowed) start();
    });
    buttons.appendChild(button);
  });
  banner.append(label, buttons);
  document.body.appendChild(banner);
})();
