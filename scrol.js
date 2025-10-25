<script>
(function () {
  const W   = window.parent || window;
  const DOC = W.document;

  try { W.__chatAutoscrollMsgObs?.disconnect(); } catch (_) {}
  try { W.__chatAutoscrollBootObs?.disconnect(); } catch (_) {}
  W.__chatAutoscrollMsgObs  = null;
  W.__chatAutoscrollBootObs = null;
  W.__chatAutoscrollRoot    = null;


  function scrollLast(root) {
    if (!root) return;
    const msgs = root.querySelectorAll('[data-testid="stChatMessage"]');
    if (!msgs.length) return;
    requestAnimationFrame(() => {
      msgs[msgs.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
    });
  }

  function installFor(root) {
    if (!root || root === W.__chatAutoscrollRoot) return;
    try { W.__chatAutoscrollMsgObs?.disconnect(); } catch (_) {}
    W.__chatAutoscrollRoot = root;
    // root.setAttribute('inert', '');
    root.style.userSelect = 'none'; // optional: prevent text copying
    let pending = false;
    const msgObs = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.type === 'childList' && m.addedNodes?.length) {
          const hit = Array.from(m.addedNodes).some(n =>
            (n.nodeType === 1) && (
              n.matches?.('[data-testid="stChatMessage"]') ||
              n.querySelector?.('[data-testid="stChatMessage"]')
            )
          );
          if (hit && !pending) {
            pending = true;
            setTimeout(() => { pending = false; scrollLast(root); }, 0);
            break;
          }
        }
      }
    });

    msgObs.observe(root, { childList: true, subtree: true });
    W.__chatAutoscrollMsgObs = msgObs;
    scrollLast(root);
  }

  const bootObs = new MutationObserver(() => {
    const root = DOC.querySelector('.st-key-chatbox');
    if (root && root !== W.__chatAutoscrollRoot) installFor(root);
    if (!root) W.__chatAutoscrollRoot = null;
  });

  bootObs.observe(DOC.documentElement || DOC.body, { childList: true, subtree: true });
  W.__chatAutoscrollBootObs = bootObs;

  const existing = DOC.querySelector('.st-key-chatbox');
  if (existing) installFor(existing);
})();
</script>