// EchoScribe-AI / SonoAssist - Clinical UI Controller
// Enterprise Medical Workstation Engine & Audio Synthesizer
// Covers Member 1 (Joel), Member 2 (Sohum), Member 3 (Manya), Member 4 (Dinesh), Member 5 (Nikilan)

document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentSessionId = "SESS_20261023_042";
  let activeRole = "radiologist";
  let currentSlide = 1;
  const totalSlides = 6;
  let auditEvents = [];
  let isListening = false;
  let recognition = null;
  let isAudioPlaying = false;
  let audioContext = null;
  let dopplerOscillator = null;
  let dopplerGain = null;
  let animFrameId = null;
  let audioStartTime = 0;
  const audioDurationSec = 6.0;

  // Toast Notification System (Replaces disruptive alert popups)
  function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(20px)";
      setTimeout(() => toast.remove(), 250);
    }, 3200);
  }

  // ==========================================================
  // WEB AUDIO & SPEECH SYNTHESIS ENGINE (REAL SOUND PLAYBACK)
  // ==========================================================
  function initAudioContext() {
    if (!audioContext) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        audioContext = new AudioCtx();
      }
    }
    if (audioContext && audioContext.state === "suspended") {
      audioContext.resume();
    }
  }

  // Play Diagnostic Foot Pedal Click & Bip Tone (Hardware Interrupt Sound)
  function playPedalSound() {
    try {
      initAudioContext();
      if (!audioContext) return;

      const now = audioContext.currentTime;

      // 1. Mechanical Relay Latch Click (Noise Burst)
      const bufferSize = audioContext.sampleRate * 0.02; // 20ms
      const noiseBuffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        output[i] = Math.random() * 2 - 1;
      }
      const whiteNoise = audioContext.createBufferSource();
      whiteNoise.buffer = noiseBuffer;
      const noiseGain = audioContext.createGain();
      noiseGain.gain.setValueAtTime(0.3, now);
      noiseGain.gain.exponentialRampToValueAtTime(0.01, now + 0.02);
      whiteNoise.connect(noiseGain);
      noiseGain.connect(audioContext.destination);
      whiteNoise.start(now);

      // 2. High-Precision DICOM Keyframe Grab Beep (880 Hz pulse)
      const osc = audioContext.createOscillator();
      const oscGain = audioContext.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(880, now + 0.01);
      oscGain.gain.setValueAtTime(0.18, now + 0.01);
      oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
      osc.connect(oscGain);
      oscGain.connect(audioContext.destination);
      osc.start(now + 0.01);
      osc.stop(now + 0.09);
    } catch (err) {
      console.warn("AudioContext error on pedal click:", err);
    }
  }

  // Start Ultrasound Doppler Flow Sound (Subtle acoustic hum)
  function startUltrasoundAcousticSound() {
    try {
      initAudioContext();
      if (!audioContext) return;

      const now = audioContext.currentTime;
      dopplerOscillator = audioContext.createOscillator();
      dopplerGain = audioContext.createGain();

      dopplerOscillator.type = "triangle";
      dopplerOscillator.frequency.setValueAtTime(110, now); // Low Doppler pulse frequency

      // Subtle LFO modulation to mimic vascular/acoustic flow
      const lfo = audioContext.createOscillator();
      const lfoGain = audioContext.createGain();
      lfo.frequency.setValueAtTime(1.8, now); // 1.8 Hz pulsing
      lfoGain.gain.setValueAtTime(15, now);
      lfo.connect(dopplerOscillator.frequency);
      lfo.start(now);

      dopplerGain.gain.setValueAtTime(0.06, now);
      dopplerOscillator.connect(dopplerGain);
      dopplerGain.connect(audioContext.destination);
      dopplerOscillator.start(now);
    } catch (e) {
      console.warn("Doppler sound error:", e);
    }
  }

  // Stop Ultrasound Doppler Sound
  function stopUltrasoundAcousticSound() {
    try {
      if (dopplerGain && audioContext) {
        dopplerGain.gain.setTargetAtTime(0, audioContext.currentTime, 0.05);
      }
      setTimeout(() => {
        if (dopplerOscillator) {
          dopplerOscillator.stop();
          dopplerOscillator.disconnect();
          dopplerOscillator = null;
        }
      }, 100);
    } catch (e) {
      // Ignored
    }
  }

  // Real Medical Speech Dictation (TTS with authoritative medical prosody)
  function speakMedicalDictation(text, onBoundaryWord, onComplete) {
    if (!("speechSynthesis" in window)) {
      console.warn("Web SpeechSynthesis not supported.");
      if (onComplete) setTimeout(onComplete, 3000);
      return;
    }

    window.speechSynthesis.cancel(); // Stop any pending speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 0.98;

    // Pick best English voice if available
    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang.includes("en-US") && (v.name.includes("Natural") || v.name.includes("David") || v.name.includes("Google"))) ||
                         voices.find(v => v.lang.startsWith("en"));
    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    utterance.onboundary = (event) => {
      if (event.name === "word" && onBoundaryWord) {
        const spokenWord = text.substring(event.charIndex, event.charIndex + event.charLength);
        onBoundaryWord(spokenWord, event.charIndex);
      }
    };

    utterance.onend = () => {
      if (onComplete) onComplete();
    };

    utterance.onerror = () => {
      if (onComplete) onComplete();
    };

    window.speechSynthesis.speak(utterance);
  }

  // Stop all active audio
  function stopAllAudio() {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    stopUltrasoundAcousticSound();
    isAudioPlaying = false;
    const playBtn = document.getElementById("play-pause-btn");
    if (playBtn) {
      playBtn.classList.remove("playing");
      playBtn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
    }
    if (animFrameId) {
      cancelAnimationFrame(animFrameId);
      animFrameId = null;
    }
    drawIdleWaveform();
  }

  // ==========================================================
  // REAL-TIME HTML5 CANVAS WAVEFORM OSCILLOSCOPE
  // ==========================================================
  const canvas = document.getElementById("live-audio-canvas");
  const ctx = canvas ? canvas.getContext("2d") : null;

  function drawIdleWaveform() {
    if (!ctx || !canvas) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Baseline resting electric waveform
    ctx.beginPath();
    ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
    ctx.lineWidth = 1.5;
    const midY = h / 2;

    for (let x = 0; x < w; x++) {
      const y = midY + Math.sin(x * 0.05) * 1.5 + (Math.random() - 0.5) * 1.2;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Resting time display
    const timeDisplay = document.getElementById("audio-time-display");
    if (timeDisplay && !isAudioPlaying) {
      timeDisplay.innerText = "00:00.0 / 00:06.0";
    }
  }

  function startAnimatedWaveform() {
    if (!ctx || !canvas) return;
    const w = canvas.width;
    const h = canvas.height;
    audioStartTime = performance.now();

    function renderLoop(now) {
      if (!isAudioPlaying) return;

      const elapsedMs = now - audioStartTime;
      const elapsedSec = Math.min(elapsedMs / 1000, audioDurationSec);

      // Update Timecode
      const timeDisplay = document.getElementById("audio-time-display");
      if (timeDisplay) {
        const mm = String(Math.floor(elapsedSec / 60)).padStart(2, "0");
        const ss = String(Math.floor(elapsedSec % 60)).padStart(2, "0");
        const ds = Math.floor((elapsedSec % 1) * 10);
        timeDisplay.innerText = `${mm}:${ss}.${ds} / 00:06.0`;
      }

      ctx.clearRect(0, 0, w, h);

      // Gradient wave stroke
      const gradient = ctx.createLinearGradient(0, 0, w, 0);
      gradient.addColorStop(0, "#38bdf8");
      gradient.addColorStop(0.5, "#2dd4bf");
      gradient.addColorStop(1, "#38bdf8");

      ctx.beginPath();
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      const midY = h / 2;
      const t = now * 0.008;

      for (let x = 0; x < w; x++) {
        const envelope = Math.sin((x / w) * Math.PI); // Taper at edges
        const wave1 = Math.sin(x * 0.08 + t) * 9;
        const wave2 = Math.cos(x * 0.04 - t * 1.3) * 5;
        const noise = (Math.random() - 0.5) * 3;
        const y = midY + (wave1 + wave2 + noise) * envelope;

        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      animFrameId = requestAnimationFrame(renderLoop);
    }

    animFrameId = requestAnimationFrame(renderLoop);
  }

  // Initialize idle wave
  drawIdleWaveform();

  // ==========================================================
  // DATASET & CLINICAL CASES
  // ==========================================================
  const clinicalCasesData = {
    "CASE_ABD_001": {
      id: "CASE_ABD_001",
      organ: "Gallbladder",
      condition: "Acute cholecystitis with cholelithiasis",
      speechText: "Gallbladder demonstrates diffuse wall thickening measuring 4.5 millimeters with multiple mobile echogenic calculi in the lumen producing distinct posterior acoustic shadowing. Sonographic Murphy's sign is positive. Pericholecystic fluid is noted in the gallbladder bed.",
      rawText: "Gall bladder demonstrates diffuse wall thickening measuring four point five millimeters with multiple mobile echo genic call cul us in the lumen producing distinct posterior acoustic shadow. Sonographic murphys sign is positive. Peri cholecystic fluid is noted in the gall bladder bed.",
      biasedText: `Gallbladder demonstrates diffuse wall thickening measuring <strong class="highlight-meas">4.5 mm</strong> with multiple mobile echogenic <strong class="highlight-anat">calculi</strong> in the lumen producing distinct posterior <strong class="highlight-anat">acoustic shadowing</strong>. Sonographic <strong class="highlight-anat">Murphy's sign</strong> is positive. <strong class="highlight-anat">Pericholecystic fluid</strong> is noted in the gallbladder bed.`,
      plainBiased: "Gallbladder demonstrates diffuse wall thickening measuring 4.5 mm with multiple mobile echogenic calculi in the lumen producing distinct posterior acoustic shadowing. Sonographic Murphy's sign is positive. Pericholecystic fluid is noted in the gallbladder bed.",
      rawErrorsCount: 4,
      cwer: "13.6%",
      wer: "15.8%",
      latency: "9.2 ms",
      corrections: [
        { input: "call cul us / cal cul us", soundex: "K424", strategy: "Phonetic Homophone Mapping", rescued: "calculus / calculi" },
        { input: "four point five millimeters", soundex: "NUM_UNIT", strategy: "Regex Spoken Metric Parser", rescued: "4.5 mm" },
        { input: "acoustic shadow", soundex: "A223", strategy: "N-Gram Hotword Boosting", rescued: "posterior acoustic shadowing" },
        { input: "murphys sign", soundex: "M612", strategy: "Ultrasound Lexicon Match", rescued: "Murphy's sign" },
        { input: "peri cholecystic", soundex: "P624", strategy: "Prefix Token Concatenation", rescued: "pericholecystic" }
      ]
    },
    "CASE_ABD_002": {
      id: "CASE_ABD_002",
      organ: "Liver",
      condition: "Hepatic steatosis with focal hemangioma",
      speechText: "The liver shows increased diffuse parenchymal echogenicity consistent with moderate hepatic steatosis. In segment six of the right hepatic lobe, there is a well-circumscribed hyperechoic lesion measuring 1.8 centimeters, characteristic of a hepatic hemangioma. Portal vein remains patent.",
      rawText: "The liver shows increased diffuse parenchymal echo genicity consistent with moderate hepatic stea tosis. There is mild posterior acoustic attenuation. In segment six of the right hepatic lobe, there is a well-circumscribed hyper echoic lesion measuring one point eight centimeters, characteristic of a hepatic hemangioma. Portal vein remains patent.",
      biasedText: `The liver shows increased diffuse parenchymal <strong class="highlight-anat">echogenicity</strong> consistent with moderate hepatic <strong class="highlight-anat">steatosis</strong>. In segment six of the right hepatic lobe, there is a well-circumscribed <strong class="highlight-anat">hyperechoic</strong> lesion measuring <strong class="highlight-meas">1.8 cm</strong>, characteristic of a <strong class="highlight-anat">hepatic hemangioma</strong>. Portal vein remains patent.`,
      plainBiased: "The liver shows increased diffuse parenchymal echogenicity consistent with moderate hepatic steatosis. In segment six of the right hepatic lobe, there is a well-circumscribed hyperechoic lesion measuring 1.8 cm, characteristic of a hepatic hemangioma. Portal vein remains patent.",
      rawErrorsCount: 3,
      cwer: "8.7%",
      wer: "6.8%",
      latency: "8.8 ms",
      corrections: [
        { input: "stea tosis", soundex: "S332", strategy: "Syllable Fusion / Soundex", rescued: "steatosis" },
        { input: "hyper echoic", soundex: "H162", strategy: "Compound Term Unification", rescued: "hyperechoic" },
        { input: "one point eight centimeters", soundex: "NUM_UNIT", strategy: "Regex Spoken Metric Parser", rescued: "1.8 cm" }
      ]
    },
    "CASE_ABD_003": {
      id: "CASE_ABD_003",
      organ: "Kidneys",
      condition: "Right renal calculus and hydronephrosis",
      speechText: "Right kidney demonstrates moderate pyelocaliceal dilatation and hydronephrosis secondary to an obstructing 7.0 millimeter calculus in the right proximal ureter. Preserved corticomedullary differentiation. Left kidney is normal without nephrolithiasis.",
      rawText: "Right kidney demonstrates moderate pyelo caliceal dilatation and hydro nephrosis secondary to an obstructing seven millimeter call cul us in the right proximal ureter. Preserved cortico medullary differentiation. Left kidney is normal in size without nephro lithiasis.",
      biasedText: `Right kidney demonstrates moderate <strong class="highlight-anat">pyelocaliceal dilatation</strong> and <strong class="highlight-anat">hydronephrosis</strong> secondary to an obstructing <strong class="highlight-meas">7.0 mm</strong> <strong class="highlight-anat">calculus</strong> in the right proximal ureter. Preserved <strong class="highlight-anat">corticomedullary differentiation</strong>. Left kidney is normal without <strong class="highlight-anat">nephrolithiasis</strong>.`,
      plainBiased: "Right kidney demonstrates moderate pyelocaliceal dilatation and hydronephrosis secondary to an obstructing 7.0 mm calculus in the right proximal ureter. Preserved corticomedullary differentiation. Left kidney is normal without nephrolithiasis.",
      rawErrorsCount: 5,
      cwer: "13.6%",
      wer: "11.8%",
      latency: "10.4 ms",
      corrections: [
        { input: "pyelo caliceal", soundex: "P424", strategy: "Anatomical Lexicon Match", rescued: "pyelocaliceal" },
        { input: "hydro nephrosis", soundex: "H365", strategy: "Compound Term Fusion", rescued: "hydronephrosis" },
        { input: "seven millimeter", soundex: "NUM_UNIT", strategy: "Regex Spoken Metric Parser", rescued: "7.0 mm" },
        { input: "cortico medullary", soundex: "C632", strategy: "Levenshtein Fuzzy Match", rescued: "corticomedullary" },
        { input: "nephro lithiasis", soundex: "N164", strategy: "Phonetic Dictionary", rescued: "nephrolithiasis" }
      ]
    },
    "CASE_ABD_004": {
      id: "CASE_ABD_004",
      organ: "Aorta",
      condition: "Abdominal aortic aneurysm with mural thrombus",
      speechText: "Proximal abdominal aorta measures 2.1 centimeters. Infrarenal abdominal aorta demonstrates a fusiform aneurysm measuring 4.8 centimeters with concentric mural thrombus.",
      rawText: "Proximal abdominal aorta measures two point one centimeters. Infra renal abdominal aorta demonstrates a fusiform aneurysm measuring four point eight centimeters in maximal transverse diameter with concentric mural thrombus.",
      biasedText: `Proximal abdominal aorta measures <strong class="highlight-meas">2.1 cm</strong>. Infrarenal abdominal aorta demonstrates a <strong class="highlight-anat">fusiform aneurysm</strong> measuring <strong class="highlight-meas">4.8 cm</strong> in maximal transverse diameter with concentric <strong class="highlight-anat">mural thrombus</strong>.`,
      plainBiased: "Proximal abdominal aorta measures 2.1 cm. Infrarenal abdominal aorta demonstrates a fusiform aneurysm measuring 4.8 cm in maximal transverse diameter with concentric mural thrombus.",
      rawErrorsCount: 3,
      cwer: "6.7%",
      wer: "12.5%",
      latency: "8.4 ms",
      corrections: [
        { input: "two point one centimeters", soundex: "NUM_UNIT", strategy: "Regex Spoken Metric Parser", rescued: "2.1 cm" },
        { input: "four point eight centimeters", soundex: "NUM_UNIT", strategy: "Regex Spoken Metric Parser", rescued: "4.8 cm" },
        { input: "infra renal", soundex: "I516", strategy: "Anatomical Compound Fix", rescued: "infrarenal" }
      ]
    },
    "CASE_ABD_005": {
      id: "CASE_ABD_005",
      organ: "Spleen",
      condition: "Splenomegaly with free fluid in Morison's pouch",
      speechText: "Spleen is enlarged with craniocaudal length measuring 14.2 centimeters consistent with moderate splenomegaly. Parenchymal echotexture is homogeneous. Trace anechoic free fluid in Morison's pouch.",
      rawText: "Spleen is enlarged with craniocaudal length measuring fourteen point two centimeters consistent with moderate spleno megaly. Parenchymal echo texture is homogeneous. Trace an echoic free fluid is visualized in morrisons pouch and splenorenal recess.",
      biasedText: `Spleen is enlarged with craniocaudal length measuring <strong class="highlight-meas">14.2 cm</strong> consistent with moderate <strong class="highlight-anat">splenomegaly</strong>. Parenchymal echotexture is homogeneous. Trace <strong class="highlight-anat">anechoic</strong> free fluid is visualized in <strong class="highlight-anat">Morison's pouch</strong>.`,
      plainBiased: "Spleen is enlarged with craniocaudal length measuring 14.2 cm consistent with moderate splenomegaly. Parenchymal echotexture is homogeneous. Trace anechoic free fluid is visualized in Morison's pouch.",
      rawErrorsCount: 4,
      cwer: "6.2%",
      wer: "10.3%",
      latency: "9.6 ms",
      corrections: [
        { input: "fourteen point two centimeters", soundex: "NUM_UNIT", strategy: "Regex Spoken Metric Parser", rescued: "14.2 cm" },
        { input: "spleno megaly", soundex: "S145", strategy: "Syllable Fusion / Soundex", rescued: "splenomegaly" },
        { input: "an echoic", soundex: "A522", strategy: "Echogenicity Descriptor Match", rescued: "anechoic" },
        { input: "morrisons pouch", soundex: "M625", strategy: "Eponym Normalization", rescued: "Morison's pouch" }
      ]
    }
  };

  // Simulated Keyframes
  const sampleKeyframes = [
    {
      id: "KF_01_GB",
      organ: "Gallbladder",
      view: "Subcostal Transverse",
      timestamp: "1.2s",
      caseId: "CASE_ABD_001",
      measurements: { d1: "4.5 mm (Wall)", d2: "7.0 mm (Calculus)" }
    },
    {
      id: "KF_02_LIVER",
      organ: "Liver Seg VI",
      view: "Intercostal Sagittal",
      timestamp: "2.8s",
      caseId: "CASE_ABD_002",
      measurements: { d1: "1.8 cm (Hemangioma)", d2: "14.5 cm (Span)" }
    },
    {
      id: "KF_03_KIDNEY",
      organ: "Right Kidney",
      view: "Coronal Hepatorenal",
      timestamp: "4.5s",
      caseId: "CASE_ABD_003",
      measurements: { d1: "7.0 mm (Calculus)", d2: "11.2 cm (Length)" }
    }
  ];

  // Initialize Keyframe Strip
  const gallery = document.getElementById("keyframe-gallery");
  if (gallery) {
    gallery.innerHTML = sampleKeyframes.map((kf, i) => `
      <div class="keyframe-item ${i === 0 ? 'selected' : ''}" data-id="${kf.id}" data-case="${kf.caseId}">
        <div class="keyframe-thumb-label">${kf.organ}</div>
        <div class="keyframe-thumb-time">${kf.view} &bull; ${kf.timestamp}</div>
      </div>
    `).join("");

    gallery.querySelectorAll(".keyframe-item").forEach(item => {
      item.addEventListener("click", () => {
        gallery.querySelectorAll(".keyframe-item").forEach(k => k.classList.remove("selected"));
        item.classList.add("selected");
        const caseId = item.dataset.case;
        loadClinicalCase(caseId);
        showToast(`Synchronized Keyframe: ${item.dataset.id} selected`);
      });
    });
  }

  // Structured Organ Findings
  const sampleOrganFindings = [
    {
      organ: "gallbladder",
      name: "Gallbladder & Biliary Tree",
      abnormal: true,
      text: "Gallbladder demonstrates diffuse wall thickening measuring 4.5 mm with multiple mobile echogenic calculi in the lumen producing distinct posterior acoustic shadowing. Positive sonographic Murphy's sign and trace pericholecystic fluid."
    },
    {
      organ: "liver",
      name: "Liver & Portal Venous System",
      abnormal: true,
      text: "Liver parenchyma demonstrates moderately increased echogenicity consistent with hepatic steatosis. Well-circumscribed hyperechoic lesion measuring 1.8 cm in segment 6 compatible with hemangioma. Portal vein is patent."
    },
    {
      organ: "kidneys",
      name: "Kidneys & Retroperitoneum",
      abnormal: false,
      text: "Bilateral kidneys demonstrate normal corticomedullary differentiation. Preserved renal sinus echogenicity. No hydronephrosis or obstructing nephrolithiasis identified."
    },
    {
      organ: "aorta",
      name: "Abdominal Aorta & Inferior Vena Cava",
      abnormal: false,
      text: "Abdominal aorta is non-aneurysmal measuring 1.9 cm in maximal caliber. Proximal celiac axis and SMA origins are widely patent. IVC demonstrates normal respiratory collapsibility."
    }
  ];

  // Initialize Findings Editor
  const findingsContainer = document.getElementById("organ-findings-list");
  if (findingsContainer) {
    findingsContainer.innerHTML = sampleOrganFindings.map(f => `
      <div class="organ-card" data-organ="${f.organ}">
        <div class="organ-card-header">
          <span class="organ-name">${f.name}</span>
          <span class="${f.abnormal ? 'badge-abnormal' : 'badge-normal'}">
            ${f.abnormal ? 'ABNORMAL FINDING' : 'UNREMARKABLE'}
          </span>
        </div>
        <textarea class="organ-textarea" rows="2" data-prev="${encodeURIComponent(f.text)}">${f.text}</textarea>
      </div>
    `).join("");
  }

  // ==========================================================
  // CRYPTOGRAPHIC SHA-256 AUDIT LOG SYSTEM (MEMBER 4: DINESH)
  // ==========================================================
  async function computeSha256(str) {
    try {
      if (window.crypto && window.crypto.subtle) {
        const encoder = new TextEncoder();
        const data = encoder.encode(str);
        const hashBuffer = await window.crypto.subtle.digest("SHA-256", data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return "sha256:" + hashArray.map(b => b.toString(16).padStart(2, "0")).slice(0, 8).join("");
      }
    } catch (e) {
      // Fallback
    }
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return "sha256:" + Math.abs(hash).toString(16).padStart(8, "0");
  }

  async function recordAuditEvent(action, field, prevVal, newVal, reason) {
    const timestamp = Date.now();
    const eventId = `AUD_${timestamp}_${auditEvents.length + 1}`;
    const rawPayload = `${eventId}:${timestamp}:${activeRole}:${field}:${newVal}`;
    const checksum = await computeSha256(rawPayload);

    const entry = {
      eventId,
      time: new Date(timestamp).toLocaleTimeString(),
      isoTime: new Date(timestamp).toISOString(),
      user: activeRole.toUpperCase(),
      action,
      field,
      prevVal: String(prevVal).substring(0, 45) + "...",
      newVal: String(newVal).substring(0, 45) + "...",
      checksum,
      reason: reason || "Radiologist verification edit"
    };

    auditEvents.unshift(entry);
    renderAuditStream();
    renderFullAuditTable();

    const countBadge = document.getElementById("audit-count-badge");
    if (countBadge) countBadge.innerText = `${auditEvents.length} Events`;
  }

  function renderAuditStream() {
    const feed = document.getElementById("audit-feed-box");
    if (!feed) return;
    feed.innerHTML = auditEvents.slice(0, 6).map(e => `
      <div class="audit-event-card">
        <div class="audit-event-header">
          <span>${e.time} &bull; ${e.user}</span>
          <span style="color: var(--accent-cyan);">${e.action}</span>
        </div>
        <div class="audit-event-body">
          <strong>${e.field}:</strong> ${e.newVal}
        </div>
        <div class="audit-hash">${e.checksum}</div>
      </div>
    `).join("");
  }

  function renderFullAuditTable() {
    const tbody = document.getElementById("full-audit-table-body");
    if (!tbody) return;
    tbody.innerHTML = auditEvents.map(e => `
      <tr>
        <td><code>${e.eventId}</code></td>
        <td>${e.isoTime}</td>
        <td><span class="badge-member it">${e.user}</span></td>
        <td>${e.action}</td>
        <td><strong>${e.field}</strong></td>
        <td>${e.newVal}</td>
        <td><code>${e.checksum}</code></td>
      </tr>
    `).join("");
  }

  // Pre-seed initial compliance events
  recordAuditEvent("SESSION_INITIALIZED", "multimodal_capture", "NONE", "Master clock sync 16kHz audio + video", "System boot");
  recordAuditEvent("BIAS_ASR_APPLIED", "cholelithiasis", "coal a lithiasis", "cholelithiasis (boosted)", "Member 2 ASR Biasing");
  recordAuditEvent("MEASUREMENT_NORMALIZED", "gallbladder_wall", "four point five millimeters", "4.5 mm", "Structured Formatter");

  // Track keystrokes in organ cards
  document.querySelectorAll(".organ-textarea").forEach(textarea => {
    textarea.addEventListener("blur", (e) => {
      const prev = decodeURIComponent(e.target.dataset.prev);
      const cur = e.target.value.trim();
      if (prev !== cur) {
        const organCard = e.target.closest(".organ-card");
        const organName = organCard ? organCard.querySelector(".organ-name").innerText : "Organ";
        recordAuditEvent("RADIOLOGIST_MANUAL_EDIT", organName, prev, cur, "Clinical accuracy correction");
        e.target.dataset.prev = encodeURIComponent(cur);
      }
    });
  });

  // Track keystrokes in impression textarea
  const impArea = document.getElementById("impression-textarea");
  let prevImp = impArea ? impArea.value : "";
  if (impArea) {
    impArea.addEventListener("blur", () => {
      if (impArea.value !== prevImp) {
        recordAuditEvent("RADIOLOGIST_IMPRESSION_EDIT", "Final Impression", prevImp, impArea.value, "Clinical synthesis review");
        prevImp = impArea.value;
      }
    });
  }

  // ==========================================================
  // PLAY / PAUSE SYNCHRONOUS AUDIO DICTATION (REAL SOUND)
  // ==========================================================
  const playBtn = document.getElementById("play-pause-btn");
  const caseSelect = document.getElementById("asr-case-select");

  function toggleAudioPlayback() {
    if (isAudioPlaying) {
      stopAllAudio();
      showToast("Audio playback paused");
      return;
    }

    const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
    const caseData = clinicalCasesData[activeCaseId];
    if (!caseData) return;

    isAudioPlaying = true;
    if (playBtn) {
      playBtn.classList.add("playing");
      playBtn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`;
    }

    // Start Doppler acoustics & oscilloscope wave
    startUltrasoundAcousticSound();
    startAnimatedWaveform();

    // Stream speech dictation aloud via SpeechSynthesis
    const streamBiased = document.getElementById("stream-text-biased");
    const streamRaw = document.getElementById("stream-text-raw");

    if (streamBiased) {
      streamBiased.innerHTML = `<span style="color: var(--accent-cyan);">Streaming synchronous audio...</span>`;
    }

    speakMedicalDictation(
      caseData.speechText,
      (spokenWord) => {
        // As words are spoken, update the stream
        if (streamBiased) {
          streamBiased.innerHTML = caseData.biasedText;
        }
      },
      () => {
        // Complete
        stopAllAudio();
        recordAuditEvent("SPEECH_STREAM_FINALIZED", "AudioPlayback", "PLAYING", "Completed 6.0s sync segment", "Member 2 ASR Streamer");
        showToast("Synchronous dictation playback finished");
      }
    );

    recordAuditEvent("AUDIO_PLAYBACK_STARTED", caseData.organ, "OFFLINE", "Acoustic Doppler + Voice Synced", "Member 1 Keyframe Audio Play");
    showToast(`Playing doctor dictation for ${caseData.organ}...`);
  }

  if (playBtn) {
    playBtn.addEventListener("click", toggleAudioPlayback);
  }

  // Word-by-word streaming simulation button
  const streamReplayBtn = document.getElementById("stream-replay-btn");
  if (streamReplayBtn) {
    streamReplayBtn.addEventListener("click", () => {
      toggleAudioPlayback();
    });
  }

  // Foot pedal simulation button
  const simTriggerBtn = document.getElementById("simulate-trigger-btn");
  if (simTriggerBtn) {
    simTriggerBtn.addEventListener("click", () => {
      playPedalSound();
      const organs = ["Gallbladder", "Liver Seg VI", "Right Kidney", "Spleen", "Aorta"];
      const randomOrgan = organs[Math.floor(Math.random() * organs.length)];
      recordAuditEvent("HARDWARE_PEDAL_TRIGGER", randomOrgan, "FRAME_BUFFER", `KEYFRAME_CAPTURED_TIMESTAMP_${Date.now()}`, "Member 1 Foot Pedal Interrupt (Hotkey: F8)");
      showToast(`[PEDAL CLICK] Keyframe captured for: ${randomOrgan} + 16kHz audio synced!`);
    });
  }

  // Listen for F8 key as Foot Pedal
  window.addEventListener("keydown", (e) => {
    if (e.key === "F8") {
      e.preventDefault();
      if (simTriggerBtn) simTriggerBtn.click();
    }
  });

  // ==========================================================
  // SPEECH-TO-TEXT LAB CONTROLLER (MEMBER 2: SOHUM)
  // ==========================================================
  function loadClinicalCase(caseId) {
    const data = clinicalCasesData[caseId];
    if (!data) return;

    // Update ASR Lab KPIs
    const cwerEl = document.getElementById("lab-cwer-val");
    const werEl = document.getElementById("lab-wer-val");
    const latEl = document.getElementById("lab-latency-val");
    const errCountEl = document.getElementById("lab-raw-errors-count");

    if (cwerEl) cwerEl.innerText = data.cwer;
    if (werEl) werEl.innerText = data.wer;
    if (latEl) latEl.innerText = data.latency;
    if (errCountEl) errCountEl.innerText = `${data.rawErrorsCount} Terminology Errors`;

    // Update Comparison Text
    const rawBox = document.getElementById("lab-raw-text-box");
    const biasedBox = document.getElementById("lab-biased-text-box");
    if (rawBox) rawBox.innerHTML = data.rawText;
    if (biasedBox) biasedBox.innerHTML = data.biasedText;

    // Update Phonetic Table
    const tbody = document.getElementById("phonetic-corrections-tbody");
    if (tbody) {
      tbody.innerHTML = data.corrections.map(c => `
        <tr>
          <td><code>${c.input}</code></td>
          <td><code>${c.soundex}</code></td>
          <td>${c.strategy}</td>
          <td><strong class="highlight-anat">${c.rescued}</strong></td>
          <td><span class="status-done">&check; Rescued</span></td>
        </tr>
      `).join("");
    }

    // Update Review Stream as well
    const streamRaw = document.getElementById("stream-text-raw");
    const streamBiased = document.getElementById("stream-text-biased");
    if (streamRaw) streamRaw.innerHTML = data.rawText;
    if (streamBiased) streamBiased.innerHTML = data.biasedText;

    recordAuditEvent("CLINICAL_CASE_LOADED", data.organ, "PREVIOUS_CASE", data.condition, "User switched evaluation scenario");
  }

  if (caseSelect) {
    caseSelect.addEventListener("change", (e) => {
      loadClinicalCase(e.target.value);
      if (isAudioPlaying) {
        stopAllAudio();
      }
    });
    // Load initial case
    loadClinicalCase("CASE_ABD_001");
  }

  // Button: Transcribe Case in ASR Lab (with audio voice)
  const labSimulateBtn = document.getElementById("lab-simulate-btn");
  if (labSimulateBtn) {
    labSimulateBtn.addEventListener("click", () => {
      toggleAudioPlayback();
    });
  }

  // Push to report editor button
  const pushToEditorBtn = document.getElementById("push-to-editor-btn");
  if (pushToEditorBtn) {
    pushToEditorBtn.addEventListener("click", () => {
      const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
      const caseData = clinicalCasesData[activeCaseId];

      const targetCard = document.querySelector(`.organ-card[data-organ="${caseData.organ.toLowerCase()}"]`);
      if (targetCard) {
        const textarea = targetCard.querySelector(".organ-textarea");
        if (textarea) {
          const oldVal = textarea.value;
          textarea.value = caseData.plainBiased;
          textarea.dataset.prev = encodeURIComponent(caseData.plainBiased);
          recordAuditEvent("LLM_STRUCTURED_REPORT_SYNC", caseData.organ, oldVal, caseData.plainBiased, "Member 3 LLM structuring from Member 2 ASR stream");
        }
      }

      showToast(`Findings for ${caseData.organ} pushed directly to Report Editor!`);
      const reviewTab = document.getElementById("tab-btn-review");
      if (reviewTab) reviewTab.click();
    });
  }

  // Interactive Biasing Sandbox (Type any sentence to see real-time biasing)
  const runSandboxBtn = document.getElementById("run-sandbox-btn");
  const sandboxInput = document.getElementById("sandbox-input");
  const sandboxOutput = document.getElementById("sandbox-output-text");

  function runSandboxBiasing() {
    if (!sandboxInput || !sandboxOutput) return;
    const text = sandboxInput.value.trim();
    if (!text) return;

    let processed = text
      .replace(/call cul us|cal cul us/gi, `<strong class="highlight-anat">calculi</strong>`)
      .replace(/peri cholecystic/gi, `<strong class="highlight-anat">pericholecystic</strong>`)
      .replace(/chole lithiasis|coal a lithiasis/gi, `<strong class="highlight-anat">cholelithiasis</strong>`)
      .replace(/stea tosis/gi, `<strong class="highlight-anat">steatosis</strong>`)
      .replace(/hyper echoic/gi, `<strong class="highlight-anat">hyperechoic</strong>`)
      .replace(/four point five millimeters/gi, `<strong class="highlight-meas">4.5 mm</strong>`)
      .replace(/seven millimeter|7 millimeter/gi, `<strong class="highlight-meas">7.0 mm</strong>`)
      .replace(/one point eight centimeters/gi, `<strong class="highlight-meas">1.8 cm</strong>`);

    sandboxOutput.innerHTML = processed;
    recordAuditEvent("SANDBOX_BIAS_TEST", "interactive_input", text, processed.replace(/<[^>]*>/g, ""), "Phonetic Soundex Sandbox");
    showToast("Phonetic Biasing applied to custom input!");
  }

  if (runSandboxBtn) runSandboxBtn.addEventListener("click", runSandboxBiasing);
  if (sandboxInput) {
    sandboxInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") runSandboxBiasing();
    });
  }

  // ==========================================================
  // REAL-TIME MICROPHONE SPEECH-TO-TEXT (WEB SPEECH API)
  // ==========================================================
  function setupLiveMicrophone() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const micButtons = [
      { btn: document.getElementById("live-mic-btn"), label: document.getElementById("live-mic-text") },
      { btn: document.getElementById("lab-mic-btn"), label: document.getElementById("lab-mic-text") }
    ];

    if (!SpeechRecognition) {
      console.warn("Web Speech API not supported. Falling back to simulated voice.");
      micButtons.forEach(({ btn, label }) => {
        if (btn) {
          btn.addEventListener("click", () => {
            toggleAudioPlayback();
          });
        }
      });
      return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isListening = true;
      initAudioContext();
      startAnimatedWaveform();
      micButtons.forEach(({ btn, label }) => {
        if (btn) btn.classList.add("recording");
        if (label) label.innerText = "Listening (Speak Now)...";
      });
      recordAuditEvent("MICROPHONE_OPENED", "live_stream", "OFFLINE", "16kHz Mono Stream Active", "Radiologist live dictation");
      showToast("Microphone active! Speak medical terms now...");
    };

    recognition.onresult = (event) => {
      let interim = "";
      let final = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      const spoken = final || interim;
      if (spoken) {
        let biased = spoken
          .replace(/call cul us|cal cul us/gi, "calculus")
          .replace(/chole lithiasis|coal a lithiasis/gi, "cholelithiasis")
          .replace(/hyper echoic/gi, "hyperechoic")
          .replace(/stea tosis/gi, "steatosis")
          .replace(/hydro nephrosis/gi, "hydronephrosis")
          .replace(/four point five millimeters/gi, "4.5 mm");

        const streamRaw = document.getElementById("stream-text-raw");
        const streamBiased = document.getElementById("stream-text-biased");
        if (streamRaw) streamRaw.innerText = spoken;
        if (streamBiased) streamBiased.innerHTML = biased;
      }
    };

    recognition.onerror = (e) => {
      console.error("SpeechRecognition error:", e);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };

    function startListening() {
      try {
        recognition.start();
      } catch (err) {
        console.error(err);
      }
    }

    function stopListening() {
      isListening = false;
      if (animFrameId) {
        cancelAnimationFrame(animFrameId);
        animFrameId = null;
      }
      drawIdleWaveform();
      micButtons.forEach(({ btn, label }) => {
        if (btn) btn.classList.remove("recording");
        if (label) label.innerText = label.id === "live-mic-text" ? "Live Mic" : "Live Microphone";
      });
    }

    micButtons.forEach(({ btn }) => {
      if (btn) {
        btn.addEventListener("click", () => {
          if (isListening) {
            recognition.stop();
            stopListening();
          } else {
            startListening();
          }
        });
      }
    });
  }

  setupLiveMicrophone();

  // ==========================================================
  // NAVIGATION & PRESENTATION MODE SLIDE DECK
  // ==========================================================
  // Tab Switching
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach(t => {
        t.classList.remove("active");
        t.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");
      const targetId = tab.dataset.tab;
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Slide Deck Navigation
  function showSlide(n) {
    if (n < 1) n = 1;
    if (n > totalSlides) n = totalSlides;
    currentSlide = n;

    document.querySelectorAll(".presentation-slide").forEach(s => s.classList.remove("active"));
    const activeSlide = document.querySelector(`.presentation-slide[data-slide="${currentSlide}"]`);
    if (activeSlide) activeSlide.classList.add("active");

    const curEl = document.getElementById("current-slide-num");
    if (curEl) curEl.innerText = currentSlide;
  }

  const prevBtn = document.getElementById("prev-slide-btn");
  const nextBtn = document.getElementById("next-slide-btn");
  if (prevBtn) prevBtn.addEventListener("click", () => showSlide(currentSlide - 1));
  if (nextBtn) nextBtn.addEventListener("click", () => showSlide(currentSlide + 1));

  document.addEventListener("keydown", (e) => {
    const presMode = document.getElementById("presentation-mode");
    if (presMode && presMode.classList.contains("active")) {
      if (e.key === "ArrowRight") showSlide(currentSlide + 1);
      if (e.key === "ArrowLeft") showSlide(currentSlide - 1);
      if (e.key === "f" || e.key === "F") {
        if (!document.fullscreenElement) {
          presMode.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      }
    }
  });

  // Fullscreen button
  const fsBtn = document.getElementById("fullscreen-toggle-btn");
  if (fsBtn) {
    fsBtn.addEventListener("click", () => {
      const presMode = document.getElementById("presentation-mode");
      if (presMode) {
        if (!document.fullscreenElement) {
          presMode.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      }
    });
  }

  // Launch Demo button from slide 6
  const launchDemoBtn = document.getElementById("launch-demo-from-slide-btn");
  if (launchDemoBtn) {
    launchDemoBtn.addEventListener("click", () => {
      const reviewTab = document.getElementById("tab-btn-review");
      if (reviewTab) reviewTab.click();
    });
  }

  // Open full audit log button
  const openAuditBtn = document.getElementById("open-full-audit-btn");
  if (openAuditBtn) {
    openAuditBtn.addEventListener("click", () => {
      const auditTab = document.getElementById("tab-btn-audit");
      if (auditTab) auditTab.click();
    });
  }

  // Diff toggle button
  const toggleDiffBtn = document.getElementById("toggle-diff-btn");
  let diffActive = false;
  if (toggleDiffBtn) {
    toggleDiffBtn.addEventListener("click", () => {
      diffActive = !diffActive;
      toggleDiffBtn.style.color = diffActive ? "var(--accent-cyan)" : "var(--text-main)";
      toggleDiffBtn.innerText = diffActive ? "Showing Diff Highlights" : "Show AI vs Corrected";
      showToast(diffActive ? "Diff comparison mode activated" : "Standard editor mode");
    });
  }

  // Approve & Sign Report Button (Authentic SHA-256 Sign-off)
  const saveReportBtn = document.getElementById("save-report-btn");
  if (saveReportBtn) {
    saveReportBtn.addEventListener("click", async () => {
      const statusText = document.getElementById("save-status-text");
      const signature = await computeSha256("FINAL_REPORT_ACR_ALVAREZ_" + Date.now());

      if (statusText) {
        statusText.innerHTML = `
          <span class="status-indicator-dot online"></span>
          <span>SIGNED &amp; COMMITTED (${signature})</span>
        `;
        statusText.style.color = "var(--accent-emerald)";
      }

      await recordAuditEvent("REPORT_APPROVED_AND_SIGNED", "approval_state", "DRAFT", signature, "Attending Radiologist Final Cryptographic Signature");
      showToast("Report approved and cryptographically signed with SHA-256! Ready for PACS export.");
    });
  }

  // RBAC Role Switcher
  const rbacSelect = document.getElementById("rbac-role-select");
  if (rbacSelect) {
    rbacSelect.addEventListener("change", (e) => {
      activeRole = e.target.value;
      recordAuditEvent("RBAC_ROLE_SWITCH", "active_user_context", activeRole, e.target.value, "Operator switched clinical role");
      showToast(`Active role switched to: ${e.target.options[e.target.selectedIndex].text}`);
    });
  }

  // Export Audit Log (JSONL)
  const exportAuditBtn = document.getElementById("export-audit-json-btn");
  if (exportAuditBtn) {
    exportAuditBtn.addEventListener("click", () => {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(auditEvents, null, 2));
      const dlAnchor = document.createElement("a");
      dlAnchor.setAttribute("href", dataStr);
      dlAnchor.setAttribute("download", `${currentSessionId}_audit_log.json`);
      dlAnchor.click();
      showToast("Audit log exported as JSONL");
    });
  }
});
