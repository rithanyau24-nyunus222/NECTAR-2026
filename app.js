/**
 * NECTAR'26 — CUTE & WHIMSICAL APPLICATION CONTROLLER
 * Multi-page scrapbook router, real-time debounced simulation engine client,
 * milestone tracking (BRS/FRS/ERS), cute confetti sparkles, and pastel chart drawing.
 */

document.addEventListener("DOMContentLoaded", () => {
  // ==========================================================================
  // 1. CUTE MULTI-PAGE ROUTER (SPA Navigation)
  // ==========================================================================
  const navTabs = document.querySelectorAll(".cute-tab");
  const pageViews = document.querySelectorAll(".scrapbook-page");
  const linkBtns = document.querySelectorAll("[data-page]");

  function switchPage(pageId) {
    pageViews.forEach((page) => page.classList.remove("active"));
    navTabs.forEach((tab) => tab.classList.remove("active"));

    const targetPage = document.getElementById(`page-${pageId}`);
    if (targetPage) {
      targetPage.classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    const activeTab = document.querySelector(`.cute-tab[data-page="${pageId}"]`);
    if (activeTab) {
      activeTab.classList.add("active");
    }

    window.location.hash = pageId;

    // Redraw chart if navigating to analytics
    if (pageId === "analytics" && lastSimulationData) {
      setTimeout(() => {
        drawAnalyticsChart(lastSimulationData.yearly_projections);
      }, 50);
    }
  }

  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      switchPage(tab.dataset.page);
    });
  });

  linkBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      switchPage(btn.dataset.page);
    });
  });

  // Direct Button Links
  const btnLaunchSimHero = document.getElementById("btnLaunchSimHero");
  if (btnLaunchSimHero) btnLaunchSimHero.addEventListener("click", () => switchPage("simulator"));

  const btnReadGuideHero = document.getElementById("btnReadGuideHero");
  if (btnReadGuideHero) btnReadGuideHero.addEventListener("click", () => switchPage("guide"));

  const btnTopSimulate = document.getElementById("btnTopSimulate");
  if (btnTopSimulate) btnTopSimulate.addEventListener("click", () => switchPage("simulator"));

  // Initial Route
  const initialHash = window.location.hash.replace("#", "") || "home";
  switchPage(initialHash);

  // ==========================================================================
  // 2. SIMULATION CONTROLS & STATE
  // ==========================================================================
  const simAge = document.getElementById("simAge");
  const valSimAge = document.getElementById("valSimAge");
  const simSalary = document.getElementById("simSalary");
  const valSimSalary = document.getElementById("valSimSalary");
  const simOA = document.getElementById("simOA");
  const simSA = document.getElementById("simSA");
  const simIncrement = document.getElementById("simIncrement");
  const valSimIncrement = document.getElementById("valSimIncrement");
  const simHorizon = document.getElementById("simHorizon");
  const valSimHorizon = document.getElementById("valSimHorizon");
  const btnRunStudioSim = document.getElementById("btnRunStudioSim");

  // Output Elements (Studio)
  const studioTotalCpf = document.getElementById("studioTotalCpf");
  const studioOaBal = document.getElementById("studioOaBal");
  const studioSaBal = document.getElementById("studioSaBal");
  const studioInterestVal = document.getElementById("studioInterestVal");
  const studioBonusText = document.getElementById("studioBonusText");

  // Housing Elements
  const housePrice = document.getElementById("housePrice");
  const houseYear = document.getElementById("houseYear");
  const valHouseYear = document.getElementById("valHouseYear");
  const houseMortgage = document.getElementById("houseMortgage");
  const valHouseMortgage = document.getElementById("valHouseMortgage");
  const houseToggleBuffer = document.getElementById("houseToggleBuffer");
  const loanPills = document.querySelectorAll(".loan-pill");

  const housingVerdictChip = document.getElementById("housingVerdictChip");
  const housingVerdictNarrative = document.getElementById("housingVerdictNarrative");
  const houseReqDownpayment = document.getElementById("houseReqDownpayment");
  const houseUsableOA = document.getElementById("houseUsableOA");
  const houseMeterFill = document.getElementById("houseMeterFill");
  const houseShortfallText = document.getElementById("houseShortfallText");

  // Milestones Elements
  const statusBrs = document.getElementById("statusBrs");
  const statusFrs = document.getElementById("statusFrs");
  const statusErs = document.getElementById("statusErs");

  // Analytics Elements
  const analyticsChartCanvas = document.getElementById("analyticsChart");
  const analyticsChartCtx = analyticsChartCanvas ? analyticsChartCanvas.getContext("2d") : null;
  const analyticsTableBody = document.getElementById("analyticsTableBody");

  let currentDownpaymentPct = 0.20;
  let debounceTimer = null;
  let lastSimulationData = null;

  // Format currency
  const formatSGD = (num) => {
    return new Intl.NumberFormat("en-SG", {
      style: "currency",
      currency: "SGD",
      maximumFractionDigits: 0,
    }).format(num);
  };

  // Update Slider Labels
  function updateSliderLabels() {
    if (valSimAge) valSimAge.textContent = `${simAge.value} yrs`;
    if (valSimSalary) valSimSalary.textContent = `$${Number(simSalary.value).toLocaleString()}`;
    if (valSimIncrement) valSimIncrement.textContent = `${Number(simIncrement.value).toFixed(1)}%`;
    if (valSimHorizon) valSimHorizon.textContent = `${simHorizon.value} Years`;
    if (valHouseYear) valHouseYear.textContent = `Year ${houseYear.value}`;
    if (valHouseMortgage) valHouseMortgage.textContent = `$${Number(houseMortgage.value).toLocaleString()}/mo`;
  }

  // Handle Loan Pills (HDB vs Bank)
  loanPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      loanPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentDownpaymentPct = parseFloat(pill.dataset.pct);
      triggerSimulation();
    });
  });

  // Build Payload
  function buildPayload() {
    const age = parseInt(simAge.value, 10);
    const salary = parseFloat(simSalary.value);
    const oa = parseFloat(simOA.value) || 0;
    const sa = parseFloat(simSA.value) || 0;
    const increment = parseFloat(simIncrement.value) / 100.0;
    const horizon = parseInt(simHorizon.value, 10);

    const property = parseFloat(housePrice.value) || 0;
    const pYear = parseInt(houseYear.value, 10);
    const mortgage = parseFloat(houseMortgage.value) || 0;
    const retainBuffer = houseToggleBuffer.checked ? 20000.0 : 0.0;

    return {
      age: age,
      monthly_salary: salary,
      current_oa: oa,
      current_sa: sa,
      current_ma: 15000.0,
      simulation_years: horizon,
      annual_salary_increment: increment,
      ow_ceiling: 8000.0,
      property_price: property,
      downpayment_pct: currentDownpaymentPct,
      purchase_year: pYear,
      monthly_mortgage_oa: mortgage,
      retain_oa_buffer: retainBuffer,
    };
  }

  // Trigger Simulation with Debounce
  function triggerSimulation() {
    updateSliderLabels();
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      await fetchSimulation();
    }, 150);
  }

  // API Call to /api/v1/simulate
  async function fetchSimulation() {
    const payload = buildPayload();
    try {
      const response = await fetch("/api/v1/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      lastSimulationData = data;
      renderAllData(data);
    } catch (err) {
      console.error("Simulation request error:", err);
    }
  }

  // Render Data
  function renderAllData(data) {
    const { summary, housing_assessment, yearly_projections, milestones } = data;

    // 1. Studio Snapshot
    if (studioTotalCpf) studioTotalCpf.textContent = formatSGD(summary.final_total_cpf);
    if (studioOaBal) studioOaBal.textContent = formatSGD(summary.final_oa_balance);
    if (studioSaBal) studioSaBal.textContent = formatSGD(summary.final_sa_balance);
    if (studioInterestVal) studioInterestVal.textContent = `+${formatSGD(summary.total_interest_earned)}`;
    if (studioBonusText) studioBonusText.textContent = `Includes ${formatSGD(summary.total_bonus_interest_earned)} in extra 1% bonus yield!`;

    // 2. Housing Assessment
    if (houseReqDownpayment) houseReqDownpayment.textContent = formatSGD(housing_assessment.required_downpayment);
    if (houseUsableOA) houseUsableOA.textContent = formatSGD(housing_assessment.usable_oa);
    if (housingVerdictNarrative) housingVerdictNarrative.textContent = housing_assessment.recommendation;

    if (housingVerdictChip) {
      housingVerdictChip.className = "verdict-chip";
      if (housing_assessment.status === "SUFFICIENT_OA_WITH_BUFFER") {
        housingVerdictChip.textContent = "SUFFICIENT • $20k BUFFER INTACT 🌸";
        housingVerdictChip.classList.add("chip-success");
        if (houseShortfallText) {
          houseShortfallText.textContent = `Surplus OA: ${formatSGD(housing_assessment.surplus)} (3.5% yield kept!)`;
          houseShortfallText.style.color = "#15803d";
        }
      } else if (housing_assessment.status === "SUFFICIENT_OA_BUFFER_SACRIFICED") {
        housingVerdictChip.textContent = "SUFFICIENT • BUFFER REDUCED ⚠️";
        housingVerdictChip.classList.add("chip-warning");
        if (houseShortfallText) {
          houseShortfallText.textContent = `Surplus OA: ${formatSGD(housing_assessment.surplus)} (Buffer partially used)`;
          houseShortfallText.style.color = "#854d0e";
        }
      } else if (housing_assessment.status === "CASH_SHORTFALL") {
        housingVerdictChip.textContent = "CASH SHORTFALL DETECTED 🚨";
        housingVerdictChip.classList.add("chip-danger");
        if (houseShortfallText) {
          houseShortfallText.textContent = `Shortfall: ${formatSGD(housing_assessment.shortfall)} (Prepare cash top-up)`;
          houseShortfallText.style.color = "#b91c1c";
        }
      } else {
        housingVerdictChip.textContent = "NO PROPERTY CONFIGURED 🏡";
        housingVerdictChip.classList.add("chip-warning");
      }
    }

    const req = housing_assessment.required_downpayment;
    const usable = housing_assessment.usable_oa;
    let pct = req > 0 ? Math.min(100, Math.round((usable / req) * 100)) : 100;
    if (houseMeterFill) houseMeterFill.style.width = `${pct}%`;

    // 3. Milestones
    if (milestones) {
      if (statusBrs) {
        if (milestones.brs_achieved_year) {
          statusBrs.textContent = `Achieved: Year ${milestones.brs_achieved_year} 🌟`;
          statusBrs.style.color = "#15803d";
        } else {
          statusBrs.textContent = "Beyond Simulation Horizon";
          statusBrs.style.color = "#64748b";
        }
      }

      if (statusFrs) {
        if (milestones.frs_achieved_year) {
          statusFrs.textContent = `Achieved: Year ${milestones.frs_achieved_year} 🏆`;
          statusFrs.style.color = "#15803d";
        } else {
          statusFrs.textContent = "Target in Progress ⏳";
          statusFrs.style.color = "#64748b";
        }
      }

      if (statusErs) {
        if (milestones.ers_achieved_year) {
          statusErs.textContent = `Achieved: Year ${milestones.ers_achieved_year} 🚀`;
          statusErs.style.color = "#15803d";
        } else {
          statusErs.textContent = "Beyond Year 5 Horizon";
          statusErs.style.color = "#64748b";
        }
      }
    }

    // 4. Analytics Table
    if (analyticsTableBody) {
      analyticsTableBody.innerHTML = "";
      yearly_projections.forEach((p) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>Year ${p.year}</strong></td>
          <td>${p.age}</td>
          <td>${formatSGD(p.monthly_salary)}</td>
          <td style="color: #0284c7; font-weight: 700;">${formatSGD(p.oa_balance)}</td>
          <td style="color: #d97706; font-weight: 700;">${formatSGD(p.sa_balance)}</td>
          <td style="color: #1e293b; font-weight: 800;">${formatSGD(p.total_cpf)}</td>
          <td>${formatSGD(p.annual_interest_oa)}</td>
          <td>${formatSGD(p.annual_interest_sa)}</td>
          <td style="color: #16a34a; font-weight: 700;">+${formatSGD(p.annual_bonus_interest)}</td>
        `;
        analyticsTableBody.appendChild(tr);
      });
    }

    // 5. Draw Pastel Chart
    drawAnalyticsChart(yearly_projections);
  }

  // Draw Cute Pastel Growth Chart
  function drawAnalyticsChart(projections) {
    if (!projections || projections.length === 0 || !analyticsChartCanvas) return;

    const canvas = analyticsChartCanvas;
    const ctx = analyticsChartCtx;
    const dpr = window.devicePixelRatio || 1;

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    ctx.clearRect(0, 0, w, h);

    const padding = { top: 25, right: 30, bottom: 35, left: 60 };
    const chartW = w - padding.left - padding.right;
    const chartH = h - padding.top - padding.bottom;

    const maxVal = Math.max(...projections.map((p) => p.total_cpf)) * 1.15;
    const minVal = 0;

    const getX = (index) => padding.left + (index / (projections.length - 1)) * chartW;
    const getY = (val) => padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

    // Horizontal Grid Lines
    ctx.strokeStyle = "#e2e8f0";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);

    for (let i = 0; i <= 4; i++) {
      const y = padding.top + (chartH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(w - padding.right, y);
      ctx.stroke();

      const labelVal = Math.round(maxVal - (maxVal / 4) * i);
      ctx.fillStyle = "#64748b";
      ctx.font = "bold 11px 'Plus Jakarta Sans', sans-serif";
      ctx.textAlign = "right";
      ctx.fillText(`$${Math.round(labelVal / 1000)}k`, padding.left - 10, y + 4);
    }
    ctx.setLineDash([]);

    // X Axis Labels
    projections.forEach((p, idx) => {
      const x = getX(idx);
      ctx.fillStyle = "#1e293b";
      ctx.font = "bold 11px 'DynaPuff', cursive";
      ctx.textAlign = "center";
      ctx.fillText(`Yr ${p.year}`, x, h - 10);
    });

    // Curve Drawer
    function drawCuteCurve(points, strokeColor, fillColor = null) {
      if (points.length === 0) return;

      if (fillColor) {
        ctx.beginPath();
        ctx.moveTo(getX(0), getY(points[0]));
        for (let i = 1; i < points.length; i++) {
          const xc = (getX(i) + getX(i - 1)) / 2;
          const yc = (getY(points[i]) + getY(points[i - 1])) / 2;
          ctx.quadraticCurveTo(getX(i - 1), getY(points[i - 1]), xc, yc);
        }
        ctx.lineTo(getX(points.length - 1), getY(points[points.length - 1]));
        ctx.lineTo(getX(points.length - 1), padding.top + chartH);
        ctx.lineTo(getX(0), padding.top + chartH);
        ctx.closePath();
        ctx.fillStyle = fillColor;
        ctx.fill();
      }

      ctx.beginPath();
      ctx.moveTo(getX(0), getY(points[0]));
      for (let i = 1; i < points.length; i++) {
        const xc = (getX(i) + getX(i - 1)) / 2;
        const yc = (getY(points[i]) + getY(points[i - 1])) / 2;
        ctx.quadraticCurveTo(getX(i - 1), getY(points[i - 1]), xc, yc);
      }
      ctx.lineTo(getX(points.length - 1), getY(points[points.length - 1]));
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 3.5;
      ctx.lineCap = "round";
      ctx.stroke();

      // Cute dots with white border and black rim
      points.forEach((val, idx) => {
        const x = getX(idx);
        const y = getY(val);
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = strokeColor;
        ctx.fill();
        ctx.strokeStyle = "#1e293b";
        ctx.lineWidth = 2.5;
        ctx.stroke();
      });
    }

    // 1. Total CPF (Cherry Pink fill + stroke)
    const totalGrad = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
    totalGrad.addColorStop(0, "rgba(244, 63, 94, 0.15)");
    totalGrad.addColorStop(1, "rgba(244, 63, 94, 0.0)");
    drawCuteCurve(projections.map((p) => p.total_cpf), "#f43f5e", totalGrad);

    // 2. Special Account (Golden Honey)
    drawCuteCurve(projections.map((p) => p.sa_balance), "#d97706");

    // 3. Ordinary Account (Sky Blue)
    drawCuteCurve(projections.map((p) => p.oa_balance), "#0284c7");
  }

  // Event Listeners for Controls
  [simAge, simSalary, simIncrement, simHorizon, housePrice, houseYear, houseMortgage].forEach((elem) => {
    if (elem) elem.addEventListener("input", triggerSimulation);
  });

  [simOA, simSA, houseToggleBuffer].forEach((elem) => {
    if (elem) elem.addEventListener("change", triggerSimulation);
  });

  if (btnRunStudioSim) {
    btnRunStudioSim.addEventListener("click", () => {
      fetchSimulation();
    });
  }

  // Initial Load
  updateSliderLabels();
  fetchSimulation();
});
