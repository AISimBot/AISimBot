<script>
const root = window.parent.document.querySelector('.st-key-chatbox');
if (root) {
  const msgs = root.querySelectorAll('[data-testid="stChatMessage"]');
  if (msgs.length) {
    msgs[msgs.length - 1].scrollIntoView({behavior: 'smooth', block: 'end'});
  }
}
</script>