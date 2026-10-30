Views.plan = {
  title: 'Reorder planner', plan: null,
  async render() {
    const [s, orders] = await Promise.all([api('/settings'), api('/orders')]);
    const pend = orders.filter(o => o.status === 'pending');
    return `<div class="card"><h3>Plan this week’s orders</h3>
      <p class="mut" style="margin-bottom:12px">Chooses order quantities for all medicines that need restocking, within your budget, shelf space and each supplier’s minimum order.</p>
      <div class="tools"><label>Budget (₹) <input id="bd" type="number" min="1" value="${s.budget}"></label>
      <label>Shelf space limit <input id="st" type="number" min="1" value="${s.storage_limit}"></label>
      <button class="btn p" onclick="Views.plan.generate()">Generate plan</button></div></div>
      <div id="res" style="margin-top:16px"></div>
      <div class="card tw" style="margin-top:16px"><h3>Purchase orders</h3><table><tr><th>No.</th><th>Medicine</th><th>Qty</th><th>Supplier</th><th>Cost</th><th>Status</th><th></th></tr>
      ${orders.map(o => `<tr><td>PO-${o.id}</td><td>${esc(o.medicine)}</td><td>${o.quantity}</td><td>${esc(o.supplier)}</td><td>${money(o.cost)}</td><td>${o.status}</td>
        <td>${o.status === 'pending' ? `<button class="btn sm" onclick="Views.plan.recv(${o.id})">Mark received</button>` : ''}</td></tr>`).join('') || '<tr><td colspan="7">No purchase orders yet.</td></tr>'}</table>
      ${pend.length ? '' : ''}</div>`;
  },
  async generate() {
    try {
      const body = {budget: +$('#bd').value, storage_limit: +$('#st').value};
      await api('/settings', {method: 'PUT', body});
      const p = this.plan = await api('/planner/reorder', {method: 'POST', body});
      const L = p.lines.filter(l => l.quantity > 0);
      $('#res').innerHTML = `<div class="grid k">
        <div class="card kpi"><small>Budget used</small><div class="v">${money(p.spent)}</div><small>of ${money(p.budget)}</small></div>
        <div class="card kpi"><small>Shelf space used</small><div class="v">${p.space_used}</div><small>${p.space_free} free</small></div>
        <div class="card kpi"><small>Medicines ordered</small><div class="v">${L.length}</div><small>of ${p.lines.length} needing stock</small></div>
        <div class="card kpi"><small>Search</small><div class="v">${p.optimal ? 'Best' : 'Good'}</div><small>${p.nodes.toLocaleString()} options checked</small></div></div>
      <div class="card tw"><div class="row"><h3>Suggested orders</h3><button class="btn p" ${L.length ? '' : 'disabled'} onclick="Views.plan.approve()">Approve plan</button></div>
      <table><tr><th>Medicine</th><th>Criticality</th><th>Status</th><th>Order</th><th>Full need</th><th>Cost</th><th>Supplier</th><th>Why</th></tr>
      ${p.lines.map(l => `<tr><td><b>${esc(l.name)}</b></td><td>${badge(l.criticality)}</td><td>${badge(l.status)}</td><td><b>${l.quantity}</b></td><td>${l.full_quantity}</td><td>${money(l.cost)}</td><td>${esc(l.supplier)}</td><td class="mut">${esc(l.reason)}</td></tr>`).join('')}</table>
      <div class="note"><b>Supplier minimum orders: </b>${p.suppliers.map(s => `${esc(s.name)} ${money(s.total)} (min ${money(s.minimum)}) ${s.met ? '✓' : '✗'}`).join(' · ') || 'No orders placed.'}</div></div>`;
    } catch (e) { toast(e.message, 1); }
  },
  async approve() {
    try {
      await api('/orders', {method: 'POST', body: {lines: this.plan.lines.filter(l => l.quantity > 0).map(l => ({medicine_id: l.medicine_id, quantity: l.quantity}))}});
      toast('Orders approved'); go('plan');
    } catch (e) { toast(e.message, 1); }
  },
  async recv(id) { try { await api(`/orders/${id}/receive`, {method: 'POST'}); toast('Stock received'); go('plan'); } catch (e) { toast(e.message, 1); } }
};
