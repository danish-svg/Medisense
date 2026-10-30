Views.inv = {
  title: 'Inventory', rows: [], sortK: 'name', sortD: 1,
  async render() {
    this.rows = await api('/medicines');
    const cats = [...new Set(this.rows.map(r => r.category))].sort();
    return `<div class="tools"><input id="q" placeholder="Search medicine" oninput="Views.inv.draw()">
      <select id="cf" onchange="Views.inv.draw()"><option>All</option>${cats.map(c => `<option>${esc(c)}</option>`).join('')}</select>
      <span class="grow"></span><button class="btn" onclick="$('#csvf').click()">Import sales CSV</button><button class="btn" onclick="Views.inv.csv()">Export CSV</button><button class="btn" onclick="openSell()">Record sale</button><button class="btn p" onclick="openAdd()">Add medicine</button></div>
      <div class="card tw" id="tbl"></div>`;
  },
  after() { this.draw(); },
  sort(k) { this.sortD = this.sortK === k ? -this.sortD : 1; this.sortK = k; this.draw(); },
  draw() {
    const q = $('#q').value.toLowerCase(), c = $('#cf').value, k = this.sortK;
    const L = this.rows.filter(r => r.name.toLowerCase().includes(q) && (c === 'All' || r.category === c))
      .sort((a, b) => (a[k] > b[k] ? 1 : -1) * this.sortD);
    const th = (t, key) => `<th class="s" onclick="Views.inv.sort('${key}')">${t}</th>`;
    $('#tbl').innerHTML = `<table><tr>${th('Medicine', 'name')}<th>Category</th><th>Criticality</th><th>Demand</th>${th('Stock', 'stock')}<th>Sold today</th><th>Level</th>${th('Days of cover', 'days_cover')}<th>Min stock</th>${th('Expiry (days)', 'expiry_days')}<th>Status</th><th></th></tr>
      ${L.map(r => `<tr><td><b>${esc(r.name)}</b><br><small class="mut">${esc(r.supplier)}</small></td><td>${esc(r.category)}</td>
        <td>${badge(r.criticality)}</td><td>${badge(r.pattern)}</td><td>${r.stock}</td><td>${r.sold_today}</td>
        <td><div class="cap ${r.status}"><span style="width:${Math.min(100, Math.round(r.stock / (r.reorder_point * 2) * 100))}%"></span></div></td>
        <td>${r.days_cover}</td><td>${r.min_stock}</td><td>${r.expiry_days}</td><td>${badge(r.status)}</td>
        <td style="white-space:nowrap"><button class="btn sm" onclick="openSell(${r.id})">Sell</button> <button class="btn sm" onclick="Views.inv.add(${r.id})">+50</button>
        ${['Critical', 'Low', 'Expired'].includes(r.status) ? `<button class="btn sm" onclick="openSubs(${r.id})">Substitutes</button>` : ''}
        <button class="btn sm" onclick="Views.inv.del(${r.id})">Remove</button></td></tr>`).join('')
        || '<tr><td colspan="12">No medicines match. Clear the search or add a new medicine.</td></tr>'}</table>`;
  },
  async add(id) { try { await api(`/medicines/${id}/stock`, {method: 'PATCH', body: {delta: 50}}); toast('Added 50 units'); go('inv'); } catch (e) { toast(e.message, 1); } },
  async del(id) { if (!confirm('Remove this medicine?')) return; try { await api('/medicines/' + id, {method: 'DELETE'}); toast('Medicine removed'); go('inv'); } catch (e) { toast(e.message, 1); } },
  csv() {
    const r = [['Medicine', 'Category', 'Criticality', 'Stock', 'Price', 'ExpiryDays', 'Status']].concat(this.rows.map(m => [m.name, m.category, m.criticality, m.stock, m.unit_price, m.expiry_days, m.status]));
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([r.join('\n')], {type: 'text/csv'})); a.download = 'inventory.csv'; a.click();
  }
};
