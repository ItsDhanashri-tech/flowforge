mermaid.initialize({ startOnLoad: false, theme: "neutral" });
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

document.querySelectorAll(".chip").forEach((c) => (c.onclick = () => ($("idea").value = c.textContent)));

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const idea = $("idea").value.trim();
  if (!idea) return ($("error").textContent = "Please describe your idea first.");
  $("error").textContent = "";
  $("go").disabled = true;
  $("results").classList.add("hidden");
  $("loading").classList.remove("hidden");
  try {
    const res = await fetch("/api/generate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ idea }) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong");
    await render(data);
  } catch (err) {
    $("error").textContent = err.message;
  } finally {
    $("go").disabled = false;
    $("loading").classList.add("hidden");
  }
});

async function render(d) {
  $("title").textContent = d.title;
  $("summary").textContent = d.summary;
  $("steps").innerHTML = (d.steps || []).map((s) => `<li><b>${esc(s.name)}</b>${esc(s.description)}<br><small>⏱ ${esc(s.duration)}</small></li>`).join("");
  $("tasks").innerHTML = (d.tasks || []).map((t) => `<tr><td>${esc(t.task)}</td><td>${esc(t.owner)}</td><td class="p-${esc(t.priority)}">${esc(t.priority)}</td></tr>`).join("");
  $("resources").innerHTML = (d.resources || []).map((r) => `<li><span class="tag">${esc(r.category)}</span><b>${esc(r.item)}</b> — ${esc(r.details)}</li>`).join("");
  $("missing").innerHTML = (d.missing_steps || []).map((m) => `<li>${esc(m)}</li>`).join("");
  $("suggestions").innerHTML = (d.suggestions || []).map((m) => `<li>${esc(m)}</li>`).join("");
  $("results").classList.remove("hidden");
  try {
    const { svg } = await mermaid.render("fc" + Date.now(), d.flowchart);
    $("chart").innerHTML = svg;
  } catch {
    $("chart").innerHTML = (d.steps || []).map((s) => esc(s.name)).join(" → ");
  }
  $("results").scrollIntoView({ behavior: "smooth" });
}
