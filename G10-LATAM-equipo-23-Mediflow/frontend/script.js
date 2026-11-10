"use strict";

// Endpoints da API REST em FastAPI
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const scenarios = {
  routine: {
    text: "HOSPITAL SANTA LÚCIA - Consulta de Rotina. Paciente: Ana Maria Sousa, 45 anos. Solicitante: Dr. Paulo Mendes CRM-SP 98765. Exame: Hemograma Completo. Indicação: Acompanhamento de rotina sem queixas atípicas. Paciente relata leve desconforto eventual.",
  },
  urgent: {
    text: "HOSPITAL SANTA LÚCIA - LAUDO DE EXAME RADIOLÓGICO. Paciente: Carlos Eduardo Mendes, 52 anos. Solicitante: Dra. Renata Silveira CRM-SP 145892. Exame: Tomografia de Tórax com contraste. Indicação: Suspeita de embolia pulmonar aguda, dispneia súbita. Achados: Falha de enchimento em artéria pulmonar principal direita compatível com TEP agudo. CONCLUSÃO: Quadro compatível com Tromboembolismo Pulmonar Agudo. Sugere-se correlação clínica urgente.",
  },
  ambiguous: {
    text: "RELATÓRIO CLÍNICO. Paciente com dados incompletos. Relata tonturas sem especificação de frequência ou início. Diagnóstico incerto.",
  },
};

const form = document.querySelector("#triage-form");
const textInput = document.querySelector("#clinical-text");
const fileInput = document.querySelector("#document-file");
const characterCount = document.querySelector("#character-count");
const formError = document.querySelector("#form-error");
const emptyState = document.querySelector("#empty-state");
const resultContent = document.querySelector("#result-content");
const resultStatus = document.querySelector("#result-status");
const priorityCard = document.querySelector("#priority-card");
const selectedScenarioButtons = document.querySelectorAll("[data-scenario]");
const attachmentPreview = document.querySelector("#attachment-preview");
const attachmentImage = document.querySelector("#attachment-image");
const attachmentName = document.querySelector("#attachment-name");
const attachmentDetails = document.querySelector("#attachment-details");
const attachmentOpen = document.querySelector("#attachment-open");
const removeAttachmentButton = document.querySelector("#remove-attachment");

let selectedScenario = null;
let currentFile = null;
let attachmentObjectUrl = null;

const supportedFileTypes = {
  txt: { kind: "text", label: "Arquivo de texto" },
  json: { kind: "json", label: "Arquivo JSON" },
  jpg: { kind: "image", label: "Imagem" },
  jpeg: { kind: "image", label: "Imagem" },
  png: { kind: "image", label: "Imagem" },
  webp: { kind: "image", label: "Imagem" },
  gif: { kind: "image", label: "Imagem" },
  pdf: { kind: "pdf", label: "Documento PDF" },
};

const priorityLabels = {
  Rotina: "ROTINA",
  Urgente: "PRIORIDADE",
  Indefinido: "REVISÃO HUMANA",
};

function setScenarioButton(activeScenario) {
  selectedScenarioButtons.forEach((button) => {
    const isSelected = button.dataset.scenario === activeScenario;
    button.classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-pressed", String(isSelected));
  });
}

function getFileType(file) {
  const extension = file.name.split(".").pop()?.toLocaleLowerCase("pt-BR");
  return supportedFileTypes[extension] ?? null;
}

function formatFileSize(size) {
  return size < 1024 * 1024
    ? `${Math.max(1, Math.round(size / 1024))} KB`
    : `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function showFileError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function updateAttachmentPreview(file, type) {
  if (attachmentObjectUrl) {
    URL.revokeObjectURL(attachmentObjectUrl);
    attachmentObjectUrl = null;
  }

  currentFile = file;
  attachmentName.textContent = file.name;
  attachmentDetails.textContent = `${type.label} · ${formatFileSize(file.size)}`;
  attachmentImage.hidden = true;
  attachmentOpen.hidden = true;
  attachmentImage.removeAttribute("src");
  attachmentOpen.removeAttribute("href");

  if (type.kind === "image" || type.kind === "pdf") {
    attachmentObjectUrl = URL.createObjectURL(file);
    if (type.kind === "image") {
      attachmentImage.src = attachmentObjectUrl;
      attachmentImage.hidden = false;
    } else {
      attachmentOpen.href = attachmentObjectUrl;
      attachmentOpen.hidden = false;
    }
  }

  attachmentPreview.hidden = false;
}

function clearAttachment() {
  if (attachmentObjectUrl) {
    URL.revokeObjectURL(attachmentObjectUrl);
    attachmentObjectUrl = null;
  }

  currentFile = null;
  fileInput.value = "";
  attachmentPreview.hidden = true;
  attachmentImage.hidden = true;
  attachmentImage.removeAttribute("src");
  attachmentOpen.hidden = true;
  attachmentOpen.removeAttribute("href");
}

// Renderiza a resposta obtida da API no painel
function renderApiResponse(apiData) {
  const extraidos = apiData.dados_extraidos;
  const roteamento = apiData.decisao_roteamento;
  const classificacao = extraidos.classificacao;

  let priorityClass = "routine";
  if (classificacao.nivel_prioridade === "Urgente") priorityClass = "urgent";
  if (roteamento.requer_auditoria_humana) priorityClass = "review";

  emptyState.hidden = true;
  resultContent.hidden = false;
  priorityCard.dataset.priority = priorityClass;

  document.querySelector("#priority-label").textContent = priorityLabels[classificacao.nivel_prioridade] || "TRIAGEM";
  document.querySelector("#confidence").textContent = `Confiança: ${Math.round(classificacao.score_confianca * 100)}%`;
  document.querySelector("#result-title").textContent = `Destino: ${roteamento.destino_principal}`;
  document.querySelector("#result-summary").textContent = roteamento.justificativa_roteamento;
  document.querySelector("#review-text").textContent = roteamento.requer_auditoria_humana
    ? "Encaminhamento necessário para Auditoria Humana (HitL)."
    : "Documento processado automaticamente sem necessidade de intervenção manual.";
  
  document.querySelector("#document-type").textContent = classificacao.tipo_documento;
  
  const totalEntidades = (extraidos.medicamentos?.length || 0) + (extraidos.exames_solicitados?.length || 0);
  document.querySelector("#entity-count").textContent = `${totalEntidades} ${totalEntidades === 1 ? "item" : "itens"}`;
  
  document.querySelector("#json-output").textContent = JSON.stringify(apiData, null, 2);

  resultStatus.classList.toggle("is-review", roteamento.requer_auditoria_humana);
  resultStatus.classList.add("is-ready");
  resultStatus.innerHTML = '<span class="status-dot" aria-hidden="true"></span>Processado via API MediFlow';
  resultContent.setAttribute("aria-label", "Resultado da triagem processado pela API");
}

// Chamada assíncrona ao Backend FastAPI
async function sendToTriageApi(text) {
  const formData = new FormData();
  formData.append("texto", text);

  const response = await fetch(`${API_BASE_URL}/triage/text`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail?.motivo || errorData.detail?.erro || "Erro no processamento da API.");
  }

  return await response.json();
}

textInput.addEventListener("input", () => {
  characterCount.textContent = `${textInput.value.length} / 6000`;
  formError.hidden = true;
  selectedScenario = null;
  setScenarioButton(null);
});

selectedScenarioButtons.forEach((button) => {
  button.setAttribute("aria-pressed", "false");
  button.addEventListener("click", () => {
    selectedScenario = button.dataset.scenario;
    textInput.value = scenarios[selectedScenario].text;
    characterCount.textContent = `${textInput.value.length} / 6000`;
    formError.hidden = true;
    setScenarioButton(selectedScenario);
    textInput.focus();
  });
});

fileInput.addEventListener("change", async () => {
  const [file] = fileInput.files ?? [];
  if (!file) return;

  const type = getFileType(file);
  if (!type) {
    showFileError("Formato não suportado. Escolha TXT, JSON, JPG, PNG ou PDF.");
    fileInput.value = "";
    return;
  }

  const textFile = type.kind === "text" || type.kind === "json";
  if (textFile) {
    try {
      const text = await file.text();
      textInput.value = text.slice(0, 6000);
      textInput.dispatchEvent(new Event("input", { bubbles: true }));
      updateAttachmentPreview(file, type);
    } catch {
      showFileError("Não foi possível ler o arquivo.");
    }
    return;
  }

  updateAttachmentPreview(file, type);
});

removeAttachmentButton.addEventListener("click", () => {
  clearAttachment();
  formError.hidden = true;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textInput.value.trim();

  if (!text) {
    showFileError("Escolha um cenário ou cole um texto médico antes de analisar.");
    textInput.focus();
    return;
  }

  // Feedback visual de carregamento
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.querySelector("span").textContent = "Analisando com IA e Guardrails...";

  try {
    const apiResult = await sendToTriageApi(text);
    renderApiResponse(apiResult);
    document.querySelector("#results-heading").focus({ preventScroll: true });
  } catch (err) {
    showFileError(`Falha na Segurança/API: ${err.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector("span").textContent = "Analisar demonstração";
  }
});
