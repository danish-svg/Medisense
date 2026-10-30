Views.exp = {
  title: 'Expiry planner',
  async render() {
    const L = await api('/expiry');
    if (!L.length) return '<div class="card">No medicines are at risk of expiring unsold.</div>';
    return `<div class="grid cards">${L.map(x => { const p = x.plan; return `<div class="card">
      <div class="row"><h3>${esc(x.name)}</h3><span class="badge ${x.expiry_days <= 0 ? 'Expired' : x.expiry_days <= 30 ? 'Critical' : 'Expiring'}">${x.expiry_days <= 0 ? 'Expired' : x.expiry_days + ' days'}</span></div>
      <p class="mut">${x.units} units ${x.expiry_days <= 0 ? 'expired' : 'likely unsold'} · worth ${money(p.value)}</p>
      <p style="margin:12px 0 4px"><b>Recommended: ${esc(p.action)}</b></p>
      <ul style="margin-left:18px;line-height:1.6">${p.plan.map(s => `<li>${esc(s.step)} <span class="mut">(${money(s.cost)})</span></li>`).join('')}</ul>
      <p style="margin-top:8px">Expected loss <b>${money(p.expected_loss)}</b> instead of ${money(p.value)}</p>
      ${p.options.length ? `<details><summary>Compare options</summary><ul>${p.options.map(o => `<li>${esc(o.name)}: ${money(o.cost)} ${o.chosen ? '(chosen)' : ''}</li>`).join('')}</ul></details>` : ''}
      </div>`; }).join('')}</div>`;
  }
};
