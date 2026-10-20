// Журнал событий демо-записи + видимый курсор с «кругами» клика.
//
// Внедряется в контекст записи ДО создания страницы:
//   await ctx.addInitScript({ content: <текст этого файла> });
// События хранятся в sessionStorage (переживают переходы внутри origin).
//
// Ключевые моменты агент отмечает сам — в момент, когда они видны на экране:
//   await page.evaluate(() => window.__demo.mark('send', 'textarea'));
//   await page.evaluate(() => window.__demo.mark('result_open', '[role=dialog]', { note: 'реестр xlsx' }));
// target — CSS-селектор или null; его рамка (box) нужна auto_edit.py для зума.
// Клики пишутся автоматически (type = 'click').
//
// Выгрузка в конце записи:
//   const events = await page.evaluate(() => window.__demo.events());
// и сохранить в events.json вместе с video_start_ms (см. DEMO-VIDEO.md §3).
//
// Курсор двигается только по событиям мыши: перед кликом вести мышь плавно —
//   await page.mouse.move(x, y, { steps: 25 });
(() => {
  if (window.__demo) return;
  const KEY = '__demo_events';

  const load = () => {
    try { return JSON.parse(sessionStorage.getItem(KEY) || '[]'); } catch (e) { return []; }
  };
  const save = (ev) => {
    const all = load();
    all.push(ev);
    try { sessionStorage.setItem(KEY, JSON.stringify(all)); } catch (e) { /* квота — пропустить */ }
  };
  const box = (el) => {
    if (!el || !el.getBoundingClientRect) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height, vw: innerWidth, vh: innerHeight };
  };
  const log = (type, el, extra) => save(Object.assign({ type, ts: Date.now(), box: box(el) }, extra || {}));

  window.__demo = {
    mark: (type, target, extra) =>
      log(type, typeof target === 'string' ? document.querySelector(target) : target, extra),
    events: load,
    clear: () => sessionStorage.removeItem(KEY),
  };

  addEventListener('click', (e) => {
    const el = e.target.closest
      ? e.target.closest('button,a,[role=button],[role=menuitem],[role=tab],input,textarea') || e.target
      : e.target;
    log('click', el, { text: (el.innerText || el.value || '').trim().slice(0, 60) });
  }, true);

  const install = () => {
    if (document.getElementById('__demo_cursor')) return;
    const st = document.createElement('style');
    st.textContent = [
      '#__demo_cursor{position:fixed;left:-50px;top:-50px;width:20px;height:20px;margin:-10px 0 0 -10px;',
      'border-radius:50%;background:rgba(26,179,176,.30);border:2px solid rgba(26,179,176,.95);',
      'pointer-events:none;z-index:2147483647;transition:transform .08s ease-out}',
      '.__demo_ripple{position:fixed;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;',
      'border:3px solid rgba(26,179,176,.9);pointer-events:none;z-index:2147483646;',
      'animation:__demo_r .55s ease-out forwards}',
      '@keyframes __demo_r{from{transform:scale(.3);opacity:1}to{transform:scale(1.5);opacity:0}}',
    ].join('');
    document.head.appendChild(st);
    const c = document.createElement('div');
    c.id = '__demo_cursor';
    document.body.appendChild(c);
    addEventListener('mousemove', (e) => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
    addEventListener('mousedown', (e) => {
      c.style.transform = 'scale(.7)';
      const r = document.createElement('div');
      r.className = '__demo_ripple';
      r.style.left = e.clientX + 'px';
      r.style.top = e.clientY + 'px';
      document.body.appendChild(r);
      setTimeout(() => r.remove(), 650);
    }, true);
    addEventListener('mouseup', () => { c.style.transform = ''; }, true);
  };
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', install);
  else install();
})();
