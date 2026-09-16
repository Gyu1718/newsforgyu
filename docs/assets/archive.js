"use strict";

// Entries remain readable without JavaScript or an extra data request.
const filters = document.querySelector("#filters");
if (filters) {
  const query = document.querySelector("#query");
  const month = document.querySelector("#month");
  const entries = [...document.querySelectorAll(".item")];
  const count = document.querySelector("#count");
  const empty = document.querySelector("#empty");
  const list = document.querySelector("#briefings");
  const normalize = (value) => value.normalize("NFC").toLocaleLowerCase("ko-KR");
  const searchable = entries.map((entry) => normalize(entry.textContent));
  function filter() {
    const words = normalize(query.value).trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    entries.forEach((entry, index) => {
      const matches = (!month.value || entry.dataset.month === month.value)
        && words.every((word) => searchable[index].includes(word));
      entry.hidden = !matches;
      if (matches) shown += 1;
    });
    count.textContent = `${entries.length}개 중 ${shown}개 브리핑`;
    empty.hidden = shown !== 0;
    list.hidden = shown === 0;
  }
  query.addEventListener("input", filter);
  month.addEventListener("change", filter);
  filters.addEventListener("submit", (event) => event.preventDefault());
  document.querySelector("#reset").addEventListener("click", () => {
    query.value = "";
    month.value = "";
    filter();
    query.focus();
  });
  filters.hidden = false;
  filter();
}
