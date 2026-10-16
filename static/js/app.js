/**
 * ResuMetrics Minimalist UI - Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // State variables
  let currentFile = null;
  let activeInputMode = "file"; // 'file' or 'text'
  let latestAnalysisData = null;

  // DOM Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const fileSelectedBadge = document.getElementById("file-selected-badge");
  const selectedFilename = document.getElementById("selected-filename");
  const selectedFilesize = document.getElementById("selected-filesize");
  const removeFileBtn = document.getElementById("remove-file-btn");

  const tabModeFile = document.getElementById("tab-mode-file");
  const tabModeText = document.getElementById("tab-mode-text");
  const fileUploadMode = document.getElementById("file-upload-mode");
  const textPasteMode = document.getElementById("text-paste-mode");
  const resumeRawTextarea = document.getElementById("resume-raw-textarea");

  const toggleJdBtn = document.getElementById("toggle-jd-btn");
  const jdContainer = document.getElementById("jd-container");
  const jdChevron = document.getElementById("jd-chevron");
  const jdTextarea = document.getElementById("jd-textarea");
  const insertSampleJdBtn = document.getElementById("insert-sample-jd-btn");

  const analyzeBtn = document.getElementById("analyze-btn");
  const analyzeBtnText = document.getElementById("analyze-btn-text");
  const analyzeBtnIcon = document.getElementById("analyze-btn-icon");
  const analyzeSpinner = document.getElementById("analyze-spinner");
  const clearBtn = document.getElementById("clear-btn");
  const loadSampleBtn = document.getElementById("load-sample-btn");

  const resultsSection = document.getElementById("results-section");
  const themeToggle = document.getElementById("theme-toggle");
  const themeIcon = document.getElementById("theme-icon");

  const printReportBtn = document.getElementById("print-report-btn");
  const copySummaryBtn = document.getElementById("copy-summary-btn");
  const exportJsonBtn = document.getElementById("export-json-btn");

  // Init Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // -------------------------------------------------------------
  // Theme Toggle (Dark / Light)
  // -------------------------------------------------------------
  const savedTheme = localStorage.getItem("resumetrics_theme") || "dark";
  setTheme(savedTheme);

  themeToggle.addEventListener("click", () => {
    const isDark = document.documentElement.classList.contains("dark");
    setTheme(isDark ? "light" : "dark");
  });

  function setTheme(mode) {
    if (mode === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
      themeIcon.setAttribute("data-lucide", "sun");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.add("light");
      themeIcon.setAttribute("data-lucide", "moon");
    }
    localStorage.setItem("resumetrics_theme", mode);
    if (window.lucide) lucide.createIcons();
  }

  // -------------------------------------------------------------
  // Input Mode Tabs (File Upload vs Raw Text)
  // -------------------------------------------------------------
  tabModeFile.addEventListener("click", () => {
    activeInputMode = "file";
    tabModeFile.className = "px-3 py-1.5 text-xs font-medium rounded-lg bg-zinc-800 text-white border border-zinc-700 transition";
    tabModeText.className = "px-3 py-1.5 text-xs font-medium rounded-lg text-zinc-400 hover:text-zinc-200 transition";
    fileUploadMode.classList.remove("hidden");
    textPasteMode.classList.add("hidden");
  });

  tabModeText.addEventListener("click", () => {
    activeInputMode = "text";
    tabModeText.className = "px-3 py-1.5 text-xs font-medium rounded-lg bg-zinc-800 text-white border border-zinc-700 transition";
    tabModeFile.className = "px-3 py-1.5 text-xs font-medium rounded-lg text-zinc-400 hover:text-zinc-200 transition";
    textPasteMode.classList.remove("hidden");
    fileUploadMode.classList.add("hidden");
  });

  // -------------------------------------------------------------
  // Drag & Drop File Handling
  // -------------------------------------------------------------
  dropzone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  });

  function handleFileSelection(file) {
    const ext = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx", "txt", "md"].includes(ext)) {
      showToast("Please upload a PDF, DOCX, or TXT file.", "warning");
      return;
    }
    currentFile = file;
    selectedFilename.textContent = file.name;
    selectedFilesize.textContent = formatBytes(file.size);
    dropzone.classList.add("hidden");
    fileSelectedBadge.classList.remove("hidden");
  }

  removeFileBtn.addEventListener("click", () => {
    currentFile = null;
    fileInput.value = "";
    fileSelectedBadge.classList.add("hidden");
    dropzone.classList.remove("hidden");
  });

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  // -------------------------------------------------------------
  // Job Description Toggle & Sample Insert
  // -------------------------------------------------------------
  toggleJdBtn.addEventListener("click", () => {
    const isHidden = jdContainer.classList.contains("hidden");
    if (isHidden) {
      jdContainer.classList.remove("hidden");
      jdChevron.style.transform = "rotate(180deg)";
    } else {
      jdContainer.classList.add("hidden");
      jdChevron.style.transform = "rotate(0deg)";
    }
  });

  insertSampleJdBtn.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/sample");
      const data = await res.json();
      if (data.sample_jd) {
        jdTextarea.value = data.sample_jd;
        showToast("Sample job description loaded.", "success");
      }
    } catch {
      showToast("Could not load sample job description.", "error");
    }
  });

  // -------------------------------------------------------------
  // Load Sample Resume Button
  // -------------------------------------------------------------
  loadSampleBtn.addEventListener("click", async () => {
    try {
      showToast("Loading demo sample...", "info");
      const res = await fetch("/api/sample");
      const data = await res.json();

      tabModeText.click();
      resumeRawTextarea.value = data.sample_resume;
      jdTextarea.value = data.sample_jd;
      if (jdContainer.classList.contains("hidden")) {
        toggleJdBtn.click();
      }

      // Auto-trigger analysis for seamless preview
      setTimeout(() => {
        analyzeBtn.click();
      }, 300);
    } catch (e) {
      showToast("Failed to fetch sample data.", "error");
    }
  });

  // Clear button
  clearBtn.addEventListener("click", () => {
    currentFile = null;
    fileInput.value = "";
    fileSelectedBadge.classList.add("hidden");
    dropzone.classList.remove("hidden");
    resumeRawTextarea.value = "";
    jdTextarea.value = "";
    resultsSection.classList.add("hidden");
    showToast("Inputs cleared.", "info");
  });

  // -------------------------------------------------------------
  // Run Analysis Call
  // -------------------------------------------------------------
  analyzeBtn.addEventListener("click", async () => {
    const formData = new FormData();
    const jdText = jdTextarea.value.trim();
    if (jdText) {
      formData.append("job_description", jdText);
    }

    if (activeInputMode === "file") {
      if (!currentFile) {
        showToast("Please select a resume file first or switch to Paste Text.", "warning");
        return;
      }
      formData.append("file", currentFile);
    } else {
      const text = resumeRawTextarea.value.trim();
      if (!text) {
        showToast("Please paste your resume text.", "warning");
        return;
      }
      formData.append("resume_text", text);
    }

    // Set Loading State
    setAnalyzingState(true);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.detail || data.error || "Analysis failed.");
      }

      latestAnalysisData = data;
      renderResults(data);
      resultsSection.classList.remove("hidden");
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
      showToast("Resume analysis complete!", "success");

    } catch (err) {
      showToast(err.message || "Failed to analyze resume.", "error");
    } finally {
      setAnalyzingState(false);
    }
  });

  function setAnalyzingState(loading) {
    if (loading) {
      analyzeBtn.disabled = true;
      analyzeBtnText.textContent = "Analyzing...";
      analyzeBtnIcon.classList.add("hidden");
      analyzeSpinner.classList.remove("hidden");
    } else {
      analyzeBtn.disabled = false;
      analyzeBtnText.textContent = "Analyze Resume";
      analyzeBtnIcon.classList.remove("hidden");
      analyzeSpinner.classList.add("hidden");
    }
  }

  // -------------------------------------------------------------
  // Render Results to UI
  // -------------------------------------------------------------
  function renderResults(data) {
    const analysis = data.analysis;
    const jobMatch = data.job_match;

    // 1. Overall Score & Gauge
    const score = analysis.score || 0;
    const scoreRing = document.getElementById("score-ring");
    const scoreNum = document.getElementById("score-number");
    const scoreGrade = document.getElementById("score-grade");

    // Animate score number
    animateValue(scoreNum, 0, score, 800);

    // Circumference = 2 * PI * 40 ≈ 251.2
    const circumference = 251.2;
    const offset = circumference - (score / 100) * circumference;
    scoreRing.style.strokeDashoffset = offset;

    // Color based on score
    if (score >= 80) {
      scoreRing.setAttribute("class", "score-circle text-emerald-500");
      scoreGrade.className = "px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    } else if (score >= 65) {
      scoreRing.setAttribute("class", "score-circle text-blue-500");
      scoreGrade.className = "px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20";
    } else if (score >= 50) {
      scoreRing.setAttribute("class", "score-circle text-amber-500");
      scoreGrade.className = "px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20";
    } else {
      scoreRing.setAttribute("class", "score-circle text-rose-500");
      scoreGrade.className = "px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20";
    }
    scoreGrade.textContent = analysis.grade || "Ready";

    document.getElementById("result-filename").textContent = data.filename || "Resume";

    // 2. Candidate Information
    const contact = analysis.contact_info || {};
    document.getElementById("candidate-name").textContent = contact.name || "Candidate Resume";

    const contactChips = document.getElementById("contact-chips");
    contactChips.innerHTML = "";
    if (contact.email) {
      contactChips.innerHTML += `<span class="flex items-center gap-1 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800"><i data-lucide="mail" class="w-3 h-3 text-zinc-400"></i> ${contact.email}</span>`;
    }
    if (contact.phone) {
      contactChips.innerHTML += `<span class="flex items-center gap-1 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800"><i data-lucide="phone" class="w-3 h-3 text-zinc-400"></i> ${contact.phone}</span>`;
    }
    if (contact.linkedin) {
      contactChips.innerHTML += `<span class="flex items-center gap-1 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800"><i data-lucide="linkedin" class="w-3 h-3 text-blue-400"></i> LinkedIn</span>`;
    }
    if (contact.github) {
      contactChips.innerHTML += `<span class="flex items-center gap-1 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800"><i data-lucide="github" class="w-3 h-3 text-purple-400"></i> GitHub</span>`;
    }

    // 3. KPI Cards
    const kpiMatch = document.getElementById("kpi-match");
    const kpiMatchSub = document.getElementById("kpi-match-sub");
    if (jobMatch && jobMatch.has_job_description) {
      kpiMatch.textContent = `${jobMatch.match_score}%`;
      kpiMatchSub.textContent = jobMatch.match_grade;
      kpiMatch.className = "text-xl font-bold text-emerald-400 tracking-tight";
    } else {
      kpiMatch.textContent = "N/A";
      kpiMatchSub.textContent = "No JD provided";
      kpiMatch.className = "text-xl font-bold text-zinc-400 tracking-tight";
    }

    document.getElementById("kpi-skills").textContent = analysis.skills.total_count || 0;
    document.getElementById("kpi-skills-sub").textContent = `${Object.keys(analysis.skills.by_category || {}).length} categories`;

    const impactPct = analysis.impact_analysis.metric_bullet_percentage || 0;
    document.getElementById("kpi-impact").textContent = `${impactPct}%`;
    document.getElementById("kpi-impact-sub").textContent = `${analysis.impact_analysis.bullets_with_metrics_count || 0} of ${analysis.impact_analysis.total_bullets || 0} bullets`;

    document.getElementById("kpi-verbs").textContent = analysis.action_verbs.power_verbs_count || 0;
    document.getElementById("kpi-verbs-sub").textContent = `${analysis.action_verbs.bullets_starting_with_power_ratio || 0}% bullets lead with action`;

    // 4. Tab 1: Section Checklist & Formatting
    renderChecklist(analysis);

    // 5. Tab 2: Skills & JD Match
    renderSkillsAndJD(analysis, jobMatch);

    // 6. Tab 3: Bullet Impact & Verbs
    renderImpactAndVerbs(analysis);

    // 7. Tab 4: Fixes & Recommendations
    renderRecommendations(analysis.recommendations || []);

    // 8. Tab 5: Raw Parsed Text
    document.getElementById("raw-text-display").textContent = data.raw_text_preview || "No preview available.";

    if (window.lucide) lucide.createIcons();
  }

  function renderChecklist(analysis) {
    const secContainer = document.getElementById("section-checklist");
    const fmtContainer = document.getElementById("format-checklist");
    const breakdownContainer = document.getElementById("score-breakdown-bars");

    const detected = analysis.sections.detected || [];
    const standardSections = ["summary", "experience", "education", "skills", "projects"];

    secContainer.innerHTML = standardSections.map(sec => {
      const has = detected.includes(sec);
      return `
        <div class="flex items-center justify-between p-2 rounded bg-zinc-950/40 border border-zinc-800/60">
          <span class="capitalize font-medium text-zinc-300">${sec} Section</span>
          ${has
            ? `<span class="flex items-center gap-1 text-emerald-400"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i> Detected</span>`
            : `<span class="flex items-center gap-1 text-zinc-500"><i data-lucide="x-circle" class="w-3.5 h-3.5"></i> Missing</span>`}
        </div>
      `;
    }).join("");

    // Format & Health checklist
    const overview = analysis.overview || {};
    const readability = analysis.readability || {};
    fmtContainer.innerHTML = `
      <div class="flex items-center justify-between p-2 rounded bg-zinc-950/40 border border-zinc-800/60">
        <span class="text-zinc-300">Word Count & Length</span>
        <span class="font-mono text-zinc-400">${overview.word_count || 0} words (~${overview.estimated_pages || 1} pg)</span>
      </div>
      <div class="flex items-center justify-between p-2 rounded bg-zinc-950/40 border border-zinc-800/60">
        <span class="text-zinc-300">Readability Score</span>
        <span class="font-mono text-emerald-400">${readability.flesch_reading_ease || 0}/100 (${readability.reading_level || 'Good'})</span>
      </div>
      <div class="flex items-center justify-between p-2 rounded bg-zinc-950/40 border border-zinc-800/60">
        <span class="text-zinc-300">Machine Readable (Non-Scanned)</span>
        <span class="flex items-center gap-1 text-emerald-400"><i data-lucide="check" class="w-3.5 h-3.5"></i> Clean Text</span>
      </div>
      <div class="flex items-center justify-between p-2 rounded bg-zinc-950/40 border border-zinc-800/60">
        <span class="text-zinc-300">Avg Sentence Length</span>
        <span class="font-mono text-zinc-400">${readability.avg_sentence_length_words || 0} words</span>
      </div>
    `;

    // Score Breakdown Progress Bars
    const bd = analysis.score_breakdown || {};
    breakdownContainer.innerHTML = Object.entries(bd).map(([key, val]) => {
      const pct = Math.round((val.score / val.max) * 100);
      const label = key.replace(/_/g, " ").toUpperCase();
      return `
        <div>
          <div class="flex justify-between text-xs mb-1">
            <span class="text-zinc-400 font-mono text-[11px]">${label}</span>
            <span class="font-medium text-zinc-200">${val.score} / ${val.max} pts</span>
          </div>
          <div class="w-full bg-zinc-950 rounded-full h-1.5 overflow-hidden">
            <div class="bg-emerald-500 h-1.5 rounded-full transition-all duration-700" style="width: ${pct}%"></div>
          </div>
        </div>
      `;
    }).join("");
  }

  function renderSkillsAndJD(analysis, jobMatch) {
    const jdPanel = document.getElementById("jd-match-panel");
    if (jobMatch && jobMatch.has_job_description) {
      jdPanel.classList.remove("hidden");
      document.getElementById("jd-match-badge").textContent = `${jobMatch.match_score}% Match`;
      document.getElementById("matched-skills-count").textContent = jobMatch.matching_skills.length;
      document.getElementById("missing-skills-count").textContent = jobMatch.missing_skills.length;

      const matchedChips = document.getElementById("matched-skills-chips");
      matchedChips.innerHTML = jobMatch.matching_skills.length > 0
        ? jobMatch.matching_skills.map(s => `<span class="px-2 py-0.5 rounded text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">${s}</span>`).join("")
        : `<span class="text-xs text-zinc-500">None detected</span>`;

      const missingChips = document.getElementById("missing-skills-chips");
      missingChips.innerHTML = jobMatch.missing_skills.length > 0
        ? jobMatch.missing_skills.map(s => `<span class="px-2 py-0.5 rounded text-xs bg-rose-500/10 text-rose-300 border border-rose-500/30 flex items-center gap-1"><i data-lucide="plus" class="w-3 h-3"></i> ${s}</span>`).join("")
        : `<span class="text-xs text-emerald-400">All required skills present!</span>`;

      const kwChips = document.getElementById("missing-keywords-chips");
      kwChips.innerHTML = (jobMatch.missing_keywords || []).map(kw =>
        `<span class="px-1.5 py-0.5 rounded text-[11px] bg-zinc-800 text-zinc-400 border border-zinc-700 font-mono">${kw}</span>`
      ).join("");
    } else {
      jdPanel.classList.add("hidden");
    }

    // Categorized Skills
    const catContainer = document.getElementById("categorized-skills-container");
    const byCat = analysis.skills.by_category || {};
    if (Object.keys(byCat).length === 0) {
      catContainer.innerHTML = `<p class="text-xs text-zinc-500">No categorized skills recognized.</p>`;
      return;
    }

    catContainer.innerHTML = Object.entries(byCat).map(([category, skills]) => `
      <div>
        <h4 class="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2 font-mono">${category} (${skills.length})</h4>
        <div class="flex flex-wrap gap-1.5">
          ${skills.map(skill => `<span class="px-2 py-1 rounded-md text-xs bg-zinc-950 border border-zinc-800 text-zinc-200">${skill}</span>`).join("")}
        </div>
      </div>
    `).join("");
  }

  function renderImpactAndVerbs(analysis) {
    // Power verbs
    const powerChips = document.getElementById("power-verbs-chips");
    const verbs = analysis.action_verbs.power_verbs_list || [];
    powerChips.innerHTML = verbs.length > 0
      ? verbs.map(v => `<span class="px-2 py-0.5 rounded text-xs bg-amber-500/10 text-amber-300 border border-amber-500/30">${v}</span>`).join("")
      : `<span class="text-xs text-zinc-500">No dominant power verbs identified.</span>`;

    // Weak verbs
    const weakList = document.getElementById("weak-verbs-list");
    const weaks = analysis.action_verbs.weak_phrases_detected || [];
    weakList.innerHTML = weaks.length > 0
      ? weaks.map(w => `
        <div class="flex items-center justify-between p-2 rounded bg-zinc-950/40 border border-rose-900/30 text-rose-300">
          <span>Found phrase: "${w.phrase}"</span>
          <span class="text-[11px] font-mono opacity-80">${w.count}x</span>
        </div>
      `).join("")
      : `<div class="p-2 rounded bg-zinc-950/40 border border-zinc-800 text-emerald-400 flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5"></i> No passive cliches detected!</div>`;

    // Impact Bullets
    const impactList = document.getElementById("impact-bullets-list");
    const samples = analysis.impact_analysis.samples || [];
    impactList.innerHTML = samples.length > 0
      ? samples.map(s => `
        <div class="p-3 rounded-lg bg-zinc-950/40 border border-zinc-800 text-xs">
          <p class="text-zinc-200 mb-1.5">${escapeHtml(s.text)}</p>
          <div class="flex flex-wrap gap-1">
            ${s.metrics_found.map(m => `<span class="px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono text-[11px]">${escapeHtml(m)}</span>`).join("")}
          </div>
        </div>
      `).join("")
      : `<p class="text-xs text-zinc-500">No bullets with clear numbers or percentages found. Add numbers like '%', '$', or team scale.</p>`;

    // Bullet Rewrites
    const rewritesList = document.getElementById("bullet-rewrites-list");
    const rewrites = analysis.bullet_suggestions || [];
    rewritesList.innerHTML = rewrites.length > 0
      ? rewrites.map(r => `
        <div class="p-3.5 rounded-lg bg-zinc-950/50 border border-zinc-800 text-xs space-y-2">
          <div>
            <span class="text-[11px] uppercase tracking-wider text-rose-400 font-mono font-semibold">Current Bullet:</span>
            <p class="text-zinc-400 line-through mt-0.5">${escapeHtml(r.original)}</p>
          </div>
          <div>
            <span class="text-[11px] uppercase tracking-wider text-emerald-400 font-mono font-semibold">Recommended STAR Polish:</span>
            <p class="text-emerald-200 mt-0.5 font-medium">${escapeHtml(r.suggestion)}</p>
          </div>
        </div>
      `).join("")
      : `<p class="text-xs text-zinc-500">Your bullet points are well-structured with action verbs and metrics.</p>`;
  }

  function renderRecommendations(recs) {
    const container = document.getElementById("recommendations-container");
    if (!recs || recs.length === 0) {
      container.innerHTML = `<p class="text-xs text-zinc-500">No immediate issues detected!</p>`;
      return;
    }

    container.innerHTML = recs.map(rec => {
      let badgeStyle = "bg-zinc-800 text-zinc-300 border-zinc-700";
      let icon = "alert-circle";

      if (rec.severity === "critical") {
        badgeStyle = "bg-rose-500/10 text-rose-400 border-rose-500/30";
        icon = "alert-octagon";
      } else if (rec.severity === "high") {
        badgeStyle = "bg-amber-500/10 text-amber-400 border-amber-500/30";
        icon = "alert-triangle";
      } else if (rec.severity === "positive") {
        badgeStyle = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
        icon = "check-circle";
      }

      return `
        <div class="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800 flex items-start gap-3.5">
          <div class="p-2 rounded-lg ${badgeStyle} border flex-shrink-0 mt-0.5">
            <i data-lucide="${icon}" class="w-4 h-4"></i>
          </div>
          <div class="space-y-1 flex-1">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-zinc-200">${escapeHtml(rec.title)}</span>
              <span class="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${badgeStyle} border">${rec.category}</span>
            </div>
            <p class="text-xs text-zinc-400 leading-relaxed">${escapeHtml(rec.message)}</p>
            ${rec.fix ? `<p class="text-xs text-emerald-400/90 font-medium pt-1"><span class="text-zinc-500">How to fix:</span> ${escapeHtml(rec.fix)}</p>` : ''}
          </div>
        </div>
      `;
    }).join("");
  }

  // -------------------------------------------------------------
  // Tabs Switching for Results
  // -------------------------------------------------------------
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      tabButtons.forEach(b => {
        b.className = "tab-btn px-3 py-2 font-medium rounded-t-lg border-b-2 border-transparent text-zinc-400 hover:text-zinc-200 transition";
      });
      btn.className = "tab-btn px-3 py-2 font-medium rounded-t-lg border-b-2 border-emerald-500 text-emerald-400 transition";

      tabContents.forEach(c => {
        if (c.id === targetId) {
          c.classList.remove("hidden");
        } else {
          c.classList.add("hidden");
        }
      });

      if (window.lucide) lucide.createIcons();
    });
  });

  // -------------------------------------------------------------
  // Export Actions
  // -------------------------------------------------------------
  printReportBtn.addEventListener("click", () => {
    window.print();
  });

  copySummaryBtn.addEventListener("click", () => {
    if (!latestAnalysisData) return;
    const a = latestAnalysisData.analysis;
    const summary = `
RESUMETRICS ATS AUDIT REPORT
Candidate: ${a.contact_info?.name || 'N/A'}
Overall ATS Score: ${a.score}/100 (${a.grade})
Word Count: ${a.overview?.word_count || 0}
Recognized Skills: ${a.skills?.total_count || 0}
Measurable Impact Bullets: ${a.impact_analysis?.metric_bullet_percentage || 0}%
Power Verbs Identified: ${a.action_verbs?.power_verbs_count || 0}
Top Skills: ${(a.skills?.all_skills || []).slice(0, 15).join(', ')}
    `.trim();

    navigator.clipboard.writeText(summary).then(() => {
      showToast("Audit summary copied to clipboard!", "success");
    }).catch(() => {
      showToast("Unable to copy to clipboard.", "error");
    });
  });

  exportJsonBtn.addEventListener("click", () => {
    if (!latestAnalysisData) return;
    const jsonStr = JSON.stringify(latestAnalysisData, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume_analysis_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Downloaded JSON analysis file.", "info");
  });

  // -------------------------------------------------------------
  // Helpers: Toast & Animation
  // -------------------------------------------------------------
  function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-msg");
    const toastIcon = document.getElementById("toast-icon");

    toastMsg.textContent = message;
    if (type === "success") {
      toastIcon.setAttribute("data-lucide", "check-circle");
      toastIcon.className = "w-4 h-4 text-emerald-400";
    } else if (type === "warning") {
      toastIcon.setAttribute("data-lucide", "alert-triangle");
      toastIcon.className = "w-4 h-4 text-amber-400";
    } else if (type === "error") {
      toastIcon.setAttribute("data-lucide", "alert-octagon");
      toastIcon.className = "w-4 h-4 text-rose-400";
    } else {
      toastIcon.setAttribute("data-lucide", "info");
      toastIcon.className = "w-4 h-4 text-blue-400";
    }

    if (window.lucide) lucide.createIcons();

    toast.classList.remove("translate-y-16", "opacity-0");
    toast.classList.add("translate-y-0", "opacity-100");

    setTimeout(() => {
      toast.classList.remove("translate-y-0", "opacity-100");
      toast.classList.add("translate-y-16", "opacity-0");
    }, 3200);
  }

  function animateValue(element, start, end, duration) {
    if (start === end) return;
    const range = end - start;
    let current = start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    const timer = setInterval(() => {
      current += increment;
      element.textContent = current;
      if (current === end) {
        clearInterval(timer);
      }
    }, stepTime);
  }

  function escapeHtml(text) {
    if (!text) return "";
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
