const form = document.getElementById("question-form");
const history = document.getElementById("question-history");
const textarea = form.querySelector("textarea");

function scrollToBottom() {
  history.scrollTop = history.scrollHeight;
}

scrollToBottom();

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = form.querySelector("button");
  const label = button.querySelector(".btn-label");
  button.disabled = true;
  label.textContent = "Thinking...";

  try {
    const response = await fetch("/questions", {
      method: "POST",
      body: new FormData(form),
    });
    const html = await response.text();

    const emptyChat = history.querySelector(".empty-chat");
    if (emptyChat) emptyChat.remove();

    history.insertAdjacentHTML("beforeend", html);
    form.reset();
    scrollToBottom();
  } finally {
    button.disabled = false;
    label.textContent = "Ask";
  }
});

textarea.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});
