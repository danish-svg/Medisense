Views.alerts = {
  title: 'Alerts',
  async render() {
    const list = await api('/alerts');
    return `<div class="card"><h3>${list.length} alerts</h3>${alertList(list)}</div>`;
  }
};
