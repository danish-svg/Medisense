Views.dash = {
  title: 'Dashboard',
  async render() {
    const d = this.d = await api('/dashboard'), k = d.kpis, mx = Math.max(...Object.values(d.categories), 1);
    return `<div class="brief"><div class="pulse"></div>
      <h1>${k.at_risk} medicines may run out before restock, and <em>${money(k.waste_risk)}</em> of stock is at risk of expiring unsold.</h1>
      <p>Today’s brief, based on 28 days of sales, supplier lead times and batch expiry dates.</p></div>
    <div class="grid k">
      <div class="card kpi"><small>Medicines tracked</small><div class="v">${k.tracked}</div></div>
      <div class="card kpi"><small>Stock value</small><div class="v">${money(k.stock_value)}</div></div>
      <div class="card kpi bad"><small>Need reorder</small><div class="v">${k.need_reorder}</div></div>
      <div class="card kpi warn"><small>Expiring in 30 days</small><div class="v">${k.expiring_30}</div></div>
      <div class="card kpi"><small>Avg. forecast confidence</small><div class="v">${k.confidence}%</div></div></div>
    <div class="grid two">
      <div class="card"><h3>Total demand: history and 7-day forecast</h3><canvas id="cv"></canvas></div>
      <div class="card"><h3>Stock value by category</h3>${Object.entries(d.categories).map(([c, v]) =>
        `<div class="bar"><span>${esc(c)}</span><div class="cap"><span style="width:${v / mx * 100}%"></span></div><span class="mut">${money(v / 1000)}k</span></div>`).join('')}</div></div>
    <div class="card" style="margin-top:16px"><h3>Top alerts</h3>${alertList(d.alerts)}</div>`;
  },
  after() { chart($('#cv'), this.d.history, this.d.forecast, 'Last 28 days'); }
};
