  // FILTER DROPDOWN
  const toggleBtn = document.querySelector(".filter-toggle");
  const dropdown = document.querySelector(".filter-dropdown");
  toggleBtn.addEventListener("click", () => {
    dropdown.classList.toggle("active");
  });

  // SLIDER LOGIC
  const slides = document.querySelectorAll(".slides img");
  const slideContainer = document.querySelector(".slides");
  const prevBtn = document.querySelector(".prev");
  const nextBtn = document.querySelector(".next");
  const dots = document.querySelectorAll(".dot");

  let index = 0;

  function showSlide(i) {
    if (i >= slides.length) index = 0;
    if (i < 0) index = slides.length - 1;
    slideContainer.style.transform = `translateX(-${index * 100}%)`;
    updateDots();
  }

  function updateDots() {
    dots.forEach((dot, i) => {
      dot.classList.toggle("active", i === index);
    });
  }

  nextBtn.addEventListener("click", () => {
    index++;
    showSlide(index);
  });

  prevBtn.addEventListener("click", () => {
    index--;
    showSlide(index);
  });

  dots.forEach((dot, i) => {
    dot.addEventListener("click", () => {
      index = i;
      showSlide(index);
    });
  });

  // Auto slide every 4 seconds
  setInterval(() => {
    index++;
    showSlide(index);
  }, 4000);

  // Placeholder typing animation
  const searchInput = document.querySelector('.search-bar');
  const placeholderText = "Search PG or Hostel...";
  let i = 0;

  function typePlaceholder() {
    if (i <= placeholderText.length) {
      searchInput.setAttribute('placeholder', placeholderText.slice(0, i));
      i++;
      setTimeout(typePlaceholder, 100); // speed of typing
    } else {
      setTimeout(() => { i = 0; typePlaceholder(); }, 2000); // restart after 2s
    }
  }
  typePlaceholder();