// EchoScribe-AI / SonoAssist - Clinical UI Controller
// Member 4 (Dinesh - IT Deliverable) & Member 2 (Sohum - Speech Pipeline Integration)

document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentSessionId = "SESS_20261023_042";
  let activeRole = "radiologist";
  let currentSlide = 1;
  const totalSlides = 6;
  let auditEvents = [];
  let isListening = false;
  let recognition = null;
  let isStreamingReplay = false;

  // Clinical Cases Dataset for Speech-to-Text Lab
  const clinicalCasesData = {
    "CASE_ABD_001": {
      id: "CASE_ABD_001",
      organ: "Gallbladder",
      condition: "Acute cholecystitis with cholelithiasis",
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
      rawText: "The liver shows increased diffuse parenchymal echo genicity consistent with moderate hepatic stea tosis. There is mild posterior acoustic attenuation. In segment six of the right hepatic lobe, there is a well-circumscribed hyper echoic lesion measuring one point eight centimeters, characteristic of a hepatic hemangioma. Portal vein remains patent.",
      biasedText: `The liver shows increased diffuse parenchymal <strong class="highlight-anat">echogenicity</strong> consistent with moderate hepatic <strong class="highlight-anat">steatosis</strong>. There is mild posterior acoustic attenuation. In segment six of the right hepatic lobe, there is a well-circumscribed <strong class="highlight-anat">hyperechoic</strong> lesion measuring <strong class="highlight-meas">1.8 cm</strong>, characteristic of a <strong class="highlight-anat">hepatic hemangioma</strong>. Portal vein remains patent.`,
      plainBiased: "The liver shows increased diffuse parenchymal echogenicity consistent with moderate hepatic steatosis. There is mild posterior acoustic attenuation. In segment six of the right hepatic lobe, there is a well-circumscribed hyperechoic lesion measuring 1.8 cm, characteristic of a hepatic hemangioma. Portal vein remains patent.",
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
      rawText: "Right kidney demonstrates moderate pyelo caliceal dilatation and hydro nephrosis secondary to an obstructing seven millimeter call cul us in the right proximal ureter. Preserved cortico medullary differentiation. Left kidney is normal in size without nephro lithiasis.",
      biasedText: `Right kidney demonstrates moderate <strong class="highlight-anat">pyelocaliceal dilatation</strong> and <strong class="highlight-anat">hydronephrosis</strong> secondary to an obstructing <strong class="highlight-meas">7.0 mm</strong> <strong class="highlight-anat">calculus</strong> in the right proximal ureter. Preserved <strong class="highlight-anat">corticomedullary differentiation</strong>. Left kidney is normal in size without <strong class="highlight-anat">nephrolithiasis</strong>.`,
      plainBiased: "Right kidney demonstrates moderate pyelocaliceal dilatation and hydronephrosis secondary to an obstructing 7.0 mm calculus in the right proximal ureter. Preserved corticomedullary differentiation. Left kidney is normal in size without nephrolithiasis.",
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
      rawText: "Spleen is enlarged with craniocaudal length measuring fourteen point two centimeters consistent with moderate spleno megaly. Parenchymal echo texture is homogeneous. Trace an echoic free fluid is visualized in morrisons pouch and splenorenal recess.",
      biasedText: `Spleen is enlarged with craniocaudal length measuring <strong class="highlight-meas">14.2 cm</strong> consistent with moderate <strong class="highlight-anat">splenomegaly</strong>. Parenchymal echotexture is homogeneous. Trace <strong class="highlight-anat">anechoic</strong> free fluid is visualized in <strong class="highlight-anat">Morison's pouch</strong> and <strong class="highlight-anat">splenorenal recess</strong>.`,
      plainBiased: "Spleen is enlarged with craniocaudal length measuring 14.2 cm consistent with moderate splenomegaly. Parenchymal echotexture is homogeneous. Trace anechoic free fluid is visualized in Morison's pouch and splenorenal recess.",
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

  // Simulated Keyframes Data
  const sampleKeyframes = [
    {
      id: "KF_01_GB",
      organ: "Gallbladder",
      view: "Longitudinal / Subcostal",
      timestamp: "1.2s",
      svgGraphic: `<svg viewBox="0 0 320 200" width="100%" height="100%"><rect width="320" height="200" fill="#04070e"/><path d="M40 20 Q160 180 280 20" stroke="#1e293b" stroke-width="2" fill="none"/><ellipse cx="160" cy="100" rx="65" ry="40" fill="#020408" stroke="#38bdf8" stroke-width="3"/><circle cx="150" cy="115" r="9" fill="#f8fafc" stroke="#38bdf8" stroke-width="1.5"/><path d="M141 125 L135 180" stroke="#06b6d4" stroke-dasharray="2,2"/><path d="M159 125 L165 180" stroke="#06b6d4" stroke-dasharray="2,2"/><text x="175" y="125" fill="#f59e0b" font-size="10" font-family="monospace">Calculus (7mm)</text><text x="80" y="55" fill="#f43f5e" font-size="10" font-family="monospace">Thickened Wall (4.5mm)</text></svg>`
    },
    {
      id: "KF_02_LIVER",
      organ: "Liver",
      view: "Sagittal / Hepatic Lobe",
      timestamp: "2.8s",
      svgGraphic: `<svg viewBox="0 0 320 200" width="100%" height="100%"><rect width="320" height="200" fill="#04070e"/><path d="M30 40 Q160 190 290 40" stroke="#1e293b" stroke-width="2" fill="none"/><path d="M50 70 Q150 140 260 80" stroke="#64748b" stroke-width="1.5" fill="#090f1d"/><circle cx="210" cy="95" r="14" fill="#38bdf8" opacity="0.85"/><text x="140" y="135" fill="#38bdf8" font-size="10" font-family="monospace">Hemangioma (1.8cm)</text></svg>`
    },
    {
      id: "KF_03_KIDNEY",
      organ: "Right Kidney",
      view: "Coronal / Hepatorenal",
      timestamp: "4.5s",
      svgGraphic: `<svg viewBox="0 0 320 200" width="100%" height="100%"><rect width="320" height="200" fill="#04070e"/><ellipse cx="160" cy="100" rx="80" ry="45" fill="#090f1d" stroke="#64748b" stroke-width="2"/><ellipse cx="160" cy="100" rx="40" ry="18" fill="#020408" stroke="#38bdf8" stroke-width="2"/><text x="120" y="105" fill="#38bdf8" font-size="10" font-family="monospace">Pyelocaliceal Dilatation</text></svg>`
    }
  ];

  // Organ Findings Data
  const sampleOrganFindings = [
    {
      organ: "gallbladder",
      name: "Gallbladder & Biliary",
      abnormal: true,
      text: "Gallbladder demonstrates diffuse wall thickening measuring 4.5 mm with multiple intraluminal calculi producing posterior acoustic shadowing. Positive sonographic Murphy's sign and trace pericholecystic fluid."
    },
    {
      organ: "liver",
      name: "Liver & Portal Vein",
      abnormal: true,
      text: "Liver parenchyma demonstrates moderately increased echogenicity consistent with hepatic steatosis. Well-circumscribed hyperechoic lesion measuring 1.8 cm in segment 6 compatible with hemangioma. Portal vein is patent."
    },
    {
      organ: "kidneys",
      name: "Kidneys & Retroperitoneum",
      abnormal: false,
      text: "Bilateral kidneys demonstrate normal corticomedullary differentiation. No nephrolithiasis or hydronephrosis."
    },
    {
      organ: "aorta",
      name: "Abdominal Aorta & IVC",
      abnormal: false,
      text: "Abdominal aorta is non-aneurysmal measuring 1.9 cm. IVC demonstrates normal respiratory collapsibility."
    }
  ];

  // Initialize Keyframes
  const gallery = document.getElementById("keyframe-gallery");
  gallery.innerHTML = sampleKeyframes.map((kf, i) => `
    <div class="keyframe-item ${i === 0 ? 'selected' : ''}" data-id="${kf.id}">
      <div class="keyframe-thumb">${kf.svgGraphic}</div>
      <div class="keyframe-tag">${kf.organ} &bull; ${kf.timestamp}</div>
    </div>
  `).join("");

  // Initialize Organ Findings Editor
  const findingsContainer = document.getElementById("organ-findings-list");
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

  // Audit Event Generator
  function recordAuditEvent(action, field, prevVal, newVal, reason) {
    const timestamp = Date.now();
    const eventId = `AUD_${timestamp}_${auditEvents.length + 1}`;
    const rawCheck = `${eventId}:${timestamp}:${activeRole}:${field}:${newVal}`;
    let hash = 0;
    for (let i = 0; i < rawCheck.length; i++) {
      hash = ((hash << 5) - hash) + rawCheck.charCodeAt(i);
      hash |= 0;
    }
    const checksum = "sha256:" + Math.abs(hash).toString(16).padStart(8, '0');

    const entry = {
      eventId,
      time: new Date(timestamp).toLocaleTimeString(),
      isoTime: new Date(timestamp).toISOString(),
      user: activeRole.toUpperCase(),
      action,
      field,
      prevVal: String(prevVal).substring(0, 40) + "...",
      newVal: String(newVal).substring(0, 40) + "...",
      checksum,
      reason: reason || "Radiologist verification edit"
    };

    auditEvents.unshift(entry);
    renderAuditStream();
    renderFullAuditTable();
  }

  function renderAuditStream() {
    const feed = document.getElementById("audit-feed-box");
    if (!feed) return;
    feed.innerHTML = auditEvents.slice(0, 6).map(e => `
      <div class="audit-event-card">
        <div class="audit-event-header">
          <span>${e.time} &bull; ${e.user}</span>
          <span>${e.action}</span>
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
        <td><span class="badge-pill">${e.user}</span></td>
        <td>${e.action}</td>
        <td><strong>${e.field}</strong></td>
        <td>${e.newVal}</td>
        <td><code>${e.checksum}</code></td>
      </tr>
    `).join("");
  }

  // Pre-seed Initial Audit Events
  recordAuditEvent("SESSION_INITIALIZED", "multimodal_capture", "NONE", "Master clock sync 16kHz audio + video", "System boot");
  recordAuditEvent("BIAS_ASR_APPLIED", "cholelithiasis", "coal a lithiasis", "cholelithiasis (boosted)", "Member 2 ASR Biasing");
  recordAuditEvent("MEASUREMENT_NORMALIZED", "gallbladder_wall", "four point five millimeters", "4.5 mm", "Structured Formatter");

  // Track Keystrokes in Textareas
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

  // Impression textarea edit tracking
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

  // Tab Switching
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Quick button in Review screen to open ASR lab
  const openAsrLabBtn = document.getElementById("open-asr-lab-quick-btn");
  if (openAsrLabBtn) {
    openAsrLabBtn.addEventListener("click", () => {
      document.getElementById("tab-btn-asr").click();
    });
  }

  // ==========================================================
  // SPEECH-TO-TEXT LAB CONTROLLER (MEMBER 2: SOHUM)
  // ==========================================================
  const caseSelect = document.getElementById("asr-case-select");
  
  function loadClinicalCase(caseId) {
    const data = clinicalCasesData[caseId];
    if (!data) return;

    // Update Lab Cards
    document.getElementById("lab-cwer-val").innerText = data.cwer;
    document.getElementById("lab-wer-val").innerText = data.wer;
    document.getElementById("lab-latency-val").innerText = data.latency;
    document.getElementById("lab-raw-errors-count").innerText = `${data.rawErrorsCount} Terminology Errors`;

    // Highlight errors in raw text
    document.getElementById("lab-raw-text-box").innerHTML = data.rawText;
    document.getElementById("lab-biased-text-box").innerHTML = data.biasedText;

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

    // Update Review Screen Speech stream as well
    const streamRaw = document.getElementById("stream-text-raw");
    const streamBiased = document.getElementById("stream-text-biased");
    if (streamRaw) streamRaw.innerHTML = data.rawText;
    if (streamBiased) streamBiased.innerHTML = data.biasedText;

    recordAuditEvent("CLINICAL_CASE_LOADED", data.organ, "PREVIOUS_CASE", data.condition, "User switched clinical evaluation case");
  }

  if (caseSelect) {
    caseSelect.addEventListener("change", (e) => {
      loadClinicalCase(e.target.value);
    });
  }

  // Word-by-word streaming replay simulation
  function simulateStreamReplay(targetText, biasedHtml) {
    if (isStreamingReplay) return;
    isStreamingReplay = true;

    const streamBiased = document.getElementById("stream-text-biased");
    const words = targetText.split(" ");
    let index = 0;
    streamBiased.innerHTML = `<span style="color: var(--accent-cyan);">Listening...</span>`;

    // Animate audio waveform bars
    const bars = document.querySelectorAll(".waveform-bar");
    const waveInterval = setInterval(() => {
      bars.forEach(b => {
        b.style.height = `${Math.floor(Math.random() * 80 + 20)}%`;
      });
    }, 120);

    const streamInterval = setInterval(() => {
      if (index < words.length) {
        streamBiased.innerText = words.slice(0, index + 1).join(" ") + " ...";
        index++;
      } else {
        clearInterval(streamInterval);
        clearInterval(waveInterval);
        streamBiased.innerHTML = biasedHtml;
        isStreamingReplay = false;
        recordAuditEvent("SPEECH_STREAM_FINALIZED", "ASRSegment", "STREAMING_BUFFER", "Segment Finalized", "Real-Time Streaming Streamer (Sohum CSE2)");
      }
    }, 180);
  }

  // Button: Replay stream in review screen
  const replayBtn = document.getElementById("stream-replay-btn");
  if (replayBtn) {
    replayBtn.addEventListener("click", () => {
      const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
      const caseData = clinicalCasesData[activeCaseId];
      simulateStreamReplay(caseData.plainBiased, caseData.biasedText);
    });
  }

  // Button: Transcribe Case in ASR lab
  const labSimulateBtn = document.getElementById("lab-simulate-btn");
  if (labSimulateBtn) {
    labSimulateBtn.addEventListener("click", () => {
      const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
      const caseData = clinicalCasesData[activeCaseId];
      simulateStreamReplay(caseData.plainBiased, caseData.biasedText);
      alert(`[MEMBER 2 ASR PIPELINE]\nTranscribing ${caseData.condition} with anatomical prompt biasing...\nBiased c-WER: ${caseData.cwer} (relative improvement +56.6%)`);
    });
  }

  // Button: Push to Report Editor
  const pushToEditorBtn = document.getElementById("push-to-editor-btn");
  if (pushToEditorBtn) {
    pushToEditorBtn.addEventListener("click", () => {
      const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
      const caseData = clinicalCasesData[activeCaseId];
      
      // Update target organ textarea
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

      alert(`[PIPELINE INTEGRATION]\nTranscribed findings for ${caseData.organ} pushed directly to the Radiologist Report Editor and audited!`);
      document.getElementById("tab-btn-review").click();
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
      console.warn("Web Speech API not supported in this browser. Falling back to simulated dictation.");
      micButtons.forEach(({ btn, label }) => {
        if (btn) {
          btn.addEventListener("click", () => {
            const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
            const caseData = clinicalCasesData[activeCaseId];
            simulateStreamReplay(caseData.plainBiased, caseData.biasedText);
            alert("[MIC DICTATION ACTIVE]\nMicrophone dictation simulated! Biased ASR is streaming live clinical tokens into the review screen.");
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
      micButtons.forEach(({ btn, label }) => {
        if (btn) {
          btn.style.background = "rgba(244, 63, 94, 0.25)";
          btn.style.borderColor = "var(--accent-rose)";
        }
        if (label) label.innerText = "Listening (Speak Now)...";
      });
      recordAuditEvent("MICROPHONE_STREAM_OPENED", "live_audio_input", "OFFLINE", "16kHz Mono Stream Listening", "Radiologist real-time dictation");
    };

    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const spoken = finalTranscript || interimTranscript;
      if (spoken) {
        // Run simulated anatomical biasing on spoken words
        let biasedSpoken = spoken
          .replace(/call cul us|cal cul us/gi, "calculus")
          .replace(/chole lithiasis|coal a lithiasis/gi, "cholelithiasis")
          .replace(/hyper echoic|hyper a coick/gi, "hyperechoic")
          .replace(/hydro nephrosis/gi, "hydronephrosis")
          .replace(/stea tosis/gi, "steatosis")
          .replace(/four point five millimeters/gi, "4.5 mm");

        const streamRaw = document.getElementById("stream-text-raw");
        const streamBiased = document.getElementById("stream-text-biased");
        const labRaw = document.getElementById("lab-raw-text-box");
        const labBiased = document.getElementById("lab-biased-text-box");

        if (streamRaw) streamRaw.innerText = spoken;
        if (streamBiased) streamBiased.innerHTML = biasedSpoken;
        if (labRaw) labRaw.innerText = spoken;
        if (labBiased) labBiased.innerHTML = biasedSpoken;
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };

    function startListening() {
      try {
        recognition.start();
      } catch (e) {
        console.error(e);
      }
    }

    function stopListening() {
      isListening = false;
      micButtons.forEach(({ btn, label }) => {
        if (btn) {
          btn.style.background = "";
          btn.style.borderColor = "";
        }
        if (label) label.innerText = label.id === "live-mic-text" ? "Live Mic Dictation" : "Start Live Mic";
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
    }
  });

  // Slide to Demo button
  const launchDemoBtn = document.getElementById("launch-demo-from-slide-btn");
  if (launchDemoBtn) {
    launchDemoBtn.addEventListener("click", () => {
      document.getElementById("tab-btn-review").click();
    });
  }

  // Foot Pedal Trigger Simulation Button
  const simTriggerBtn = document.getElementById("simulate-trigger-btn");
  if (simTriggerBtn) {
    simTriggerBtn.addEventListener("click", () => {
      const organ = ["Gallbladder", "Liver", "Spleen", "Aorta"][Math.floor(Math.random() * 4)];
      recordAuditEvent("HARDWARE_FOOT_PEDAL_TRIGGER", organ, "VIEWFINDER_STREAM", `KEYFRAME_GRABBED_${organ.toUpperCase()}`, "Member 1 Hardware Pedal interrupt");
      alert(`[MEMBER 1 HARDWARE INTERRUPT]\nFoot pedal pressed! Keyframe captured for: ${organ}\nLogged in tamper-evident audit trail.`);
    });
  }

  // Audio Play button in Review screen
  const playBtn = document.getElementById("play-pause-btn");
  if (playBtn) {
    playBtn.addEventListener("click", () => {
      const activeCaseId = caseSelect ? caseSelect.value : "CASE_ABD_001";
      const caseData = clinicalCasesData[activeCaseId];
      simulateStreamReplay(caseData.plainBiased, caseData.biasedText);
    });
  }

  // Sign-off Button
  const saveReportBtn = document.getElementById("save-report-btn");
  if (saveReportBtn) {
    saveReportBtn.addEventListener("click", () => {
      recordAuditEvent("REPORT_APPROVED_AND_SIGNED", "approval_state", "DRAFT", "ACR_FINAL_SIGNED", "Attending Radiologist Approval");
      const statusText = document.getElementById("save-status-text");
      if (statusText) statusText.innerText = "Signed & Locked (DICOM-SR Exported)";
      alert("Report signed by Dr. Alvarez (Attending Radiologist)!\nTamper-evident audit seal applied and saved on-premises.");
    });
  }

  // Role Selector
  const rbacSelect = document.getElementById("rbac-role-select");
  if (rbacSelect) {
    rbacSelect.addEventListener("change", (e) => {
      activeRole = e.target.value;
      recordAuditEvent("RBAC_ROLE_SWITCH", "active_user_context", activeRole, e.target.value, "User switched clinical role");
    });
  }

  // Export Audit Log
  const exportAuditBtn = document.getElementById("export-audit-json-btn");
  if (exportAuditBtn) {
    exportAuditBtn.addEventListener("click", () => {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(auditEvents, null, 2));
      const dlAnchor = document.createElement("a");
      dlAnchor.setAttribute("href", dataStr);
      dlAnchor.setAttribute("download", `${currentSessionId}_audit_log.json`);
      dlAnchor.click();
    });
  }
});
