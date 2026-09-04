const form = document.querySelector("#review-form");
const providerCards = [...document.querySelectorAll(".provider-card")];
const providerInputs = [...document.querySelectorAll("input[name='provider']")];
const modelInput = document.querySelector("#model");
const baseUrlField = document.querySelector("#base-url-field");
const baseUrlInput = document.querySelector("#base-url");
const apiKeyField = document.querySelector("#api-key-field");
const apiKeyInput = document.querySelector("#api-key");
const providerNote = document.querySelector("#provider-note");
const toggleKey = document.querySelector("#toggle-key");
const fileInput = document.querySelector("#file");
const fileLabel = document.querySelector("#file-label");
const dropzone = document.querySelector("#dropzone");
const submitButton = document.querySelector("#submit-button");
const formError = document.querySelector("#form-error");
const emptyState = document.querySelector("#report-empty");
const loading = document.querySelector("#loading");
const reportContent = document.querySelector("#report-content");
const copyButton = document.querySelector("#copy-report");
const downloadButton = document.querySelector("#download-report");
let latestMarkdown = "";

fetch("/health")
  .then((response) => response.json())
  .then((data) => {
    const count = data?.knowledge?.retrieval_case_count;
    if (Number.isInteger(count)) document.querySelector("#knowledge-status").textContent = `${count}个本地案例已就绪`;
  })
  .catch(() => {});

const defaults = {
  openai: { model: "gpt-5-mini", base: "", note: "密钥不会保存；剧本会发送给 OpenAI 进行诊断。" },
  compatible: { model: "", base: "https://", note: "密钥不会保存；剧本会发送给你填写的兼容模型服务。" },
  local: { model: "", base: "http://127.0.0.1:11434/v1", note: "无需云端 API Key；若服务也在本机，剧本不会发送到云端。" },
};

function currentProvider() {
  return providerInputs.find((input) => input.checked)?.value || "openai";
}

function updateProvider() {
  const provider = currentProvider();
  const values = defaults[provider];
  providerCards.forEach((card) => card.classList.toggle("active", card.querySelector("input").checked));
  baseUrlField.classList.toggle("hidden", provider === "openai");
  apiKeyField.classList.toggle("hidden", provider === "local");
  modelInput.value = values.model;
  baseUrlInput.value = values.base;
  apiKeyInput.value = "";
  providerNote.textContent = values.note;
}

providerInputs.forEach((input) => input.addEventListener("change", updateProvider));
toggleKey.addEventListener("click", () => {
  const visible = apiKeyInput.type === "text";
  apiKeyInput.type = visible ? "password" : "text";
  toggleKey.textContent = visible ? "显示" : "隐藏";
});

fileInput.addEventListener("change", () => {
  fileLabel.textContent = fileInput.files[0]?.name || "点击选择，或拖入剧本文件";
});
["dragenter", "dragover"].forEach((name) => dropzone.addEventListener(name, () => dropzone.classList.add("dragging")));
["dragleave", "drop"].forEach((name) => dropzone.addEventListener(name, () => dropzone.classList.remove("dragging")));

function escapeHtml(value) {
  return value.replace(/[&<>"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[char]);
}

function renderMarkdown(markdown) {
  const escaped = escapeHtml(markdown);
  return escaped
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/^\d+\. (.+)$/gm, "<p><strong>$1</strong></p>")
    .replace(/^- (.+)$/gm, "<p>• $1</p>")
    .replace(/\n{2,}/g, "<br />")
    .replace(/\n/g, "<br />");
}

function setLoading(active) {
  submitButton.disabled = active;
  submitButton.querySelector("span").textContent = active ? "正在诊断…" : "开始诊断";
  emptyState.classList.toggle("hidden", active || Boolean(latestMarkdown));
  loading.classList.toggle("hidden", !active);
  reportContent.classList.toggle("hidden", active || !latestMarkdown);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.textContent = "";
  const provider = currentProvider();
  if (!fileInput.files.length && !document.querySelector("#text").value.trim()) {
    formError.textContent = "请上传剧本文件，或粘贴剧本文字。";
    return;
  }
  if (provider !== "local" && !apiKeyInput.value.trim()) {
    formError.textContent = "请填写你自己的 API Key。";
    return;
  }
  if (provider === "compatible" && !baseUrlInput.value.trim()) {
    formError.textContent = "请填写兼容接口地址。";
    return;
  }
  setLoading(true);
  try {
    const response = await fetch("/api/review", { method: "POST", body: new FormData(form) });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || "诊断失败，请稍后重试。");
    latestMarkdown = data.markdown;
    reportContent.innerHTML = renderMarkdown(latestMarkdown);
    copyButton.disabled = false;
    downloadButton.disabled = false;
  } catch (error) {
    latestMarkdown = "";
    formError.textContent = error.message;
  } finally {
    setLoading(false);
  }
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(latestMarkdown);
  copyButton.textContent = "已复制";
  setTimeout(() => (copyButton.textContent = "复制"), 1500);
});

downloadButton.addEventListener("click", () => {
  const blob = new Blob([latestMarkdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "drama-review.md";
  link.click();
  URL.revokeObjectURL(url);
});
