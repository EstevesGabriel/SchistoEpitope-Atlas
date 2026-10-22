document.addEventListener("DOMContentLoaded", () => {
  const tooltip = document.getElementById("heatmap-tooltip");
  let pointer = { x: 0, y: 0 };

  function positionTooltip() {
    if (tooltip.hidden) return;
    const pad = 12;
    const rect = tooltip.getBoundingClientRect();
    let x = pointer.x + 18;
    let y = pointer.y + 18;
    if (x + rect.width > window.innerWidth - pad) x = pointer.x - rect.width - 18;
    if (x < pad) x = Math.max(pad, Math.min(pointer.x + 18, window.innerWidth - rect.width - pad));
    if (y + rect.height > window.innerHeight - pad) y = pointer.y - rect.height - 18;
    if (y < pad) y = Math.max(pad, Math.min(pointer.y + 18, window.innerHeight - rect.height - pad));
    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
  }

  document.querySelectorAll(".heatmap-plot").forEach((plot) => {
    const script = document.getElementById(plot.dataset.figureId);
    if (!script || !window.Plotly) return;
    const figure = JSON.parse(script.textContent);
    plot.addEventListener("mousemove", (event) => {
      pointer = { x: event.clientX, y: event.clientY };
      positionTooltip();
    });
    Plotly.newPlot(plot, figure.data, figure.layout, {
      responsive: true,
      displaylogo: false,
      modeBarButtonsToRemove: ["select2d", "lasso2d"],
    }).then(() => {
      resizeHeatmaps();
      plot.on("plotly_hover", (eventData) => {
        const point = eventData.points && eventData.points[0];
        if (!point || !point.customdata) return;
        const [protein, peptide, score] = point.customdata;
        const measureLabel = plot.dataset.measureLabel || "PSA Score";
        const scoreText = score === null || score === undefined || Number.isNaN(Number(score))
          ? "Not available"
          : Number(score).toLocaleString("en-US", { maximumFractionDigits: 2 });
        tooltip.innerHTML = `<div><strong>Protein:</strong> ${escapeHtml(protein)}</div><div><strong>Peptide:</strong> ${escapeHtml(peptide)}</div><div><strong>${escapeHtml(measureLabel)}:</strong> ${escapeHtml(scoreText)}</div>`;
        tooltip.hidden = false;
        positionTooltip();
      });
      plot.on("plotly_unhover", () => { tooltip.hidden = true; });
    });
  });

  function resizeHeatmaps() {
    document.querySelectorAll(".heatmap-plot").forEach((plot) => {
      if (!plot.data || !window.Plotly) return;
      const rowCount = plot.data[0]?.y?.length || 0;
      const contentHeight = 250 + rowCount * 28;
      const viewportHeight = Math.floor(window.innerHeight * 0.72);
      const height = Math.max(500, Math.min(1200, Math.max(contentHeight, viewportHeight)));
      Plotly.relayout(plot, { height }).then(() => Plotly.Plots.resize(plot));
    });
  }
  window.addEventListener("resize", resizeHeatmaps);
  document.addEventListener("fullscreenchange", resizeHeatmaps);

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  }
});
