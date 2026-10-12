/**
 * Provenance UI spec v2: "Dispatch"
 * Physical packing-bench design system and workstation engine.
 * Full integration with CCTV RTSP video pipeline, wireless scanner burst interception,
 * temporal activity ribbon, video proof player, and theme switching.
 */

(function () {
  "use strict";

  // --- Element Helper & Selector Aliases ---
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const root = document.documentElement;

  // --- Phosphor-Style Vector SVG Icons ---
  const S = 'width="__W__" height="__W__" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"';
  function ic(path, w) {
    return '<svg ' + S.replace(/__W__/g, w || 18) + '>' + path + '</svg>';
  }

  const ICON = {
    ring: ic('<circle cx="12" cy="12" r="8"/>', 26),
    dot: '<svg width="26" height="26" viewBox="0 0 24 24"><circle class="pulse" cx="12" cy="12" r="7" fill="currentColor"/></svg>',
    check: ic('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 26),
    cam: ic('<rect x="3" y="7" width="13" height="10" rx="2"/><path d="M16 11l5-3v8l-5-3"/><path d="M3 3l18 18"/>', 26),
    folder: ic('<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'),
    down: ic('<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>'),
    clock: ic('<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>', 14),
    warn: ic('<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17.5v.01"/>'),
    x: ic('<path d="M6 6l12 12M18 6L6 18"/>'),
    barcode: ic('<path d="M3 7V5a2 2 0 0 1 2-2h2m10 0h2a2 2 0 0 1 2 2v2m0 10v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M8 7v10m4-10v10m5-10v10"/>'),
    edit: ic('<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>'),
    print: ic('<path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14" rx="1"/>'),
    trash: ic('<path d="M10 11v6m4-6v6m5-11v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'),
    copy: ic('<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>'),
    refresh: ic('<path d="M3 12a9 9 0 0 1 9-9a9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>'),
    file: ic('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'),
    expand: ic('<path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3m8 0h3a2 2 0 0 0 2-2v-3"/>'),
    shrink: ic('<path d="M4 14h6v6m10-10h-6V4m0 6 7-7M3 21l7-7"/>'),
    shield_check: ic('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>', 14),
    play: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg>',
    pause: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4.5" width="4.5" height="15"/><rect x="13.5" y="4.5" width="4.5" height="15"/></svg>'
  };

  function renderIcons() {
    $$("[data-i]").forEach(function (el) {
      if (ICON[el.dataset.i]) el.innerHTML = ICON[el.dataset.i];
    });
  }

  // --- Utility Formatters ---
  function pad(n) { return String(n).padStart(2, "0"); }
  function fmt(s) { return pad(Math.floor(s / 60)) + ":" + pad(Math.floor(s % 60)); }
  function hm(m) { return pad(Math.floor(m / 60)) + ":" + pad(Math.floor(m % 60)); }

  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return "0 B";
    const k = 1024;
    const dm = 1;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  }

  // --- Application State ---
  let appState = "idle"; // 'idle' | 'recording' | 'saved' | 'offline'
  let activeSession = null;
  let currentModalSession = null;
  let pendingDeleteSession = null;
  let allSessions = [];
  let recentClips = [];
  let timerInterval = null;
  let savedStateTimeout = null;
  let searchDebounceTimer = null;
  let statusPollInterval = null;

  // Audio Context & Buffers
  let audioCtx = null;
  const audioBuffers = { beep: null, finish: null, error: null, delete: null };

  // --- Industrial Workstation Kiosk Hardening ---
  function initKioskHardening() {
    // ponytail: strict kiosk lockout prevents viewing source, inspection, or tampering
    window.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      return false;
    }, { capture: true });

    window.addEventListener("keydown", (e) => {
      // Zoom controls
      if ((e.ctrlKey || e.metaKey) && ["+", "-", "=", "0", "_"].includes(e.key)) {
        e.preventDefault();
      }
      // F5 / Refresh
      if (e.key === "F5" || ((e.ctrlKey || e.metaKey) && (e.key === "r" || e.key === "R"))) {
        e.preventDefault();
      }
      // F12 / DevTools / View Source
      if (
        e.key === "F12" ||
        ((e.ctrlKey || e.metaKey) && (
          (e.shiftKey && ["I", "i", "J", "j", "C", "c"].includes(e.key)) ||
          e.key === "u" || e.key === "U"
        ))
      ) {
        e.preventDefault();
      }
      // Save page
      if ((e.ctrlKey || e.metaKey) && (e.key === "s" || e.key === "S")) {
        e.preventDefault();
      }
      // History back/forward (Alt + Left/Right)
      if (e.altKey && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
        e.preventDefault();
      }
    }, { capture: true });

    window.addEventListener("wheel", (e) => {
      if (e.ctrlKey || e.metaKey) e.preventDefault();
    }, { passive: false });

    window.addEventListener("dragover", (e) => e.preventDefault(), false);
    window.addEventListener("drop", (e) => e.preventDefault(), false);
    window.addEventListener("dragstart", (e) => e.preventDefault(), false);
  }

  // --- Offline Web Audio Chimes ---
  function initAudio() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext && !audioCtx) audioCtx = new AudioContext();
    } catch (e) {
      console.warn("Web Audio not available:", e);
    }
  }

  async function preloadAudio() {
    if (!audioCtx) initAudio();
    if (!audioCtx) return;
    const files = {
      beep: "/static/audio/scanner-beep.wav",
      finish: "/static/audio/scanner-finish.wav",
      error: "/static/audio/scanner-error.wav",
      delete: "/static/audio/scanner-delete.wav"
    };
    for (const [key, url] of Object.entries(files)) {
      try {
        const resp = await fetch(url);
        if (resp.ok) {
          const ab = await resp.arrayBuffer();
          audioBuffers[key] = await audioCtx.decodeAudioData(ab);
        }
      } catch (e) {
        // Fallback tone synthesis will trigger if WAV missing
      }
    }
  }

  function playChime(type) {
    if (!audioCtx) initAudio();
    if (!audioCtx) return;
    if (audioCtx.state === "suspended") audioCtx.resume();

    if (audioBuffers[type]) {
      try {
        const src = audioCtx.createBufferSource();
        src.buffer = audioBuffers[type];
        src.connect(audioCtx.destination);
        src.start(0);
        return;
      } catch (e) {
        // fallback
      }
    }

    // Synthesized fallbacks
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      if (type === "beep") {
        osc.frequency.setValueAtTime(1760, audioCtx.currentTime); // A6
        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.08);
      } else if (type === "finish") {
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.12);
        gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.16);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.16);
      } else if (type === "error") {
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(220, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.2);
      }
    } catch (e) {
      console.warn("Audio chime error:", e);
    }
  }

  // --- Toasts System (Tactile & Apple Motion Primitives) ---
  const toasts = $("#toasts");
  function toast(kind, msg) {
    const activeDialog = document.querySelector("dialog[open]");
    let target = toasts;
    if (activeDialog) {
      let dt = activeDialog.querySelector(".dialog-toasts");
      if (!dt) {
        dt = document.createElement("div");
        dt.className = "dialog-toasts";
        activeDialog.appendChild(dt);
      }
      target = dt;
    }
    if (!target) return;

    const el = document.createElement("div");
    el.className = "toast " + (kind || "ok");
    el.setAttribute("role", "status");

    const i = document.createElement("span");
    i.className = "ti";
    if (kind === "ok") {
      i.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg>';
    } else if (kind === "warn") {
      i.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17.5v.01"/></svg>';
    } else if (kind === "danger") {
      i.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>';
    } else {
      i.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M12 11v5"/></svg>';
    }

    const t = document.createElement("span");
    t.className = "toast-msg";
    t.textContent = msg;

    el.appendChild(i);
    el.appendChild(t);

    function dismiss() {
      if (el.classList.contains("out")) return;
      el.classList.add("out");
      el.addEventListener("animationend", function () {
        if (el.parentNode) el.remove();
      }, { once: true });
      setTimeout(function () {
        if (el.parentNode) el.remove();
      }, 280);
    }

    el.addEventListener("click", dismiss);
    target.appendChild(el);

    setTimeout(dismiss, 3400);
  }
  window.toast = toast;

  // --- Live Clock ---
  function tickClock() {
    const d = new Date();
    const s = pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
    const clk = $("#clock");
    if (clk) clk.textContent = s;
    const ft = $("#feedTime");
    if (ft) {
      const ymd = d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
      ft.textContent = "CAM 01  " + ymd + " " + s;
    }
  }
  setInterval(tickClock, 1000);
  tickClock();

  // --- Navigation & View Switching ---
  // --- Navigation & View Switching ---
  window.switchView = function (v) {
    $$(".tab").forEach(function (t) {
      t.setAttribute("aria-selected", t.dataset.view === v);
    });
    ["station", "manifest", "archive", "settings"].forEach(function (name) {
      const sec = $("#v-" + name);
      if (sec) sec.hidden = (name !== v);
    });
    if (v === "settings") {
      paintSwatches();
    }
    if (v === "archive") {
      loadSessions();
    }
    if (v === "manifest") {
      loadManifestData();
    }
    if (v === "station") {
      setTimeout(() => { if (barcodeInput) barcodeInput.focus(); }, 60);
    }
  };

  // --- Dispatch Manifest Controller ---
  window.loadManifestProgressOnly = async function () {
    try {
      const res = await fetch("/api/manifest/progress");
      const prog = await res.json();
      if (prog) {
        const pill = $("#manifestPill");
        if (pill) {
          pill.textContent = `${prog.packed}/${prog.total}`;
          if (prog.total > 0 && prog.packed === prog.total) {
            pill.style.background = "rgba(16,185,129,0.3)";
            pill.style.color = "#10b981";
          }
        }
      }
    } catch (e) {
      // Non-blocking telemetry
    }
  };

  window.loadManifestData = async function () {
    try {
      const [progRes, itemsRes] = await Promise.all([
        fetch("/api/manifest/progress").then(r => r.json()),
        fetch("/api/manifest/items?limit=250").then(r => r.json())
      ]);

      if (progRes) {
        if ($("#mStatTotal")) $("#mStatTotal").textContent = progRes.total || 0;
        if ($("#mStatPacked")) $("#mStatPacked").textContent = progRes.packed || 0;
        if ($("#mStatPending")) $("#mStatPending").textContent = progRes.pending || 0;
        if ($("#mStatPercent")) $("#mStatPercent").textContent = (progRes.percentage || 0).toFixed(1) + "%";
        if ($("#manifestProgressBar")) $("#manifestProgressBar").style.width = (progRes.percentage || 0) + "%";
        const pill = $("#manifestPill");
        if (pill) pill.textContent = `${progRes.packed}/${progRes.total}`;
      }

      const tbody = $("#manifestRows");
      if (tbody) {
        if (!itemsRes || !itemsRes.length) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--pallet-muted)">No manifest records found. Import a CSV dispatch list above.</td></tr>`;
          return;
        }

        let html = "";
        itemsRes.forEach(it => {
          const isPacked = it.status === "packed";
          const statusBadge = isPacked
            ? `<span class="tag ok" style="background:rgba(16,185,129,0.15);color:#10b981;font-weight:700">PACKED</span>`
            : `<span class="tag" style="background:rgba(245,158,11,0.15);color:#f59e0b;font-weight:700">PENDING</span>`;

          const actionBtn = isPacked && it.clip_filename
            ? `<button class="btn sm quiet" onclick="revealClipByFilename('${it.clip_filename}')" title="Highlight video clip in File Explorer"><span data-i="folder"></span>Show clip</button>`
            : `<span style="color:var(--pallet-muted);font-size:12px">Waiting scan</span>`;

          html += `<tr>
            <td style="font-family:monospace;font-weight:700">${escapeHtml(it.tracking_number || "")}</td>
            <td>${escapeHtml(it.order_id || "-")}</td>
            <td>${escapeHtml(it.recipient || "-")}</td>
            <td>${escapeHtml(it.sku || "-")}</td>
            <td>${statusBadge}</td>
            <td style="color:var(--pallet-muted);font-size:12px">${it.packed_at ? it.packed_at : "-"}</td>
            <td style="text-align:right">${actionBtn}</td>
          </tr>`;
        });
        tbody.innerHTML = html;
      }
    } catch (e) {
      toast("danger", "Failed to load manifest records.");
    }
  };

  window.handleManifestFileSelected = function (evt) {
    const file = evt.target.files && evt.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async function (e) {
      const text = e.target.result;
      try {
        toast("info", "Importing dispatch manifest...");
        const res = await fetch("/api/manifest/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ csv_text: text, replace: false })
        });
        const data = await res.json();
        if (data && data.success) {
          toast("ok", `Imported ${data.imported} shipments into daily manifest.`);
          loadManifestData();
        } else {
          toast("danger", "Failed to import manifest: " + ((data && data.error) || "Invalid format"));
        }
      } catch (err) {
        toast("danger", "Error communicating with manifest service.");
      }
      evt.target.value = "";
    };
    reader.readAsText(file);
  };

  window.clearManifestData = async function () {
    if (!confirm("Are you sure you want to clear the daily manifest records?")) return;
    try {
      const res = await fetch("/api/manifest/clear", { method: "POST" });
      const data = await res.json();
      if (data && data.success) {
        toast("ok", "Daily manifest cleared.");
        loadManifestData();
      }
    } catch (e) {
      toast("danger", "Failed to clear manifest.");
    }
  };

  window.revealClipByFilename = async function (fn) {
    if (!fn) return;
    try {
      const res = await fetch("/api/clips/reveal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: fn })
      });
      const data = await res.json();
      if (data && data.success) {
        toast("ok", "Video clip highlighted in File Explorer.");
      } else {
        toast("warn", "Clip file not found on disk.");
      }
    } catch (e) {
      toast("danger", "Failed to reveal clip.");
    }
  };

  // --- Theme Controller (System / Light / Dark) ---
  function initTheme() {
    const saved = localStorage.getItem("provenance_theme") || "system";
    setAppTheme(saved, false);
  }

  window.setAppTheme = function (t, persist) {
    if (persist !== false) localStorage.setItem("provenance_theme", t);
    $$("#themeSeg button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.t === t);
    });
    if (t === "system") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", t);
    }
    paintSwatches();
  };

  function paintSwatches() {
    const swN = $("#swN");
    const swS = $("#swS");
    if (!swN || !swS) return;

    const cs = getComputedStyle(root);
    const NEUT = [
      ["canvas", "--canvas"],
      ["surface", "--surface"],
      ["recess", "--recess"],
      ["hover", "--hover"],
      ["press", "--press"],
      ["line", "--line"],
      ["line-strong", "--line-strong"],
      ["frame", "--frame"],
      ["ink", "--ink"],
      ["ink-2", "--ink-2"],
      ["ink-3", "--ink-3"]
    ];
    const ST = [
      ["beacon", "--beacon"],
      ["beacon text", "--beacon-text"],
      ["pallet", "--pallet"],
      ["pallet tint", "--pallet-tint"],
      ["pallet ink", "--pallet-ink"],
      ["hivis", "--hivis"],
      ["hivis tint", "--hivis-tint"],
      ["hivis ink", "--hivis-ink"],
      ["cochineal", "--coch"],
      ["cochineal tint", "--coch-tint"],
      ["cochineal ink", "--coch-ink"]
    ];

    [[swN, NEUT], [swS, ST]].forEach(function ([box, list]) {
      box.innerHTML = "";
      list.forEach(function ([label, varName]) {
        const d = document.createElement("div");
        d.className = "sw";
        const c = document.createElement("div");
        c.className = "c";
        c.style.background = "var(" + varName + ")";
        const t = document.createElement("div");
        t.className = "t";
        const b = document.createElement("b");
        b.textContent = label;
        t.appendChild(b);
        t.appendChild(document.createTextNode(varName + "  " + cs.getPropertyValue(varName).trim()));
        d.appendChild(c);
        d.appendChild(t);
        box.appendChild(d);
      });
    });
  }

  // --- Status Band & State Machine ---
  const band = $("#band");
  const viewport = $("#viewport");
  const barcodeInput = $("#barcode");
  const startBtn = $("#start");
  const finishBtn = $("#finish");

  const STATES = {
    idle: {
      t: "READY TO SCAN",
      s: "Scan a parcel barcode to start recording.",
      i: "ring"
    },
    recording: {
      t: "RECORDING",
      s: "Footage is being recorded. Press Enter to finish.",
      i: "dot"
    },
    saved: {
      t: "CLIP SAVED",
      s: "Stored in archive. Ready for the next parcel.",
      i: "check"
    },
    offline: {
      t: "CAMERA FEED OFFLINE",
      s: "No signal from CCTV RTSP source. Check cable, then retry.",
      i: "cam"
    }
  };

  let recordStartTime = 0;

  function setStationState(s, codeText, durationSec) {
    appState = s;
    clearTimeout(savedStateTimeout);
    clearInterval(timerInterval);

    if (band) band.dataset.state = s;
    if (viewport) viewport.dataset.state = s;
    document.body.dataset.state = s;

    const conf = STATES[s] || STATES.idle;
    if ($("#bandTitle")) $("#bandTitle").textContent = conf.t;
    if ($("#bandSub")) $("#bandSub").textContent = conf.s;
    if ($("#bandIcon")) $("#bandIcon").innerHTML = ICON[conf.i];

    if (startBtn) startBtn.disabled = (s !== "idle");
    if (finishBtn) finishBtn.disabled = (s !== "recording");

    const codePill = $("#bandCode");
    if (codePill) {
      if (codeText) codePill.textContent = codeText;
    }

    if (s === "recording") {
      recordStartTime = activeSession && activeSession.start_time
        ? new Date(activeSession.start_time).getTime()
        : Date.now();
      updateTimer();
      timerInterval = setInterval(updateTimer, 250);
    } else if (s === "saved") {
      if (durationSec !== undefined) {
        if ($("#timer")) $("#timer").textContent = fmt(durationSec);
      }
      savedStateTimeout = setTimeout(function () {
        setStationState("idle");
      }, 2500);
    } else if (s === "idle") {
      if ($("#timer")) $("#timer").textContent = "00:00";
    }
  }

  function updateTimer() {
    const elapsed = Math.max(0, Math.floor((Date.now() - recordStartTime) / 1000));
    if ($("#timer")) $("#timer").textContent = fmt(elapsed);
  }

  // --- Camera Stream Handlers ---
  function handleStreamError() {
    const dot = $("#teleDot");
    if (dot) dot.style.background = "var(--coch-text)";
    if (appState !== "recording") {
      setStationState("offline");
    }
  }
  window.handleStreamError = handleStreamError;

  function handleStreamLoaded() {
    const dot = $("#teleDot");
    if (dot) dot.style.background = "var(--pallet-text)";
    if (appState === "offline") {
      setStationState("idle");
    }
  }
  window.handleStreamLoaded = handleStreamLoaded;

  // ponytail: attach stream listeners via DOM event listeners, avoiding inline HTML race condition
  const liveImg = $("#liveStream");
  if (liveImg) {
    liveImg.addEventListener("load", handleStreamLoaded);
    liveImg.addEventListener("error", handleStreamError);
  }

  window.quickSwitchCamera = async function (source) {
    try {
      const resp = await fetch("/api/camera/source", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: source })
      });
      const data = await resp.json();
      if (data.success) {
        const isRtsp = source === "rtsp";
        $("#srcRtspBtn")?.setAttribute("aria-pressed", isRtsp);
        $("#srcWebcamBtn")?.setAttribute("aria-pressed", !isRtsp);
        toast("ok", "Camera switched to " + (isRtsp ? "CCTV RTSP" : "Webcam"));
        // reload live stream element
        const img = $("#liveStream");
        if (img) img.src = "/api/camera/stream?t=" + Date.now();
      } else {
        toast("warn", "Camera switch failed: " + (data.error || "Unknown"));
      }
    } catch (e) {
      toast("danger", "Network error changing camera source.");
    }
  };

  window.toggleLiveCameraFullscreen = function () {
    const feed = $("#viewportFeed");
    const btn = $("#liveFsBtn");
    if (!feed) return;

    const isFs = document.fullscreenElement || feed.classList.contains("fs-active");

    if (!isFs) {
      feed.classList.add("fs-active");
      if (btn) btn.innerHTML = (ICON.shrink || ICON.x) + " <span>Exit Fullscreen</span>";
      if (feed.requestFullscreen) {
        feed.requestFullscreen().catch(() => {});
      }
    } else {
      feed.classList.remove("fs-active");
      if (btn) btn.innerHTML = ICON.expand + " <span>Fullscreen</span>";
      if (document.fullscreenElement && document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
    }
  };

  document.addEventListener("fullscreenchange", function () {
    const feed = $("#viewportFeed");
    const btn = $("#liveFsBtn");
    if (!feed) return;
    if (!document.fullscreenElement) {
      feed.classList.remove("fs-active");
      if (btn) btn.innerHTML = ICON.expand + " <span>Fullscreen</span>";
    } else {
      feed.classList.add("fs-active");
      if (btn) btn.innerHTML = (ICON.shrink || ICON.x) + " <span>Exit Fullscreen</span>";
    }
  });

  // --- Barcode Scanning & Global Wireless Scanner Interceptor ---
  // Zero mouse click or manual focus required: Captures scanner bursts globally.
  let scannerBuffer = "";
  let lastKeyTime = 0;
  let burstDebounceTimer = null;
  let pendingFKeyTimer = null;

  function setupBarcodeInput() {
    // 1. Maintain focus on #barcode whenever clicking anywhere on Station screen
    window.addEventListener("click", function (e) {
      const vStation = $("#v-station");
      if (!vStation || vStation.hidden) return;
      if (e.target.closest("dialog, input, textarea, select, button, a, [role='button']")) return;
      if (barcodeInput) barcodeInput.focus();
    });

    // 2. Global Keydown Listener for Wireless Barcode Scanners & Workstation Hotkeys
    window.addEventListener("keydown", function (e) {
      // Clear any pending single-F hotkey timer on subsequent keystrokes
      if (pendingFKeyTimer && e.key !== "f" && e.key !== "F") {
        clearTimeout(pendingFKeyTimer);
        pendingFKeyTimer = null;
      }

      // Escape key exits fullscreen
      if (e.key === "Escape") {
        const feed = $("#viewportFeed");
        if (document.fullscreenElement || (feed && feed.classList.contains("fs-active"))) {
          e.preventDefault();
          toggleLiveCameraFullscreen();
          return;
        }
      }

      // Ignore modifier and navigation keys
      if (
        e.key === "Tab" ||
        e.key === "Escape" ||
        e.key === "CapsLock" ||
        e.key === "Shift" ||
        e.key === "Control" ||
        e.key === "Alt" ||
        e.key === "Meta" ||
        (e.key.startsWith("F") && e.key.length > 1)
      ) {
        return;
      }

      const now = Date.now();
      const interval = now - lastKeyTime;
      lastKeyTime = now;

      const activeEl = document.activeElement;
      const isOtherInput = activeEl &&
        (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA") &&
        activeEl.id !== "barcode";

      // Fullscreen shortcut check for 'f' / 'F' key
      if ((e.key === "f" || e.key === "F") && !e.ctrlKey && !e.altKey && !e.metaKey) {
        const feed = $("#viewportFeed");
        const isFs = document.fullscreenElement || (feed && feed.classList.contains("fs-active"));
        if (isFs) {
          e.preventDefault();
          e.stopPropagation();
          toggleLiveCameraFullscreen();
          return;
        }

        // If not typing in search or edit inputs, check if single keypress vs scanner burst
        if (!isOtherInput) {
          if ((!barcodeInput || barcodeInput.value === "") && scannerBuffer.length === 0) {
            clearTimeout(pendingFKeyTimer);
            pendingFKeyTimer = setTimeout(function () {
              if (scannerBuffer === "f" || scannerBuffer === "F" || scannerBuffer === "") {
                scannerBuffer = "";
                if (barcodeInput) barcodeInput.value = "";
                toggleLiveCameraFullscreen();
              }
              pendingFKeyTimer = null;
            }, 80);
          }
        }
      }

      // Enter key completes a barcode scan
      if (e.key === "Enter") {
        clearTimeout(burstDebounceTimer);
        burstDebounceTimer = null;
        let code = scannerBuffer.trim();
        // If buffer was empty but the barcode box has text (manual typing + Enter)
        if (!code && barcodeInput && barcodeInput.value.trim().length >= 2) {
          code = barcodeInput.value.trim();
        }

        if (code.length >= 2) {
          e.preventDefault();
          e.stopPropagation();
          scannerBuffer = "";
          processScannedCode(code);
          return;
        } else if (appState === "recording" && (!activeEl || activeEl.id === "barcode" || activeEl.tagName === "BODY")) {
          // Pressing enter with empty box while recording triggers finish
          e.preventDefault();
          handleFinishClick();
          return;
        }
        scannerBuffer = "";
        return;
      }

      // Only single character printable keys
      if (e.key.length !== 1) return;

      // If human paused for > 300ms, reset the burst buffer
      if (interval > 300 && scannerBuffer.length > 0) {
        scannerBuffer = "";
      }

      // Hardware scanners typically burst at < 50ms intervals
      const isFastBurst = interval <= 50;

      // If user is actively typing in another input (e.g. searching archive or editing metadata)
      if (isOtherInput) {
        // If slow human typing, let the other input handle it
        if (!isFastBurst && scannerBuffer.length === 0) {
          return;
        }
        // If fast burst, intercept from the other input!
        scannerBuffer += e.key;
        clearTimeout(burstDebounceTimer);
        burstDebounceTimer = setTimeout(function () {
          if (scannerBuffer.length >= 3) {
            const candidate = scannerBuffer.trim();
            scannerBuffer = "";
            processScannedCode(candidate);
          } else {
            scannerBuffer = "";
          }
        }, 200);
        return;
      }

      // Focus is NOT in another input (operator is on station or general area)
      scannerBuffer += e.key;

      // Automatically route into the barcode textbox visually
      if (barcodeInput) {
        if (document.activeElement !== barcodeInput) {
          barcodeInput.focus();
        }
        barcodeInput.value = scannerBuffer;
      }

      // Scanners configured without Enter suffix fallback (250ms silence window)
      clearTimeout(burstDebounceTimer);
      burstDebounceTimer = setTimeout(function () {
        if (scannerBuffer.length >= 3) {
          const candidate = scannerBuffer.trim();
          scannerBuffer = "";
          processScannedCode(candidate);
        }
      }, 250);
    }, { capture: true });

    // Focus immediately on load
    if (barcodeInput) barcodeInput.focus();
  }

  function processScannedCode(code) {
    if (!code) return;
    code = code.trim();
    if (!code) return;

    // Auto-switch to Station view if currently on Archive or Settings
    const vStation = $("#v-station");
    if (vStation && vStation.hidden) {
      switchView("station");
    }

    if (barcodeInput) {
      barcodeInput.value = code;
      barcodeInput.classList.add("flash");
      setTimeout(() => barcodeInput.classList.remove("flash"), 400);
      barcodeInput.focus();
    }

    const upper = code.toUpperCase();
    if (
      upper === "FINISH" ||
      upper === "CMD:FINISH" ||
      upper === "STOP" ||
      upper === "CMD:STOP" ||
      upper === "DONE" ||
      upper === "END" ||
      upper.endsWith("FINISH")
    ) {
      if (appState === "recording") {
        handleFinishClick();
      } else {
        toast("warn", "No recording in progress to finish.");
        playChime("error");
        if (barcodeInput) barcodeInput.value = "";
      }
      return;
    }

    // Standard parcel barcode
    if (appState === "idle") {
      triggerBarcodeStart(code);
    } else if (appState === "recording") {
      if (activeSession && activeSession.barcode === code) {
        playChime("beep");
        toast("ok", "Already recording parcel " + code);
      } else {
        // Auto-chain next parcel seamlessly!
        triggerBarcodeStart(code, true);
      }
    }
  }

  window.simulateScan = function (code) {
    processScannedCode(code);
  };

  async function triggerBarcodeStart(code, isAutoChain = false) {
    if (!code) {
      toast("warn", "Scan or enter a barcode first.");
      if (barcodeInput) barcodeInput.focus();
      return;
    }
    if (appState === "recording") {
      if (!isAutoChain || (activeSession && activeSession.barcode === code)) {
        toast("warn", "Already recording " + (activeSession?.barcode || ""));
        return;
      }
    }

    try {
      if (barcodeInput) {
        barcodeInput.classList.add("flash");
        setTimeout(() => barcodeInput.classList.remove("flash"), 400);
      }

      const resp = await fetch("/api/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ barcode: code })
      });
      const data = await resp.json();
      const sess = data.session || data;

      if (data.success && (data.session || data.session_id || sess.session_id || sess.id)) {
        activeSession = {
          id: sess.id || sess.session_id || data.session_id,
          barcode: sess.barcode || code,
          start_time: sess.start_time || new Date().toISOString()
        };
        playChime("beep");
        setStationState("recording", code);

        const pill = $("#bandCode");
        if (pill) {
          pill.classList.remove("pop");
          void pill.offsetWidth;
          pill.classList.add("pop");
        }

        toast("ok", (isAutoChain ? "Auto-chained parcel: " : "Recording started: ") + code);
        if (barcodeInput) {
          barcodeInput.value = code;
          barcodeInput.select();
          setTimeout(() => { if (appState === "recording" && barcodeInput) barcodeInput.value = ""; }, 1200);
        }
      } else {
        playChime("error");
        toast("warn", data.error || "Failed to start recording");
      }
    } catch (e) {
      playChime("error");
      toast("danger", "Connection error starting session.");
    }
  }

  window.handleStartClick = function () {
    const val = barcodeInput ? barcodeInput.value.trim() : "";
    triggerBarcodeStart(val);
  };

  window.handleFinishClick = async function () {
    if (appState !== "recording") return;

    try {
      const resp = await fetch("/api/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const data = await resp.json();
      const finished = data.session || data;

      if (data.success && (data.session || data.session_id || finished.session_id || finished.id)) {
        playChime("finish");
        activeSession = null;

        const durSec = finished.duration_seconds || 0;
        const bc = finished.barcode || (barcodeInput ? barcodeInput.value.trim() : "PKG");
        setStationState("saved", bc, durSec);
        toast("ok", "Clip saved for " + bc + " (" + fmt(durSec) + ")");

        if (barcodeInput) {
          barcodeInput.value = "";
          setTimeout(() => barcodeInput.focus(), 100);
        }

        // Optimistic real-time entry in recent clips list
        const optId = finished.id || finished.session_id || Date.now();
        const optItem = {
          id: optId,
          barcode: bc,
          order_id: finished.order_id || "",
          carrier: finished.carrier || "",
          start_time: new Date().toISOString(),
          duration_seconds: durSec,
          file_size_bytes: finished.file_size_bytes || 0,
          status: "completed",
          clip_filename: finished.clip_filename || (bc + ".mp4")
        };
        if (!allSessions.some(s => s.id === optId)) {
          allSessions.unshift(optItem);
          renderRecentClips(allSessions);
          renderRibbon(allSessions);
          renderArchiveRows();
        }

        // Staggered loadSessions calls as background FFmpeg/OpenCV writer flushes MP4 to disk
        loadSessions();
        loadManifestProgressOnly();
        setTimeout(loadSessions, 400);
        setTimeout(loadSessions, 1200);
        setTimeout(loadSessions, 2500);
      } else {
        playChime("error");
        toast("warn", data.error || "Failed to stop recording.");
      }
    } catch (e) {
      playChime("error");
      toast("danger", "Connection error stopping session.");
    }
  };

  // --- Shift Ribbon (Pacing Tape Measure) ---
  function renderRibbon(sessions) {
    const track = $("#track");
    if (!track) return;

    // Shift window: 8:00 to 18:00 (or current day 8:00 to 20:00)
    const now = new Date();
    const currentHour = now.getHours();
    let startHour = 8;
    let endHour = 18;
    if (currentHour >= 18) endHour = Math.min(24, currentHour + 2);
    if (currentHour < 8) startHour = Math.max(0, currentHour - 1);

    const START_MIN = startHour * 60;
    const END_MIN = endHour * 60;
    const NOW_MIN = now.getHours() * 60 + now.getMinutes() + (now.getSeconds() / 60);

    track.innerHTML = "";

    // Draw hour major marks with tabular hour numerals
    for (let h = START_MIN; h <= END_MIN; h += 60) {
      const hr = document.createElement("div");
      hr.className = "hr";
      hr.style.left = ((h - START_MIN) / (END_MIN - START_MIN) * 100) + "%";
      const sp = document.createElement("span");
      sp.textContent = pad(Math.floor(h / 60)) + ":00";
      hr.appendChild(sp);
      track.appendChild(hr);
    }

    // Playhead needle
    const ph = document.createElement("div");
    ph.className = "playhead";
    ph.id = "playhead";
    const phPct = Math.max(0, Math.min(100, (NOW_MIN - START_MIN) / (END_MIN - START_MIN) * 100));
    ph.style.left = phPct + "%";
    track.appendChild(ph);

    // Plot parcels
    let shiftCount = 0;
    let totalDuration = 0;

    sessions.forEach(function (s) {
      if (!s.start_time) return;
      const st = new Date(s.start_time);
      // check if today
      if (st.toDateString() !== now.toDateString()) return;

      shiftCount++;
      const dur = s.duration_seconds || 0;
      totalDuration += dur;

      const sMin = st.getHours() * 60 + st.getMinutes() + (st.getSeconds() / 60);
      if (sMin < START_MIN || sMin > END_MIN) return;

      const pct = (sMin - START_MIN) / (END_MIN - START_MIN) * 100;
      const isAbnormal = dur >= 60; // Flag parcels > 60s
      const tick = document.createElement("div");
      tick.className = "tick" + (isAbnormal ? " ab" : "");
      tick.style.left = pct + "%";
      tick.tabIndex = 0;
      tick.setAttribute("data-tip", hm(sMin) + "  " + s.barcode + "  " + fmt(dur));
      tick.innerHTML = "<i></i>";

      tick.addEventListener("click", function () {
        openProofModal(s);
      });

      track.insertBefore(tick, ph);
    });

    // Update Ribbon KPI Header
    if ($("#mCount")) $("#mCount").textContent = shiftCount;
    const avg = shiftCount > 0 ? Math.round(totalDuration / shiftCount) : 0;
    if ($("#mAvg")) $("#mAvg").textContent = fmt(avg);

    // Throughput rate
    const hoursElapsed = Math.max(0.5, (NOW_MIN - START_MIN) / 60);
    const rate = (shiftCount / hoursElapsed).toFixed(1);
    if ($("#mRate")) $("#mRate").textContent = rate;
  }

  // --- Recent Finished Clips List ---
  function renderRecentClips(sessions) {
    const box = $("#clipList");
    if (!box) return;

    recentClips = sessions.slice(0, 10);
    if (!recentClips.length) {
      box.innerHTML = '<div class="empty">No clips recorded yet. Scan a parcel to record one.</div>';
      return;
    }

    box.innerHTML = "";
    recentClips.forEach(function (c) {
      const row = document.createElement("div");
      row.className = "clip";

      const left = document.createElement("div");
      const bc = document.createElement("div");
      bc.className = "bc";
      bc.textContent = c.barcode || "PKG-UNKNOWN";

      const meta = document.createElement("div");
      meta.className = "meta";

      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = c.order_id || ("ORD-" + c.id);

      const tm = document.createElement("span");
      const d = c.start_time ? new Date(c.start_time) : new Date();
      tm.textContent = pad(d.getHours()) + ":" + pad(d.getMinutes());

      const du = document.createElement("span");
      du.className = "d";
      du.textContent = fmt(c.duration_seconds || 0);

      meta.appendChild(tag);
      meta.appendChild(tm);
      meta.appendChild(du);

      if ((c.duration_seconds || 0) >= 90) {
        const toTag = document.createElement("span");
        toTag.className = "tag to";
        toTag.innerHTML = ICON.clock + "Timeout";
        meta.appendChild(toTag);
      }

      left.appendChild(bc);
      left.appendChild(meta);

      const proofBtn = document.createElement("button");
      proofBtn.className = "btn sm quiet";
      proofBtn.textContent = "Proof";
      proofBtn.addEventListener("click", function () {
        openProofModal(c);
      });

      row.appendChild(left);
      row.appendChild(proofBtn);
      box.appendChild(row);
    });
    box.scrollTop = 0;
  }

  // --- Archive Table ---
  window.loadSessions = async function () {
    try {
      const resp = await fetch("/api/sessions?limit=100");
      if (resp.ok) {
        const data = await resp.json();
        allSessions = Array.isArray(data) ? data : (data.sessions || []);
        renderArchiveRows();
        renderRibbon(allSessions);
        renderRecentClips(allSessions);
      }
    } catch (e) {
      console.warn("Could not load sessions:", e);
    }
  };

  window.reconcileClipsFromDisk = async function () {
    try {
      toast("info", "Scanning storage directory for video clips...");
      const resp = await fetch("/api/sessions/reconcile", { method: "POST" });
      const data = await resp.json();
      if (data && data.success) {
        if (data.reconciled > 0) {
          toast("ok", `Restored ${data.reconciled} video clips from storage folder.`);
        } else {
          toast("ok", `Storage folder in sync (${data.scanned} clips scanned).`);
        }
        window.loadSessions();
      } else {
        toast("warn", "Sync failed: " + ((data && data.error) || "Unknown error"));
      }
    } catch (e) {
      toast("danger", "Connection error syncing storage folder.");
    }
  };

  window.debounceSearch = function () {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(renderArchiveRows, 150);
  };

  function renderArchiveRows() {
    const q = $("#q") ? $("#q").value.trim().toLowerCase() : "";
    const tb = $("#rows");
    if (!tb) return;

    // Capture currently checked clip IDs before rebuilding DOM
    const checkedIds = new Set(
      $$(".row-chk:checked", tb).map(cb => {
        const tr = cb.closest("tr");
        return tr ? String(tr.dataset.id) : null;
      }).filter(Boolean)
    );

    tb.innerHTML = "";
    const filtered = allSessions.filter(function (r) {
      if (!q) return true;
      const bc = (r.barcode || "").toLowerCase();
      const ord = (r.order_id || "").toLowerCase();
      const car = (r.carrier || "").toLowerCase();
      return bc.includes(q) || ord.includes(q) || car.includes(q);
    });

    if (!filtered.length) {
      tb.innerHTML = '<tr><td colspan="8" class="empty" style="text-align:center;padding:24px">No matching clips found in archive.</td></tr>';
      updateBulkDeleteButton();
      return;
    }

    filtered.forEach(function (r) {
      const tr = document.createElement("tr");
      tr.dataset.id = r.id;

      const dur = r.duration_seconds || 0;
      const sizeStr = formatBytes(r.file_size_bytes || 0);
      const isTimeout = dur >= 90;

      tr.innerHTML = `
        <td><input type="checkbox" class="row-chk" aria-label="Select clip"></td>
        <td class="bc">${r.barcode || "PKG-UNKNOWN"}</td>
        <td><span class="tag">${r.order_id || "ORD-" + r.id}</span></td>
        <td>${r.start_time ? r.start_time.replace("T", " ").slice(0, 16) : "---"}</td>
        <td>${fmt(dur)}</td>
        <td>${sizeStr}</td>
        <td>${isTimeout ? '<span class="tag to">' + ICON.clock + 'Timeout</span>' : ''}</td>
        <td class="act"></td>
      `;

      const act = tr.querySelector(".act");
      function mkBtn(label, cls, icon, fn, title) {
        const b = document.createElement("button");
        b.className = "btn sm " + cls;
        if (title) b.title = title;
        b.innerHTML = (icon ? icon + " " : "") + label;
        b.addEventListener("click", fn);
        act.appendChild(b);
      }

      mkBtn("View proof", "primary", null, () => openProofModal(r), "Open video proof player");
      mkBtn("Edit", "quiet", ICON.edit, () => openEditMetadataModal(r), "Edit order, carrier, or notes");
      mkBtn("Show in Explorer", "quiet", ICON.folder, () => revealClipInExplorer(r), "Open this video file in Windows File Explorer");
      mkBtn("Delete", "danger", ICON.trash, () => openDeleteModal(r), "Delete this clip");

      const cb = tr.querySelector(".row-chk");
      if (checkedIds.has(String(r.id))) {
        cb.checked = true;
        tr.classList.add("sel");
      }
      cb.addEventListener("change", function () {
        tr.classList.toggle("sel", cb.checked);
        updateBulkDeleteButton();
      });

      tb.appendChild(tr);
    });

    const selAll = $("#selAll");
    if (selAll) {
      const allRows = $$(".row-chk", tb);
      selAll.checked = allRows.length > 0 && allRows.every(c => c.checked);
    }
    updateBulkDeleteButton();
  }

  window.toggleSelectAll = function (checked) {
    $$("#rows tr").forEach(function (tr) {
      const c = tr.querySelector("input.row-chk");
      if (c) {
        c.checked = checked;
        tr.classList.toggle("sel", checked);
      }
    });
    updateBulkDeleteButton();
  };

  function updateBulkDeleteButton() {
    const count = $$("#rows tr.sel").length;
    const btn = $("#bulkDeleteBtn");
    const label = $("#bulkDeleteCount");
    if (btn) btn.style.display = count > 0 ? "inline-flex" : "none";
    if (label) label.textContent = count;
  }

  window.handleBulkDownload = function () {
    window.exportEvidencePackage();
  };

  window.confirmBatchDelete = function () {
    const selRows = $$("#rows tr.sel");
    if (!selRows.length) return;
    pendingDeleteSession = "batch";
    const body = $("#dBody");
    if (body) body.textContent = `Permanently delete ${selRows.length} selected video proofs? This cannot be undone.`;
    const dlg = $("#dDelete");
    if (dlg) dlg.showModal();
  };

  function triggerClientBlobDownload(url, defaultFilename) {
    fetch(url)
      .then(r => r.blob())
      .then(blob => {
        const u = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = u;
        a.download = defaultFilename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(u);
        toast("ok", "Downloaded " + defaultFilename);
      })
      .catch(() => {
        toast("danger", "Failed to download export file.");
      });
  }

  window.exportDisputeCsv = async function () {
    try {
      toast("info", "Generating dispute CSV manifest...");
      const q = ($("#q") ? $("#q").value : "").trim();
      const res = await fetch("/api/sessions/export/csv/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: q })
      });
      const data = await res.json();
      if (data && data.success) {
        toast("ok", `Exported ${data.count} records to Downloads and highlighted in File Explorer.`);
      } else {
        triggerClientBlobDownload("/api/sessions/export/csv" + (q ? "?q=" + encodeURIComponent(q) : ""), "shipment_dispute_manifest.csv");
      }
    } catch (err) {
      triggerClientBlobDownload("/api/sessions/export/csv", "shipment_dispute_manifest.csv");
    }
  };

  window.exportEvidencePackage = async function () {
    const selRows = $$("#rows tr.sel");
    const sessionIds = [];
    selRows.forEach(tr => {
      if (tr.dataset.id) sessionIds.push(Number(tr.dataset.id));
    });
    const q = ($("#q") ? $("#q").value : "").trim();

    try {
      toast("info", sessionIds.length ? `Bundling ${sessionIds.length} video proofs and certificates into ZIP...` : "Bundling video proofs and certificates into ZIP...");
      const res = await fetch("/api/sessions/export/package/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_ids: sessionIds, q: q })
      });
      const data = await res.json();
      if (data && data.success) {
        toast("ok", `Evidence package saved to Downloads (${data.count} recordings) and opened in File Explorer.`);
      } else {
        toast("danger", "Failed to generate package: " + ((data && data.error) || "No recordings found"));
      }
    } catch (err) {
      toast("danger", "Failed to connect to export service.");
    }
  };

  // --- Windows Explorer Reveal Integrations ---
  window.revealClipInExplorer = async function (sessionOrId) {
    const id = typeof sessionOrId === "object" ? sessionOrId.id : sessionOrId;
    if (!id) {
      toast("warn", "No video clip selected to show in Explorer.");
      return;
    }
    try {
      toast("info", "Locating video in Windows Explorer...");
      const res = await fetch(`/api/sessions/${id}/reveal`, { method: "POST" });
      const data = await res.json();
      if (data && data.success) {
        if (data.revealed) {
          toast("ok", "Video clip highlighted in Windows Explorer.");
        } else {
          toast("ok", "Opened clips storage folder in Windows Explorer.");
        }
      } else {
        toast("danger", "Could not locate file: " + ((data && data.error) || "File not found"));
      }
    } catch (e) {
      toast("danger", "Failed to communicate with explorer service.");
    }
  };

  window.revealModalClipInExplorer = function () {
    if (currentModalSession && currentModalSession.id) {
      revealClipInExplorer(currentModalSession.id);
    } else {
      toast("warn", "No active video session to show in Explorer.");
    }
  };

  window.openClipsFolderInExplorer = async function () {
    try {
      toast("info", "Opening clips folder in Windows Explorer...");
      const res = await fetch("/api/clips/reveal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (data && data.success) {
        toast("ok", "Clips storage folder opened in Windows Explorer.");
      } else {
        toast("danger", "Could not open folder: " + ((data && data.error) || "Folder not found"));
      }
    } catch (e) {
      toast("danger", "Failed to communicate with explorer service.");
    }
  };

  // --- Video Proof Player Dialog ---
  const dPlayer = $("#dPlayer");
  const modalVideoPlayer = $("#modalVideoPlayer");
  let isPlaying = false;

  window.openProofModal = function (session) {
    currentModalSession = session;
    if (!session) return;

    if ($("#pTitle")) $("#pTitle").textContent = "Proof for " + (session.barcode || "PKG");
    if ($("#pCode")) $("#pCode").textContent = session.barcode || "PKG-UNKNOWN";
    if ($("#pOrder")) $("#pOrder").textContent = session.order_id || "Not assigned";
    if ($("#pCarrier")) $("#pCarrier").textContent = session.carrier || "Not assigned";
    if ($("#pAt")) $("#pAt").textContent = session.start_time ? session.start_time.replace("T", " ").slice(0, 19) : "---";
    if ($("#pDur")) $("#pDur").textContent = fmt(session.duration_seconds || 0);
    if ($("#pSize")) $("#pSize").textContent = formatBytes(session.file_size_bytes || 0);
    if ($("#pStation")) $("#pStation").textContent = session.station_id || "Station 1";
    
    const hash = session.sha256_hash || "";
    if ($("#pHash")) $("#pHash").textContent = hash || "Generating cryptographic hash...";
    if ($("#pHashShort")) {
      if (hash && hash.length >= 20) {
        $("#pHashShort").textContent = hash.slice(0, 10) + "..." + hash.slice(-10);
      } else {
        $("#pHashShort").textContent = hash || "Pending hash...";
      }
    }
    const fullHash = $("#pHash");
    const toggleBtn = $("#btnToggleFullHash");
    if (fullHash) fullHash.classList.remove("expanded");
    if (toggleBtn) toggleBtn.textContent = "Expand";

    const dl = $("#pDownload");
    if (dl && dl.tagName === "A") {
      const fn = session.clip_filename || (session.clip_path ? session.clip_path.split(/[/\\]/).pop() : (session.barcode + ".mp4"));
      dl.href = `/api/clips/download/${fn}`;
      dl.download = fn;
    }

    if (modalVideoPlayer) {
      modalVideoPlayer.src = `/api/sessions/${session.id}/video`;
      modalVideoPlayer.currentTime = 0;
      modalVideoPlayer.pause();
      isPlaying = false;
      updatePlayIcon();
      paintScrubber(0, session.duration_seconds || 1);
    }

    renderIcons();
    if (dPlayer) dPlayer.showModal();
  };

  window.closePlayerModal = function () {
    if (modalVideoPlayer) {
      try {
        modalVideoPlayer.pause();
      } catch (e) {}
      modalVideoPlayer.src = "";
    }
    if (dPlayer) dPlayer.close();
  };

  window.togglePlayPause = function () {
    if (!modalVideoPlayer) return;
    if (modalVideoPlayer.paused) {
      const p = modalVideoPlayer.play();
      if (p && typeof p.catch === "function") {
        p.catch(() => {});
      }
      isPlaying = true;
    } else {
      modalVideoPlayer.pause();
      isPlaying = false;
    }
    updatePlayIcon();
  };

  function updatePlayIcon() {
    const iconSpan = $("#pPlayIcon");
    if (iconSpan) iconSpan.innerHTML = isPlaying ? ICON.pause : ICON.play;
  }

  window.stepVideo = function (seconds) {
    if (!modalVideoPlayer) return;
    modalVideoPlayer.currentTime = Math.max(0, Math.min(modalVideoPlayer.duration || 9999, modalVideoPlayer.currentTime + seconds));
  };

  if (modalVideoPlayer) {
    modalVideoPlayer.addEventListener("timeupdate", function () {
      const cur = modalVideoPlayer.currentTime || 0;
      const dur = modalVideoPlayer.duration || (currentModalSession?.duration_seconds || 1);
      paintScrubber(cur, dur);
    });
    modalVideoPlayer.addEventListener("ended", function () {
      isPlaying = false;
      updatePlayIcon();
    });
  }

  function paintScrubber(cur, dur) {
    const p = Math.max(0, Math.min(100, (cur / dur) * 100));
    if ($("#sfill")) $("#sfill").style.width = p + "%";
    if ($("#sth")) $("#sth").style.left = p + "%";
    if ($("#pTime")) $("#pTime").textContent = fmt(cur) + " / " + fmt(dur);
  }

  const sbar = $("#sbar");
  if (sbar) {
    sbar.addEventListener("click", function (e) {
      if (!modalVideoPlayer || !modalVideoPlayer.duration) return;
      const r = this.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
      modalVideoPlayer.currentTime = pct * modalVideoPlayer.duration;
    });
  }

  window.toggleFullHashView = function () {
    const fullHash = $("#pHash");
    const toggleBtn = $("#btnToggleFullHash");
    if (!fullHash) return;
    const isExp = fullHash.classList.toggle("expanded");
    if (toggleBtn) toggleBtn.textContent = isExp ? "Collapse" : "Expand";
  };

  window.copyModalHash = function () {
    const hash = $("#pHash")?.textContent;
    if (hash && hash !== "---" && !hash.startsWith("Generating") && !hash.startsWith("Pending")) {
      navigator.clipboard.writeText(hash).then(() => {
        toast("ok", "Digital fingerprint copied to clipboard.");
        const btnText = $("#copyHashBtnText");
        if (btnText) {
          const orig = btnText.textContent;
          btnText.textContent = "Copied!";
          setTimeout(() => { btnText.textContent = orig; }, 2000);
        }
      }).catch(() => {
        toast("warn", "Could not copy hash to clipboard.");
      });
    }
  };

  // Keyboard navigation for video proof modal
  window.addEventListener("keydown", function (e) {
    if (dPlayer && dPlayer.open) {
      if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
      if (e.key === " " || e.code === "Space") {
        e.preventDefault();
        togglePlayPause();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        stepVideo(-0.04);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        stepVideo(0.04);
      } else if (e.key === "j" || e.key === "J") {
        e.preventDefault();
        stepVideo(-1.0);
      } else if (e.key === "l" || e.key === "L") {
        e.preventDefault();
        stepVideo(1.0);
      } else if (e.key === "k" || e.key === "K") {
        e.preventDefault();
        togglePlayPause();
      }
    }
  });

  window.handleModalDeleteClick = function () {
    if (!currentModalSession) return;
    closePlayerModal();
    openDeleteModal(currentModalSession);
  };

  window.handleModalEditClick = function () {
    if (!currentModalSession) return;
    closePlayerModal();
    openEditMetadataModal(currentModalSession);
  };

  // --- Edit Metadata Dialog ---
  const dEdit = $("#dEdit");
  window.openEditMetadataModal = function (session) {
    currentModalSession = session;
    if (!session || !dEdit) return;

    if ($("#editMetaSessionId")) $("#editMetaSessionId").value = session.id;
    if ($("#editMetaBarcode")) $("#editMetaBarcode").value = session.barcode || "";
    if ($("#editMetaOrderId")) $("#editMetaOrderId").value = session.order_id || "";
    if ($("#editMetaCarrier")) $("#editMetaCarrier").value = session.carrier || "";
    if ($("#editMetaNotes")) $("#editMetaNotes").value = session.notes || "";

    dEdit.showModal();
  };

  window.closeEditMetadataModal = function () {
    if (dEdit) dEdit.close();
  };

  window.saveSessionMetadata = async function () {
    const id = $("#editMetaSessionId")?.value;
    if (!id) return;

    const payload = {
      barcode: $("#editMetaBarcode")?.value.trim(),
      order_id: $("#editMetaOrderId")?.value.trim(),
      carrier: $("#editMetaCarrier")?.value.trim(),
      notes: $("#editMetaNotes")?.value.trim()
    };

    try {
      const resp = await fetch(`/api/sessions/${id}/metadata`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (data.success) {
        toast("ok", "Metadata updated for " + payload.barcode);
        closeEditMetadataModal();
        loadSessions();
      } else {
        toast("warn", data.error || "Update failed");
      }
    } catch (e) {
      toast("danger", "Connection error saving metadata.");
    }
  };

  // --- Delete Dialog ---
  const dDelete = $("#dDelete");
  window.openDeleteModal = function (session) {
    pendingDeleteSession = session;
    if (!session || !dDelete) return;

    if ($("#dTitle")) $("#dTitle").textContent = "Delete clip " + session.barcode + "?";
    if ($("#dBody")) $("#dBody").textContent = `Clip ${session.barcode} (${session.order_id || "ORD-" + session.id}) will be removed from the archive. This cannot be undone.`;

    dDelete.showModal();
  };

  window.closeDeleteModal = function () {
    pendingDeleteSession = null;
    if (dDelete) dDelete.close();
  };

  window.executeSessionDeletion = async function () {
    if (!pendingDeleteSession) return;

    if (pendingDeleteSession === "batch") {
      const selRows = $$("#rows tr.sel");
      for (const tr of selRows) {
        const id = tr.dataset.id;
        try {
          await fetch(`/api/sessions/${id}/delete`, { method: "POST" });
        } catch (e) {}
      }
      playChime("delete");
      toast("danger", "Selected clips deleted.");
      closeDeleteModal();
      loadSessions();
      return;
    }

    try {
      const resp = await fetch(`/api/sessions/${pendingDeleteSession.id}/delete`, { method: "POST" });
      const data = await resp.json();
      if (data.success) {
        playChime("delete");
        toast("danger", `Clip ${pendingDeleteSession.barcode} deleted.`);
        closeDeleteModal();
        loadSessions();
      } else {
        toast("warn", data.error || "Delete failed");
      }
    } catch (e) {
      toast("danger", "Connection error during deletion.");
    }
  };

  // --- Finish Barcode / QR Placard Dialog ---
  const printModal = $("#printBarcodeModal");
  window.openPrintBarcodeModal = function () {
    if (printModal) printModal.showModal();
  };

  window.closePrintBarcodeModal = function () {
    if (printModal) printModal.close();
  };

  window.printBenchPlacard = function () {
    window.print();
  };

  window.openClipsFolder = async function () {
    try {
      const resp = await fetch("/api/open_folder", { method: "POST" });
      if (resp.ok) {
        toast("ok", "Clips folder opened in Windows Explorer.");
      } else {
        toast("warn", "Could not open folder.");
      }
    } catch (e) {
      toast("danger", "Failed to trigger folder opening.");
    }
  };

  // --- Hardware & RTSP Configuration ---
  function parseRtspToInputs(url) {
    if (!url || !url.toLowerCase().startsWith("rtsp://")) return;
    try {
      const remainder = url.slice(7);
      const slashIdx = remainder.indexOf("/");
      const authority = slashIdx >= 0 ? remainder.slice(0, slashIdx) : remainder;
      const path = slashIdx >= 0 ? remainder.slice(slashIdx) : "/Streaming/Channels/101";

      let userinfo = "";
      let hostport = authority;
      const atIdx = authority.lastIndexOf("@");
      if (atIdx >= 0) {
        userinfo = authority.slice(0, atIdx);
        hostport = authority.slice(atIdx + 1);
      }

      let u = "", p = "";
      if (userinfo) {
        const colonIdx = userinfo.indexOf(":");
        if (colonIdx >= 0) {
          u = decodeURIComponent(userinfo.slice(0, colonIdx));
          p = decodeURIComponent(userinfo.slice(colonIdx + 1));
        } else {
          u = decodeURIComponent(userinfo);
        }
      }

      let h = hostport, pt = "554";
      const hpColon = hostport.lastIndexOf(":");
      if (hpColon >= 0) {
        h = hostport.slice(0, hpColon);
        pt = hostport.slice(hpColon + 1);
      }

      if ($("#rtspIpInput")) $("#rtspIpInput").value = h;
      if ($("#rtspPortInput")) $("#rtspPortInput").value = pt;
      if ($("#rtspUserInput")) $("#rtspUserInput").value = u;
      if ($("#rtspPassInput")) $("#rtspPassInput").value = p;
      if ($("#rtspChannelSelect")) {
        let matched = false;
        Array.from($("#rtspChannelSelect").options).forEach(opt => {
          if (opt.value === path) {
            $("#rtspChannelSelect").value = path;
            matched = true;
          }
        });
        if (!matched && path) {
          const opt = new Option(path, path, true, true);
          $("#rtspChannelSelect").add(opt);
        }
      }
    } catch (e) {
      console.warn("Could not parse RTSP URL to inputs:", e);
    }
  }

  window.syncRtspBuilder = function () {
    const ip = $("#rtspIpInput")?.value.trim() || "192.168.0.250";
    const port = $("#rtspPortInput")?.value.trim() || "554";
    const ch = $("#rtspChannelSelect")?.value.trim() || "/Streaming/Channels/101";
    const user = $("#rtspUserInput")?.value.trim() || "admin";
    const pass = $("#rtspPassInput")?.value.trim() || "";

    const userPart = user ? (encodeURIComponent(user) + (pass ? ":" + encodeURIComponent(pass) : "") + "@") : "";
    const url = `rtsp://${userPart}${ip}:${port}${ch.startsWith('/') ? ch : '/' + ch}`;
    if ($("#rtspUrlInput")) $("#rtspUrlInput").value = url;
  };

  window.setConfigCameraSource = function (source) {
    const isRtsp = source === "rtsp" || source.startsWith("rtsp://");
    $("#radioSourceRtsp")?.setAttribute("aria-pressed", isRtsp);
    $("#radioSourceWebcam")?.setAttribute("aria-pressed", !isRtsp);
  };

  window.scanAvailableCameras = async function () {
    const btn = $("#scanCamerasBtn");
    const sel = $("#detectedCamerasSelect");
    if (btn) btn.textContent = "Scanning hardware...";
    try {
      const resp = await fetch("/api/camera/devices");
      const data = await resp.json();
      if (btn) btn.innerHTML = '<span data-i="search"></span> Scan Connected Cameras';
      if (data && data.success && sel) {
        sel.innerHTML = '<option value="">-- Choose Detected Camera --</option>';
        (data.devices || []).forEach(dev => {
          const opt = document.createElement("option");
          opt.value = dev.id;
          opt.textContent = `${dev.name} [${dev.resolution || 'Auto'}] (${dev.status || 'ready'})`;
          if (dev.id === data.current_source) opt.selected = true;
          sel.appendChild(opt);
        });
        toast("ok", `Discovered ${data.devices.length} camera source(s)`);
      }
    } catch (e) {
      if (btn) btn.innerHTML = '<span data-i="search"></span> Scan Connected Cameras';
      toast("warn", "Camera scan query failed.");
    }
  };

  window.selectDetectedCamera = function (val) {
    if (!val) return;
    if (val === "rtsp" || val.startsWith("rtsp://")) {
      setConfigCameraSource("rtsp");
    } else {
      setConfigCameraSource(val);
    }
  };

  window.testCameraConnection = async function () {
    const resBox = $("#rtspTestResult");
    if (resBox) {
      resBox.textContent = "Testing camera connection...";
      resBox.style.color = "var(--ink-2)";
    }

    const isRtsp = ($("#radioSourceRtsp")?.getAttribute("aria-pressed") === "true") ||
                   ($("#srcRtspBtn")?.getAttribute("aria-pressed") === "true");
    const rtspUrl = $("#rtspUrlInput")?.value.trim() || "";
    const targetSource = isRtsp ? (rtspUrl || "rtsp") : "webcam:0";

    try {
      const resp = await fetch("/api/camera/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: targetSource })
      });
      const data = await resp.json();
      if (data && data.success) {
        if (resBox) {
          resBox.textContent = `Connected! ${data.message || 'Stream reachable'} (${data.latency_ms || 0}ms)`;
          resBox.style.color = "var(--pallet-ink)";
        }
        toast("ok", "Camera connection verified (" + (data.latency_ms || 0) + "ms)");
        const img = $("#liveStream");
        if (img) img.src = "/api/camera/stream?t=" + Date.now();
        handleStreamLoaded();
      } else {
        if (resBox) {
          resBox.textContent = data.message || data.error || "Stream offline or unreachable.";
          resBox.style.color = "var(--coch-text)";
        }
        toast("warn", data.message || "Camera stream test failed.");
      }
    } catch (e) {
      if (resBox) {
        resBox.textContent = "Connection error.";
        resBox.style.color = "var(--coch-text)";
      }
      toast("danger", "Network error probing camera.");
    }
  };

  window.saveSettings = async function () {
    const isRtsp = $("#radioSourceRtsp")?.getAttribute("aria-pressed") === "true";
    const rtspUrl = $("#rtspUrlInput")?.value.trim();
    const source = isRtsp ? (rtspUrl || "rtsp") : "webcam:0";
    const stationId = $("#stationIdInput")?.value.trim() || "Station 1";
    const timeout = parseInt($("#timeoutInput")?.value) || 300;
    const clipsDir = $("#clipsDirInput")?.value.trim();

    const updateSource = $("#updateSourceInput")?.value?.trim() || $("#manifestUrlInput")?.value?.trim() || "Guts1005/provenance";

    const payload = {
      camera_source: isRtsp ? "rtsp" : "webcam:0",
      rtsp_url: rtspUrl,
      station_id: stationId,
      idle_timeout_seconds: timeout,
      clips_dir: clipsDir,
      update_manifest_url: updateSource
    };

    try {
      const resp = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (data.success) {
        // Also immediately notify camera source switcher
        await fetch("/api/camera/source", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source: source })
        });
        toast("ok", "Configuration saved & applied.");
      } else {
        toast("warn", data.error || "Save failed");
      }
    } catch (e) {
      toast("danger", "Connection error saving configuration.");
    }
  };

  // --- Enterprise Auto-Updater Client Engine ---
  let updateDownloadInterval = null;

  window.renderUpdateStatusUI = async function renderUpdateStatusUI(statusData) {
    if (!statusData) return;
    const curVer = statusData.current_version || "2.0.7";
    if ($("#updateVersionBadge")) {
      $("#updateVersionBadge").textContent = "Current: v" + curVer;
    }

    const title = $("#updateStatusTitle");
    const detail = $("#updateStatusDetail");
    const availBox = $("#updateAvailableBox");
    const readyBox = $("#updateReadyBox");
    const progWrap = $("#updateProgressWrap");
    const dlBtn = $("#downloadUpdateBtn");
    const checkingBar = $("#updateCheckingBar");
    const tabBadge = $("#tabSettingsUpdateBadge");
    const stationBanner = $("#stationUpdateBanner");
    const bannerTag = $("#bannerNewVersionTag");

    if (statusData.status === "checking") {
      if (title) title.textContent = "Checking for Updates...";
      if (detail) detail.textContent = "Connecting to release server...";
      if (checkingBar) checkingBar.style.display = "block";
      return;
    } else {
      if (checkingBar) checkingBar.style.display = "none";
    }

    if (statusData.status === "offline") {
      if (title) title.textContent = "Station Offline / Source Unreachable";
      if (detail) detail.textContent = statusData.last_error || statusData.error || "No active internet connection. Air-gapped packing remains active.";
      if (availBox) availBox.style.display = "none";
      if (readyBox) readyBox.style.display = "none";
      if (progWrap) progWrap.style.display = "none";
      if (tabBadge) tabBadge.style.display = "none";
      if (stationBanner) stationBanner.style.display = "none";
      return;
    }

    if (statusData.status === "error") {
      if (title) title.textContent = "Update Check Failed";
      if (detail) detail.textContent = statusData.last_error || statusData.error || "Could not reach update server.";
      if (availBox) availBox.style.display = "none";
      if (readyBox) readyBox.style.display = "none";
      if (progWrap) progWrap.style.display = "none";
      if (tabBadge) tabBadge.style.display = "none";
      if (stationBanner) stationBanner.style.display = "none";
      return;
    }

    if (statusData.status === "ready_to_install") {
      const v = statusData.latest_version || "";
      if (title) title.textContent = "Update Ready to Install (v" + v + ")";
      if (detail) detail.textContent = "Verified cryptographic signature. Ready to restart.";
      if (availBox) availBox.style.display = "block";
      if (readyBox) readyBox.style.display = "flex";
      if (progWrap) progWrap.style.display = "none";
      if (dlBtn) dlBtn.style.display = "none";

      if (tabBadge) {
        tabBadge.textContent = "Ready: v" + v;
        tabBadge.style.display = "inline-flex";
      }
      if (stationBanner) {
        stationBanner.style.display = "flex";
        if (bannerTag) bannerTag.textContent = "v" + v + " (Ready to install)";
      }
      return;
    }

    if (statusData.is_downloading || statusData.status === "downloading") {
      const v = statusData.latest_version || "";
      if (title) title.textContent = "Downloading Update v" + v;
      if (detail) detail.textContent = "Streaming installer in background...";
      if (availBox) availBox.style.display = "block";
      if (progWrap) progWrap.style.display = "block";
      if (readyBox) readyBox.style.display = "none";
      if (dlBtn) dlBtn.style.display = "none";

      const pct = statusData.download_percent || 0;
      if ($("#updateProgressBar")) $("#updateProgressBar").style.width = pct + "%";
      if ($("#updateProgressPct")) $("#updateProgressPct").textContent = pct + "%";
      const mbDone = (Number(statusData.downloaded_bytes || 0) / 1048576).toFixed(1);
      const mbTot = (Number(statusData.download_size_bytes || 0) / 1048576).toFixed(1);
      if ($("#updateProgressLabel")) {
        $("#updateProgressLabel").textContent = "Downloading installer: " + mbDone + " MB / " + (mbTot > 0 ? mbTot + " MB" : "...");
      }

      if (tabBadge) {
        tabBadge.textContent = pct + "%";
        tabBadge.style.display = "inline-flex";
      }
      if (stationBanner) {
        stationBanner.style.display = "flex";
        if (bannerTag) bannerTag.textContent = "Downloading v" + v + " (" + pct + "%)";
      }
      return;
    }

    if (statusData.update_available) {
      const v = statusData.latest_version || "";
      if (title) title.textContent = "Update Available: v" + v;
      if (detail) detail.textContent = "A newer version of Provenance is ready for installation.";
      if (availBox) availBox.style.display = "block";
      if ($("#newVersionTag")) $("#newVersionTag").textContent = "v" + v;
      if ($("#newVersionDate")) $("#newVersionDate").textContent = statusData.release_date ? "Released " + statusData.release_date : "";
      if ($("#newVersionSize")) {
        const mb = (Number(statusData.download_size_bytes || 0) / 1048576).toFixed(1);
        $("#newVersionSize").textContent = "Package Size: " + (mb > 0 ? mb + " MB" : "Standard Setup");
      }

      const notesList = $("#updateReleaseNotesList");
      if (notesList) {
        notesList.innerHTML = "";
        const notes = statusData.release_notes || [];
        if (notes.length === 0) {
          notesList.innerHTML = "<li>Performance improvements and station stability fixes.</li>";
        } else {
          notes.forEach(note => {
            const li = document.createElement("li");
            li.textContent = note;
            notesList.appendChild(li);
          });
        }
      }

      if (readyBox) readyBox.style.display = "none";
      if (progWrap) progWrap.style.display = "none";
      if (dlBtn) dlBtn.style.display = "inline-flex";

      if (tabBadge) {
        tabBadge.textContent = "v" + v;
        tabBadge.style.display = "inline-flex";
      }
      if (stationBanner) {
        stationBanner.style.display = "flex";
        if (bannerTag) bannerTag.textContent = "v" + v;
      }
    } else {
      if (title) title.textContent = "System Up To Date";
      if (detail) detail.textContent = "Running version v" + curVer + ". Station is running latest release.";
      if (availBox) availBox.style.display = "none";
      if (readyBox) readyBox.style.display = "none";
      if (progWrap) progWrap.style.display = "none";
      if (tabBadge) tabBadge.style.display = "none";
      if (stationBanner) stationBanner.style.display = "none";
    }
  };

  window.triggerUpdateCheck = async function (opts) {
    const silent = Boolean(opts && opts.silent);
    const btn = $("#checkUpdateBtn");
    const checkingBar = $("#updateCheckingBar");
    const title = $("#updateStatusTitle");
    const detail = $("#updateStatusDetail");

    if (btn && !silent) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spin-anim" style="margin-right:6px"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg></span> Checking for updates...';
    }
    if (checkingBar) checkingBar.style.display = "block";
    if (!silent) {
      if (title) title.textContent = "Checking for Updates...";
      if (detail) detail.textContent = "Connecting to release server feed...";
    }

    const manifestUrl = $("#manifestUrlInput")?.value?.trim() || "Guts1005/provenance";

    try {
      const resp = await fetch("/api/updates/check?sync=1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ manifest_url: manifestUrl })
      });
      const data = await resp.json();
      renderUpdateStatusUI(data);

      if (!silent) {
        if (data.status === "offline") {
          toast("info", data.last_error || data.error || "Station is offline. Air-gapped packing continues smoothly.");
        } else if (data.update_available) {
          toast("ok", "New update v" + data.latest_version + " discovered!");
        } else if (data.status === "error") {
          toast("warn", data.last_error || data.error || "Could not reach update server.");
        } else {
          toast("ok", "Station software is completely up to date (v" + data.current_version + ").");
        }
      } else {
        if (data.update_available) {
          toast("ok", "Software update v" + data.latest_version + " is available!");
        }
      }
    } catch (e) {
      if (!silent) {
        toast("warn", "Network check failed. System operating offline.");
      }
      if (title && !silent) title.textContent = "Station Offline";
      if (detail && !silent) detail.textContent = "Air-gapped mode active.";
    } finally {
      if (checkingBar) checkingBar.style.display = "none";
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span data-i="refresh"></span> Check for Updates';
        renderIcons();
      }
    }
  };

  window.startUpdateDownload = async function () {
    const dlBtn = $("#downloadUpdateBtn");
    if (dlBtn) dlBtn.disabled = true;
    const progWrap = $("#updateProgressWrap");
    if (progWrap) progWrap.style.display = "block";

    try {
      const resp = await fetch("/api/updates/download", { method: "POST" });
      const data = await resp.json();
      renderUpdateStatusUI(data);
      toast("ok", "Update download started in background.");

      if (updateDownloadInterval) clearInterval(updateDownloadInterval);
      updateDownloadInterval = setInterval(async () => {
        try {
          const stResp = await fetch("/api/updates/status");
          if (stResp.ok) {
            const st = await stResp.json();
            renderUpdateStatusUI(st);
            if (st.status === "ready_to_install" || st.status === "error") {
              clearInterval(updateDownloadInterval);
              updateDownloadInterval = null;
              if (st.status === "ready_to_install") {
                toast("ok", "Update v" + st.latest_version + " downloaded and verified!");
              } else if (st.last_error) {
                toast("danger", "Download failed: " + st.last_error);
              }
            }
          }
        } catch (err) {}
      }, 500);

    } catch (e) {
      toast("danger", "Failed to initiate update download.");
      if (dlBtn) dlBtn.disabled = false;
    }
  };

  window.confirmApplyUpdate = async function () {
    if (appState === "recording") {
      toast("warn", "Cannot update while a parcel is actively recording. Finish recording first.");
      return;
    }

    if (!confirm("Provenance will now close, install the update, and restart. Proceed?")) {
      return;
    }

    try {
      const resp = await fetch("/api/updates/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ silent: true })
      });
      const data = await resp.json();
      if (data.success) {
        toast("ok", "Update installer launched. Restarting application...");
        setTimeout(() => {
          document.body.innerHTML = '<div style="display:flex;height:100vh;align-items:center;justify-content:center;background:#0d0e10;color:#fff;font-family:sans-serif;text-align:center"><div><h2>Applying Software Update</h2><p style="color:#94a3b8;margin-top:8px">Provenance is restarting with the latest release. Please wait...</p></div></div>';
        }, 1000);
      } else {
        toast("danger", data.error || "Update execution was blocked.");
      }
    } catch (e) {
      toast("danger", "Could not trigger update installation.");
    }
  };

  window.saveUpdateSettings = async function () {
    const manifestUrl = $("#updateSourceInput")?.value?.trim() || $("#manifestUrlInput")?.value?.trim() || "";
    try {
      await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ update_manifest_url: manifestUrl })
      });
      toast("ok", "Update feed configuration saved.");
    } catch (e) {}
  };

  window.saveUpdateSourceSettings = async function () {
    const source = $("#updateSourceInput")?.value?.trim() || "";
    if ($("#manifestUrlInput")) $("#manifestUrlInput").value = source;
    try {
      const resp = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ update_manifest_url: source })
      });
      const data = await resp.json();
      if (data.success) {
        toast("ok", "Update source configuration saved.");
      } else {
        toast("warn", data.error || "Save failed.");
      }
    } catch (e) {
      toast("danger", "Connection error saving update source.");
    }
  };

  async function loadSettings() {
    try {
      const resp = await fetch("/api/config");
      if (resp.ok) {
        const conf = await resp.json();
        if ($("#stationIdInput")) $("#stationIdInput").value = conf.station_id || "Station 1";
        if ($("#timeoutInput")) $("#timeoutInput").value = conf.idle_timeout_seconds || 300;
        if ($("#clipsDirInput")) $("#clipsDirInput").value = conf.clips_dir || "";
        if ($("#rtspUrlInput")) $("#rtspUrlInput").value = conf.rtsp_url || "";
        if ($("#manifestUrlInput")) $("#manifestUrlInput").value = conf.update_manifest_url || "Guts1005/provenance";

        parseRtspToInputs(conf.rtsp_url);

        const isRtsp = conf.camera_source === "rtsp" || (conf.camera_source && conf.camera_source.startsWith("rtsp://"));
        setConfigCameraSource(isRtsp ? "rtsp" : "webcam:0");
        scanAvailableCameras();

        // Auto-check for updates on launch
        if (conf.auto_check_updates !== "0") {
          setTimeout(() => {
            triggerUpdateCheck({ silent: true });
          }, 300);
        } else {
          try {
            const updResp = await fetch("/api/updates/status");
            if (updResp.ok) {
              const updData = await updResp.json();
              renderUpdateStatusUI(updData);
            }
          } catch (uErr) {}
        }
      }
    } catch (e) {
      console.warn("Could not load config:", e);
    }
  }

  window.navigateToUpdates = function () {
    switchView("settings");
    setTimeout(() => {
      const panel = document.getElementById("updatePanel");
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth" });
      }
    }, 120);
  };

  // --- Real-time Polling Engine ---
  function startStatusPolling() {
    let pollCount = 0;
    let lastKnownSessionId = null;
    let lastKnownSessionCount = null;
    let wasRecording = false;

    async function poll() {
      pollCount++;
      try {
        const resp = await fetch("/api/status");
        if (resp.ok) {
          const data = await resp.json();

          // Real-time Session & Manifest Synchronization
          const curSessionId = data.latest_session_id != null ? data.latest_session_id : null;
          const curCount = data.completed_sessions_count != null ? data.completed_sessions_count : null;

          if (curSessionId !== null && curCount !== null) {
            if (lastKnownSessionId === null) {
              lastKnownSessionId = curSessionId;
              lastKnownSessionCount = curCount;
            } else if (curSessionId !== lastKnownSessionId || curCount !== lastKnownSessionCount) {
              lastKnownSessionId = curSessionId;
              lastKnownSessionCount = curCount;
              loadSessions();
              loadManifestProgressOnly();
              const curTab = $(".tab[aria-selected='true']");
              if (curTab && curTab.dataset.view === "manifest") {
                loadManifestData();
              }
            }
          }

          // Real-time Update Telemetry
          if (data.update) {
            renderUpdateStatusUI(data.update);
          }

          // Periodic fallback check against updater status
          if (pollCount % 4 === 0) {
            try {
              const updResp = await fetch("/api/updates/status");
              if (updResp.ok) {
                const updData = await updResp.json();
                renderUpdateStatusUI(updData);
              }
            } catch (u) {}
          }

          // Camera Telemetry
          if (data.camera) {
            const fps = Number(data.camera.fps ?? data.camera.actual_fps ?? 0);
            const isOk = Boolean(data.camera.is_connected);
            if ($("#teleDot")) $("#teleDot").style.background = isOk ? "var(--pallet-text)" : "var(--coch-text)";
            if ($("#teleRes")) $("#teleRes").textContent = data.camera.resolution || "1920x1080";
            if ($("#teleFps")) $("#teleFps").textContent = fps.toFixed(1) + " fps";
            const teleLag = $("#teleLag");
            if (teleLag) {
              if (!isOk) {
                teleLag.textContent = "Offline";
                teleLag.style.color = "#ef4444";
              } else {
                const lagStatus = data.camera.lag_status || "OPTIMAL";
                const latMs = Math.round(Number(data.camera.latency_ms || 35));
                if (lagStatus === "OPTIMAL") {
                  teleLag.textContent = "Lag: <40ms";
                  teleLag.style.color = "#22c55e";
                } else if (lagStatus === "ACCEPTABLE") {
                  teleLag.textContent = `Lag: ${latMs}ms`;
                  teleLag.style.color = "#eab308";
                } else {
                  teleLag.textContent = `Lag: ${latMs}ms`;
                  teleLag.style.color = "#ef4444";
                }
              }
            }
          }

          // Recording sync has absolute priority over idle/offline
          if (data.recording && data.active_session) {
            wasRecording = true;
            if (appState !== "recording") {
              activeSession = data.active_session;
              setStationState("recording", activeSession.barcode);
            }
          } else {
            if (appState === "recording" || wasRecording) {
              wasRecording = false;
              setStationState("idle");
              // Recording just ended, immediately fetch updated clips & manifest
              loadSessions();
              loadManifestProgressOnly();
              setTimeout(loadSessions, 500);
              setTimeout(loadSessions, 1500);
            } else if (data.camera) {
              const isOk = Boolean(data.camera.is_connected);
              if (isOk && appState === "offline") {
                setStationState("idle");
                const img = $("#liveStream");
                if (img) img.src = "/api/camera/stream?t=" + Date.now();
              } else if (!isOk && appState === "idle") {
                setStationState("offline");
              }
            }
          }
        }
      } catch (e) {
        // network hiccup
      }
    }

    statusPollInterval = setInterval(poll, 1500);
    poll();
  }

  // --- Initialization ---
  document.addEventListener("DOMContentLoaded", function () {
    renderIcons();
    initKioskHardening();
    initAudio();
    preloadAudio();
    initTheme();
    setupBarcodeInput();
    loadSettings();
    loadSessions();
    loadManifestProgressOnly();
    startStatusPolling();
  });

})();
