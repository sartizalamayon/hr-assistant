const tabButtons = document.querySelectorAll(".tab-button");
const panels = {
  employee: document.getElementById("employee-form"),
  hr: document.getElementById("hr-form"),
};

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    button.classList.add("active");
    Object.entries(panels).forEach(([key, panel]) => {
      panel.classList.toggle("hidden", key !== button.dataset.tab);
    });
  });
});

document.getElementById("google-sso").addEventListener("click", () => {
  document.getElementById("sso-note").classList.remove("hidden");
});
