<script>
// Plays TTS audio while it is still being generated.
// Python sends each base64 Ogg Opus chunk as a tiny script that calls
// window.__ttsQueue.push([reply, seq, chunk]); a null chunk marks the end.
// The chunks are decoded with ogg-opus-decoder and scheduled back to back with Web Audio.
// stream_audio sends the decoder library (ogg-opus-decoder.min.js) once per session;
// it sets window["ogg-opus-decoder"].
(function () {
  const W = window;
  W.__ttsQueue = W.__ttsQueue || [];
  if (W.__tts) { W.__tts.drain(); return; }

  const tts = W.__tts = {
    reply: null, expect: 0, pending: new Map(), sources: [], next: 0,
    ctx: null, decoder: null, busy: Promise.resolve(),
    stats: { chunks: 0, seconds: 0, firstChunkAt: null, errors: [] },
  };
  // Debug log of the last 300 events; copy it from the console with copy(JSON.stringify(__ttsLog)).
  const log = W.__ttsLog = [];
  function note(ev, data) {
    log.push(Object.assign({ t: Math.round(performance.now()), ev, ctx: tts.ctx && +tts.ctx.currentTime.toFixed(3), state: tts.ctx && tts.ctx.state }, data));
    if (log.length > 300) log.shift();
  }
  note("load", { ua: navigator.userAgent });

  // Wait for the library, in case its script runs after this one.
  const ready = new Promise((resolve) => {
    const check = () => W["ogg-opus-decoder"] ? resolve(W["ogg-opus-decoder"]) : setTimeout(check, 20);
    check();
  })
    .then(async (m) => {
      tts.decoder = new m.OggOpusDecoder();
      await tts.decoder.ready;
    });

  function stop() {
    note("stop", { sources: tts.sources.length });
    for (const s of tts.sources) { try { s.stop(); } catch (_) {} }
    tts.sources = [];
    tts.next = 0;
  }

  async function play(chunk) {
    // The decoder holds back the last Ogg page until it sees more data,
    // so the end marker flushes it. Without this, a short reply never plays.
    let decoded;
    if (chunk === null) {
      decoded = await tts.decoder.flush();
    } else {
      const bytes = Uint8Array.from(atob(chunk), (c) => c.charCodeAt(0));
      decoded = await tts.decoder.decode(bytes);
    }
    const { channelData, samplesDecoded, sampleRate } = decoded;
    tts.stats.chunks += 1;
    if (!samplesDecoded) return;
    if (!tts.ctx) {
      tts.ctx = new AudioContext();
      tts.ctx.onstatechange = () => note("statechange");
      note("context", { rate: tts.ctx.sampleRate });
    }
    const ctx = tts.ctx;
    if (ctx.state === "suspended") ctx.resume();
    const buffer = ctx.createBuffer(channelData.length, samplesDecoded, sampleRate);
    channelData.forEach((data, i) => buffer.copyToChannel(data, i));
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);
    // The first chunk starts now, then each chunk starts where the last one ends.
    const start = Math.max(tts.next, ctx.currentTime);
    source.start(start);
    note("start", { seq: tts.expect - 1, at: +start.toFixed(3), dur: +buffer.duration.toFixed(3), rate: sampleRate });
    source.onended = () => { note("ended", { at: +start.toFixed(3) }); tts.sources = tts.sources.filter((s) => s !== source); };
    tts.sources.push(source);
    tts.next = start + buffer.duration;
    tts.stats.seconds += buffer.duration;
  }

  async function handle(reply, seq, chunk) {
    if (seq === 0 || chunk === null) note(chunk === null ? "end" : "reply", { reply: reply.slice(0, 6), seq });
    if (reply !== tts.reply) {
      // A new reply stops the previous one.
      stop();
      await tts.decoder.reset();
      tts.reply = reply;
      tts.expect = 0;
      tts.pending.clear();
      tts.stats = { chunks: 0, seconds: 0, firstChunkAt: performance.now(), errors: [] };
    }
    // Scripts can run out of order, so play chunks by sequence number.
    tts.pending.set(seq, chunk);
    while (tts.pending.has(tts.expect)) {
      const next = tts.pending.get(tts.expect);
      tts.pending.delete(tts.expect);
      tts.expect += 1;
      await play(next);
    }
  }

  tts.drain = function () {
    const items = W.__ttsQueue.splice(0);
    if (items.length > 1) note("batch", { n: items.length, reply: items[0][0].slice(0, 6) });
    for (const [reply, seq, chunk] of items) {
      tts.busy = tts.busy
        .then(() => ready)
        .then(() => (reply === tts.reply && seq < tts.expect) ? null : handle(reply, seq, chunk))
        .catch((e) => { tts.stats.errors.push(String(e)); note("error", { e: String(e) }); console.error("tts", e); });
    }
  };

  tts.drain();
})();
</script>
