const centerFootballImage = document.querySelector(".center-svg-container");

centerFootballImage.addEventListener("mouseover", () => {
  centerFootballImage.classList.add("animating");
});

centerFootballImage.addEventListener("animationend", () => {
  centerFootballImage.classList.remove("animating");
});