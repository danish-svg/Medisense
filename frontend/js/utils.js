/* Shared helpers */
const $ = s => document.querySelector(s);
const dlg = $('#dlg');
const money = n => '₹' + Math.round(n).toLocaleString('en-IN');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const badge = s => `<span class="badge ${s}">${s}</span>`;
const pct = x => Math.round(x * 100) + '%';
const Views = {};   // each screen registers itself here

function toast(t, err) {
  const d = document.createElement('div');
  d.textContent = t; if (err) d.className = 'err';
  $('#toast').append(d); setTimeout(() => d.remove(), 3500);
}

/* Alert list with a "Why?" explanation for every alert */
function alertList(list) {
  const cls = {high: 'r', medium: 'y', info: 'b'};
  if (!list.length) return '<ul class="ins"><li>No issues detected.</li></ul>';
  return `<ul class="ins">${list.map(a => `<li class="${cls[a.severity]}"><b>${esc(a.medicine)}</b> ${esc(a.message)}
    <details><summary>Why?</summary><ul>${a.why.map(w => `<li style="background:none;border:0;padding:0">${esc(w)}</li>`).join('')}</ul></details></li>`).join('')}</ul>`;
}
