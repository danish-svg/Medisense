/* Router, navigation, theme and dialogs */
const NAV = {dash: 'Dashboard', alerts: 'Alerts', inv: 'Inventory', fc: 'Demand forecast', plan: 'Reorder planner', exp: 'Expiry planner', sup: 'Suppliers'};
let current = 'dash';

async function go(v) {
  current = v; const V = Views[v];
  $('#title').textContent = V.title;
  document.querySelectorAll('.nb').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  try {
    $('#main').innerHTML = await V.render();
    if (V.after) V.after();
  } catch (e) { $('#main').innerHTML = `<div class="card">Could not load this page: ${esc(e.message)}</div>`; }
  api('/alerts').then(a => $('#bell b').textContent = a.filter(x => x.severity !== 'info').length).catch(() => {});
}

async function openAdd() {
  const sups = await api('/suppliers');
  $('#usel').innerHTML = sups.map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join('');
  dlg.showModal();
}

async function openSubs(id) {
  const d = await api(`/medicines/${id}/substitutes`), s = $('#sub');
  s.innerHTML = `<h3>Substitutes for ${esc(d.for)}</h3><p class="mut" style="margin:6px 0 12px">Category: ${esc(d.category)}</p>
    ${d.options.map(o => `<div class="note"><b>${esc(o.name)}</b> · ${o.stock} in stock · expires in ${o.expiry_days} days · ${money(o.unit_price)} each
      <br><small class="mut">${esc(o.path)}</small></div>`).join('') || '<div class="note">No suitable substitute is currently in stock.</div>'}
    <div class="note"><b>${esc(d.note)}</b></div>
    <div class="row" style="margin-top:16px;justify-content:flex-end"><button class="btn" onclick="$('#sub').close()">Close</button></div>`;
  s.showModal();
}

async function openSell(id) {
  const L = (await api('/medicines')).filter(m => m.stock > 0 && m.expiry_days > 0);
  if (!L.length) return toast('No medicines available to sell', 1);
  $('#ssel').innerHTML = L.map(m => `<option value="${m.id}" ${m.id === id ? 'selected' : ''}>${esc(m.name)} (${m.stock} in stock)</option>`).join('');
  $('#sell').showModal();
}
$('#sfrm').onsubmit = async e => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  try {
    const r = await api('/sales', {method: 'POST', body: {medicine_id: +f.medicine_id, quantity: +f.quantity}});
    $('#sell').close(); toast(`Sale recorded. ${r.stock} units left`); go(current);
  } catch (er) { toast(er.message, 1); }
};
/* CSV import: each line is "medicine name,quantity" (a header line is ignored) */
$('#csvf').onchange = async e => {
  const file = e.target.files[0]; e.target.value = '';
  if (!file) return;
  const lines = (await file.text()).split(/\r?\n/).map(l => l.trim()).filter(Boolean).map(l => {
    const i = l.lastIndexOf(',');
    return {medicine: l.slice(0, i).replace(/^"|"$/g, '').trim(), quantity: +l.slice(i + 1)};
  }).filter(l => l.quantity > 0);
  if (!lines.length) return toast('No valid lines found. Use: medicine name,quantity', 1);
  try { const r = await api('/sales/bulk', {method: 'POST', body: {lines}}); toast(`Imported ${r.lines} sales lines`); go(current); }
  catch (er) { toast(er.message, 1); }
};

const navHtml = Object.entries(NAV).map(([k, t]) => `<button class="nb" data-v="${k}" onclick="go('${k}')">${t}</button>`).join('');
$('#nav').innerHTML = navHtml;
$('#mnav').innerHTML = navHtml.replace(/class="nb"/g, 'class="nb btn"');
$('#bell').onclick = () => go('alerts');
$('#frm').onsubmit = async e => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  ['stock', 'unit_price', 'expiry_days', 'avg_daily_sales', 'storage_units', 'supplier_id'].forEach(k => f[k] = +f[k]);
  try { await api('/medicines', {method: 'POST', body: f}); dlg.close(); toast(f.name + ' added'); go('inv'); } catch (er) { toast(er.message, 1); }
};
function setTheme(t) { document.documentElement.dataset.t = t; $('#theme').textContent = t === 'dark' ? 'Light mode' : 'Dark mode'; try { localStorage.setItem('theme', t); } catch (e) {} }
$('#theme').onclick = () => { setTheme(document.documentElement.dataset.t === 'dark' ? 'light' : 'dark'); go(current); };
try { setTheme(localStorage.getItem('theme') || 'light'); } catch (e) {}
addEventListener('resize', () => { if ($('#cv')) go(current); });
go('dash');
