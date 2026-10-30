/* Line chart: history (solid) and forecast (dashed) */
function chart(c, hist, fc, histLabel) {
  const x = c.getContext('2d'), r = devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
  c.width = w * r; c.height = h * r; x.scale(r, r);
  const cs = getComputedStyle(document.documentElement), g = n => cs.getPropertyValue(n).trim();
  const A = g('--a'), B = g('--b'), M = g('--mut'), D = g('--bd');
  const all = [...hist, ...fc], mx = Math.max(...all) * 1.15 || 1, mn = Math.min(...all) * .85, p = 30, n = all.length;
  const X = i => p + i * (w - 2 * p) / (n - 1), Y = v => h - p - (v - mn) / (mx - mn || 1) * (h - 2 * p);
  x.font = '11px Inter,sans-serif'; x.fillStyle = M; x.strokeStyle = D;
  for (let i = 0; i <= 4; i++) { const y = p / 2 + i * (h - 1.5 * p) / 4; x.beginPath(); x.moveTo(p, y); x.lineTo(w - p, y); x.stroke(); }
  x.fillText(histLabel, p, h - 8); x.fillText('Next 7 days (forecast)', X(hist.length - 1) + 6, h - 8);
  const gr = x.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, A + '55'); gr.addColorStop(1, A + '00');
  x.beginPath(); hist.forEach((v, i) => i ? x.lineTo(X(i), Y(v)) : x.moveTo(X(i), Y(v)));
  x.strokeStyle = A; x.lineWidth = 2.5; x.stroke();
  x.lineTo(X(hist.length - 1), h - p); x.lineTo(X(0), h - p); x.fillStyle = gr; x.fill();
  const k = hist.length - 1;
  x.beginPath(); x.moveTo(X(k), Y(hist[k])); fc.forEach((v, i) => x.lineTo(X(k + 1 + i), Y(v)));
  x.strokeStyle = B; x.setLineDash([6, 5]); x.stroke(); x.setLineDash([]);
  x.beginPath(); x.arc(X(k), Y(hist[k]), 4, 0, 7); x.fillStyle = A; x.fill();
}
