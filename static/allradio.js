const answerRadioHolder = document.getElementById("answer");

// add event listener
answerRadioHolder.addEventListener("click", function (e) {
  if (e.target.tagName === "LABEL") {
    // set the checked to true

    e.target.control.checked = true;
  }

  document.getElementById("answer").submit();
});
