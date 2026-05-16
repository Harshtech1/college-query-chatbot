const faqDataset = JSON.parse(document.getElementById("faq-data").textContent);
const faqForm = document.getElementById("faq-form");
const faqReset = document.getElementById("faq-reset");
const uploadForm = document.getElementById("document-upload-form");
const uploadStatus = document.getElementById("upload-status");

const fields = {
  id: document.getElementById("faq-id"),
  question: document.getElementById("faq-question"),
  answer: document.getElementById("faq-answer"),
  category: document.getElementById("faq-category"),
  priority: document.getElementById("faq-priority"),
  keywords: document.getElementById("faq-keywords"),
  active: document.getElementById("faq-active"),
};

function resetForm() {
  fields.id.value = "";
  fields.question.value = "";
  fields.answer.value = "";
  fields.category.value = "General";
  fields.priority.value = 1;
  fields.keywords.value = "";
  fields.active.checked = true;
}

faqReset.addEventListener("click", resetForm);

document.querySelectorAll(".edit-faq").forEach((button) => {
  button.addEventListener("click", () => {
    const faqId = Number(button.dataset.faqId);
    const faq = faqDataset.find((item) => item.id === faqId);
    if (!faq) {
      return;
    }

    fields.id.value = faq.id;
    fields.question.value = faq.question;
    fields.answer.value = faq.answer;
    fields.category.value = faq.category;
    fields.priority.value = faq.priority;
    fields.keywords.value = (faq.keywords || []).join(", ");
    fields.active.checked = faq.is_active;
    fields.question.focus();
  });
});

document.querySelectorAll(".delete-faq").forEach((button) => {
  button.addEventListener("click", async () => {
    const faqId = Number(button.dataset.faqId);
    if (!window.confirm("Delete this FAQ entry?")) {
      return;
    }

    const response = await fetch(`/api/admin/faqs/${faqId}`, { method: "DELETE" });
    if (response.ok) {
      window.location.reload();
      return;
    }

    const payload = await response.json();
    window.alert(payload.error || "Could not delete the FAQ entry.");
  });
});

faqForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    question: fields.question.value.trim(),
    answer: fields.answer.value.trim(),
    category: fields.category.value.trim(),
    priority: Number(fields.priority.value || 1),
    keywords: fields.keywords.value.split(",").map((value) => value.trim()).filter(Boolean),
    is_active: fields.active.checked,
  };

  const faqId = fields.id.value;
  const url = faqId ? `/api/admin/faqs/${faqId}` : "/api/admin/faqs";
  const method = faqId ? "PATCH" : "POST";

  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (response.ok) {
    window.location.reload();
    return;
  }

  const result = await response.json();
  window.alert(result.error || "Could not save the FAQ entry.");
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  uploadStatus.textContent = "Uploading and processing document...";

  const formData = new FormData(uploadForm);
  const response = await fetch("/api/admin/documents", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  if (response.ok) {
    uploadStatus.textContent = `Imported ${result.title} with ${result.chunk_count} chunks.`;
    window.setTimeout(() => window.location.reload(), 800);
    return;
  }

  uploadStatus.textContent = result.error || "Upload failed.";
});

