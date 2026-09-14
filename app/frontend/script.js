const API_BASE = "/api/v1";

const transcript = document.getElementById("transcript");
const emptyState = document.getElementById("emptyState");
const form = document.getElementById("composerForm");
const input = document.getElementById("composerInput");
const submitButton = document.getElementById("composerSubmit");

function hideEmptyState() {
  if (emptyState) emptyState.remove();
}

function scrollToBottom() {
  transcript.scrollTop = transcript.scrollHeight;
}

function renderMath(el) {
  if (window.renderMathInElement) {
    renderMathInElement(el, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false },
      ],
      throwOnError: false,
    });
  }
}

function addTurn(role, text) {
  hideEmptyState();

  const turn = document.createElement("article");
  turn.className = `turn turn--${role}`;

  const label = document.createElement("span");
  label.className = "turn__label";
  label.textContent = role === "user" ? "You" : "Tutor";

  const content = document.createElement("div");
  content.className = "turn__content";
  content.textContent = text;

  turn.append(label, content);
  transcript.appendChild(turn);
  renderMath(content);
  scrollToBottom();

  return { turn, content };
}

function addPendingTutorTurn() {
  hideEmptyState();

  const turn = document.createElement("article");
  turn.className = "turn turn--tutor turn--pending";

  const label = document.createElement("span");
  label.className = "turn__label";
  label.textContent = "Tutor";

  const content = document.createElement("div");
  content.className = "turn__content";
  content.textContent = "Considering";

  turn.append(label, content);
  transcript.appendChild(turn);
  scrollToBottom();

  let dotCount = 0;
  const interval = setInterval(() => {
    dotCount = (dotCount + 1) % 4;
    content.textContent = "Considering" + ".".repeat(dotCount);
  }, 400);

  return {
    turn,
    content,
    stop: () => clearInterval(interval),
  };
}

function resolveTutorTurn(pending, text) {
  pending.stop();
  pending.turn.classList.remove("turn--pending");
  pending.content.textContent = text;
  renderMath(pending.content);
  scrollToBottom();
}

function failTutorTurn(pending, detailText, onRetry) {
  pending.stop();
  pending.turn.classList.remove("turn--pending");
  pending.turn.classList.add("turn--error");
  let errorMessage = "The tutor could not be reached. " 
  let errorDetails = ""
  if (detailText) {
    errorDetails = detailText + " ";
  }
  errorMessage += errorDetails;
  pending.content.textContent = errorMessage;

  const retryButton = document.createElement("button");
  retryButton.type = "button";
  retryButton.className = "turn__retry";
  retryButton.textContent = "Retry";
  retryButton.addEventListener("click", () => {
    pending.turn.remove();
    onRetry();
  });

  pending.content.appendChild(retryButton);
  scrollToBottom();
}

async function askTutor(questionText) {
  const pending = addPendingTutorTurn();

  try {
    const response = await fetch(`${API_BASE}/query-tutor/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: questionText }),
    });

    if (!response.ok) {
      const responseDetail = await response.text()
      const detailText = JSON.parse(responseDetail).detail
      throw new Error(`Request failed with status ${response.status}`, {cause: detailText});
    }

    const data = await response.json();
    resolveTutorTurn(pending, data.message);
  } catch (err) {
    failTutorTurn(pending, err.cause, () => askTutor(questionText));
  }
}

function autoGrow() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 128)}px`;
}

input.addEventListener("input", autoGrow);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (!text) return;

  addTurn("user", text);
  askTutor(text);

  input.value = "";
  autoGrow();
  input.focus();
});
