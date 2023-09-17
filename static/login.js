const logInSubmit = document.querySelector("#form-submit");

logInSubmit.addEventListener("mouseover", () => {
  logInSubmit.classList.add("animating");
});

logInSubmit.addEventListener("animationend", () => {
  logInSubmit.classList.remove("animating");
});
