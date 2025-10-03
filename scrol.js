<script>
(function () {
  const W   = window.parent || window;
  const DOC = W.document;

  try { W.__chatAutoscrollMsgObs?.disconnect(); } catch (_) {}
  try { W.__chatAutoscrollBootObs?.disconnect(); } catch (_) {}
  W.__chatAutoscrollMsgObs  = null;
  W.__chatAutoscrollBootObs = null;
  W.__chatAutoscrollRoot    = null;

  // Make a short beep using Web Audio API
  function play(id) {
    const audio = DOC.getElementById(id);
    if (audio) {
      audio.currentTime = 0; // rewind if already playing
      audio.play().catch(err => console.log("Play blocked:", err));
    }
  }

  function scrollLast(root) {
    if (!root) return;
    const msgs = root.querySelectorAll('[data-testid="stChatMessage"]');
    if (!msgs.length) return;
    requestAnimationFrame(() => {
      const lastMsg = msgs[msgs.length - 1];
      lastMsg.scrollIntoView({ behavior: 'smooth', block: 'end' });
      const nurseImg = lastMsg.querySelector('img[alt="Nurse avatar"]');
      if (nurseImg) {
        play("Send");
      } else {
        play("Receive");
      }
    });
  }

  function installFor(root) {
    if (!root || root === W.__chatAutoscrollRoot) return;
    try { W.__chatAutoscrollMsgObs?.disconnect(); } catch (_) {}
    W.__chatAutoscrollRoot = root;

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