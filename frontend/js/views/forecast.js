Views.fc = {
  title: 'Demand forecast', id: null,
  async render() {
    const list = await api('/medicines');
    if (!this.id || !list.some(m => m.id === this.id)) this.id = list[0].id;
    const f = this.f = await api(`/medicines/${this.id}/forecast`), m = f.medicine, b = f.bayes, e = f.evidence;
    const bar = (l, v) => `<div class="bar"><span>${l}</span><div class="cap ${v > .5 ? 'Critical' : v > .25 ? 'Low' : ''}"><span style="width:${v * 100}%"></span></div><span class="mut">${pct(v)}</span></div>`;
    const st = (a, b2) => `<div class="stat"><span class="mut">${a}</span><b>${b2}</b></div>`;
    return `<div class="tools"><select onchange="Views.fc.id=+this.value;go('fc')">${list.map(x => `<option value="${x.id}" ${x.id === m.id ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select></div>
    <div class="grid two"><div class="card"><h3>${esc(m.name)}: demand forecast</h3><canvas id="cv"></canvas></div>
      <div class="card"><h3>Model output</h3>
        ${st('Demand pattern', badge(m.pattern) + ' ' + pct(m.pattern_degree) + ' regular')}
        ${st('Criticality', badge(m.criticality))}
        ${st('Next 7 days', m.forecast_7d + ' units')}
        ${st('Trend', (m.trend > 1 ? '+' : '') + Math.round((m.trend - 1) * 100) + '% week over week')}
        ${st('Safety stock', m.safety_stock)}${st('Minimum stock', m.min_stock)}${st('Reorder point', m.reorder_point)}${st('Confidence', m.confidence + '%')}
        <div class="note">${esc(m.pattern_rule)}</div></div></div>
    <div class="grid two" style="margin-top:16px">
      <div class="card"><h3>Shortage and waste risk</h3>
        ${bar('Demand rising', b.demand_up)}${bar('Supplier delay', b.supplier_delay)}${bar('<b>Stock-out risk</b>', b.stockout)}
        ${bar('Near expiry', b.near_expiry)}${bar('Slow sales', b.low_sales)}${bar('<b>Waste risk</b>', b.waste)}
        <div class="note">Stock-out risk is <b>${b.stockout_level}</b> and waste risk is <b>${b.waste_level}</b>. Stock-out depends on demand and supplier delay; waste depends on expiry and slow sales.</div></div>
      <div class="card"><h3>Demand signals</h3>
        ${st('Sales trend says', `rising ${pct(e.trend.R)} · falling ${pct(e.trend.F)}`)}
        ${st('Season (' + esc(e.season_label) + ')', `rising ${pct(e.season.R)} · falling ${pct(e.season.F)}`)}
        ${st('Conflict between sources', pct(e.conflict))}
        ${st('Rising: belief to plausibility', pct(e.belief_rising) + ' to ' + pct(e.plausibility_rising))}
        <div class="note"><b>${e.decision === 'conflict' ? 'Conflicting evidence. ' : ''}</b>${esc(e.advice)}</div></div></div>`;
  },
  after() { chart($('#cv'), this.f.medicine.history, this.f.medicine.forecast, 'Last 28 days'); }
};
