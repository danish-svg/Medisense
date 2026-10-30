/* Thin wrapper around the backend API */
async function api(path, opt = {}) {
  const r = await fetch('/api' + path, {
    method: opt.method || 'GET',
    headers: {'Content-Type': 'application/json'},
    body: opt.body ? JSON.stringify(opt.body) : undefined
  });
  if (!r.ok) {
    let m = 'Request failed';
    try { const j = await r.json(); m = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail); } catch (e) {}
    throw new Error(m);
  }
  return r.status === 204 ? null : r.json();
}
