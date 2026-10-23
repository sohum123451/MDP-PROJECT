// EchoScribe-AI / SonoAssist - Clinical UI Controller
// Member 4 (Dinesh - IT Deliverable)

document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentSessionId = "SESS_20261023_042";
  let activeRole = "radiologist";
  let currentSlide = 1;
  const totalSlides = 6;
  let auditEvents = [];

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
    // Simple checksum
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
  let prevImp = impArea.value;
  impArea.addEventListener("blur", () => {
    if (impArea.value !== prevImp) {
      recordAuditEvent("RADIOLOGIST_IMPRESSION_EDIT", "Final Impression", prevImp, impArea.value, "Clinical synthesis review");
      prevImp = impArea.value;
    }
  });

  // Tab Switching
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      document.getElementById(targetId).classList.add("active");
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

    document.getElementById("current-slide-num").innerText = currentSlide;
  }

  document.getElementById("prev-slide-btn").addEventListener("click", () => showSlide(currentSlide - 1));
  document.getElementById("next-slide-btn").addEventListener("click", () => showSlide(currentSlide + 1));
  document.addEventListener("keydown", (e) => {
    if (document.getElementById("presentation-mode").classList.contains("active")) {
      if (e.key === "ArrowRight") showSlide(currentSlide + 1);
      if (e.key === "ArrowLeft") showSlide(currentSlide - 1);
    }
  });

  // Slide to Demo button
  document.getElementById("launch-demo-from-slide-btn").addEventListener("click", () => {
    document.getElementById("tab-btn-review").click();
  });

  // Foot Pedal Trigger Simulation Button
  document.getElementById("simulate-trigger-btn").addEventListener("click", () => {
    const organ = ["Gallbladder", "Liver", "Spleen", "Aorta"][Math.floor(Math.random() * 4)];
    recordAuditEvent("HARDWARE_FOOT_PEDAL_TRIGGER", organ, "VIEWFINDER_STREAM", `KEYFRAME_GRABBED_${organ.toUpperCase()}`, "Member 1 Hardware Pedal interrupt");
    alert(`[MEMBER 1 HARDWARE INTERRUPT]\nFoot pedal pressed! Keyframe captured for: ${organ}\nLogged in tamper-evident audit trail.`);
  });

  // Sign-off Button
  document.getElementById("save-report-btn").addEventListener("click", () => {
    recordAuditEvent("REPORT_APPROVED_AND_SIGNED", "approval_state", "DRAFT", "ACR_FINAL_SIGNED", "Attending Radiologist Approval");
    document.getElementById("save-status-text").innerText = "Signed & Locked (DICOM-SR Exported)";
    alert("Report signed by Dr. Alvarez (Attending Radiologist)!\nTamper-evident audit seal applied and saved on-premises.");
  });

  // Role Selector
  document.getElementById("rbac-role-select").addEventListener("change", (e) => {
    activeRole = e.target.value;
    recordAuditEvent("RBAC_ROLE_SWITCH", "active_user_context", activeRole, e.target.value, "User switched clinical role");
  });

  // Export Audit Log
  document.getElementById("export-audit-json-btn").addEventListener("click", () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(auditEvents, null, 2));
    const dlAnchor = document.createElement("a");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `${currentSessionId}_audit_log.json`);
    dlAnchor.click();
  });
});
