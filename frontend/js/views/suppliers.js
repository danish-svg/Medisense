Views.sup = {
  title: 'Suppliers',
  async render() {
    const L = await api('/suppliers');
    return `<div class="grid cards">${L.map((s, i) => `<div class="card"><div class="row"><h3>${esc(s.name)}</h3>${i === 0 ? '<span class="badge Healthy">Top supplier</span>' : ''}</div>
      <p class="mut">Delivery ${s.lead_time_days} days · On-time ${s.reliability_pct}% · Minimum order ${money(s.min_order_value)} · ${s.medicines} medicines</p>
      <p style="margin:12px 0 6px">Score <b>${s.score}</b>/100</p><div class="cap"><span style="width:${Math.min(100, s.score)}%"></span></div></div>`).join('')}</div>`;
  }
};
