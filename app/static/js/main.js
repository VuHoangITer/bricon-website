// ==================== FLOATING BUTTONS ====================
window.addEventListener("scroll", function () {
  const floatingButtons = document.querySelector(".floating-buttons");
  if (floatingButtons) {
    floatingButtons.style.display = "flex"; // luôn hiển thị
  }
});

// ==================== ANIMATE ON SCROLL ====================
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
};

const observer = new IntersectionObserver(function (entries) {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("animate-on-scroll");
    }
  });
}, observerOptions);

// Observe all product cards and blog cards
document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".product-card, .blog-card");
  cards.forEach((card) => {
    observer.observe(card);
  });
});

// ==================== AUTO DISMISS ALERTS ====================
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 3000);
  });
});

// ==================== SEARCH FORM VALIDATION ====================
document.addEventListener("DOMContentLoaded", function () {
  const searchForms = document.querySelectorAll('form[action*="search"]');
  searchForms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      const input = form.querySelector('input[name="q"], input[name="search"]');
      if (input && input.value.trim() === "") {
        e.preventDefault();
        alert("Vui lòng nhập từ khóa tìm kiếm");
      }
    });
  });
});

// ==================== IMAGE LAZY LOADING ====================
if ("loading" in HTMLImageElement.prototype) {
  const images = document.querySelectorAll("img[data-src]");
  images.forEach((img) => {
    img.src = img.dataset.src;
  });
} else {
  // Fallback for browsers that don't support lazy loading
  const script = document.createElement("script");
  script.src =
    "https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js";
  document.body.appendChild(script);
}

// ==================== SMOOTH SCROLL - FIXED ====================
// Chỉ áp dụng cho links KHÔNG phải Bootstrap tabs
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('a[href*="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      // BỎ QUA nếu là Bootstrap tab hoặc có data-bs-toggle
      if (this.hasAttribute("data-bs-toggle")) {
        return;
      }

      const href = this.getAttribute("href");

      // BỎ QUA nếu href chỉ là "#" đơn thuần
      if (href === "#") {
        return;
      }

      // Kiểm tra nếu target element tồn tại
      const targetId = href.includes("#") ? href.split("#")[1] : null;

      if (targetId) {
        const target = document.getElementById(targetId);

        // Chỉ scroll nếu element thực sự tồn tại
        if (target) {
          e.preventDefault();
          const offsetTop = target.offsetTop - 120;
          window.scrollTo({
            top: offsetTop,
            behavior: "smooth",
          });
        }
      }
    });
  });
});

// ==================== SCROLL TO TOP WITH PROGRESS ====================
(function () {
  const scrollToTopBtn = document.getElementById("scrollToTop");
  if (!scrollToTopBtn) return;

  const progressCircle = scrollToTopBtn.querySelector("circle.progress");
  const radius = progressCircle.r.baseVal.value;
  const circumference = 2 * Math.PI * radius;

  // Set initial progress circle
  progressCircle.style.strokeDasharray = circumference;
  progressCircle.style.strokeDashoffset = circumference;

  // Update progress on scroll
  function updateProgress() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight =
      document.documentElement.scrollHeight -
      document.documentElement.clientHeight;
    const scrollPercentage = (scrollTop / scrollHeight) * 100;

    // Update progress circle
    const offset = circumference - (scrollPercentage / 100) * circumference;
    progressCircle.style.strokeDashoffset = offset;

    // Show/hide button
    if (scrollTop > 300) {
      scrollToTopBtn.classList.add("show");
    } else {
      scrollToTopBtn.classList.remove("show");
    }
  }

  // Smooth scroll to top
  scrollToTopBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // Listen to scroll event
  let ticking = false;
  window.addEventListener("scroll", function () {
    if (!ticking) {
      window.requestAnimationFrame(function () {
        updateProgress();
        ticking = false;
      });
      ticking = true;
    }
  });

  // Initial check
  updateProgress();
})();

// ==================== BANNER LAZY LOAD + RESPONSIVE (INTEGRATED) ====================
document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.getElementById("bannerCarousel");
  if (!carousel) return; // Không có banner thì bỏ qua

  // ✅ 1. LAZY LOAD BANNER IMAGES
  const lazyBannerImages = carousel.querySelectorAll(
    '.banner-img[loading="lazy"]'
  );

  if ("IntersectionObserver" in window && lazyBannerImages.length > 0) {
    const bannerObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target;
            const parent = img.closest(".carousel-item");

            // Add loading class for skeleton effect
            if (parent) parent.classList.add("loading");

            // Load image
            img.onload = function () {
              img.classList.add("loaded");
              if (parent) parent.classList.remove("loading");
              observer.unobserve(img);
            };

            // Trigger load if data-src exists
            if (img.dataset.src) {
              img.src = img.dataset.src;
            } else {
              img.classList.add("loaded"); // Image already has src
              if (parent) parent.classList.remove("loading");
            }
          }
        });
      },
      {
        rootMargin: "100px", // Preload 100px before viewport
      }
    );

    lazyBannerImages.forEach((img) => bannerObserver.observe(img));
  } else {
    // Fallback: immediately mark as loaded
    lazyBannerImages.forEach((img) => img.classList.add("loaded"));
  }

  // ✅ 2. PRELOAD ADJACENT SLIDES
  carousel.addEventListener("slide.bs.carousel", function (e) {
    const slides = carousel.querySelectorAll(".carousel-item");
    const nextIndex = e.to;

    // Preload current slide
    const currentSlide = slides[nextIndex];
    if (currentSlide) {
      const currentImg = currentSlide.querySelector(".banner-img");
      if (currentImg && !currentImg.classList.contains("loaded")) {
        currentImg.classList.add("loaded");
      }
    }

    // Preload adjacent slides (prev/next)
    const prevIndex = nextIndex - 1 < 0 ? slides.length - 1 : nextIndex - 1;
    const nextSlideIndex = nextIndex + 1 >= slides.length ? 0 : nextIndex + 1;

    [prevIndex, nextSlideIndex].forEach((index) => {
      const slide = slides[index];
      if (slide) {
        const img = slide.querySelector(".banner-img");
        if (img && !img.classList.contains("loaded")) {
          img.classList.add("loaded");
        }
      }
    });
  });

  // ✅ 3. PAUSE ON HOVER (Desktop only)
  if (window.innerWidth >= 768) {
    let isHovering = false;

    carousel.addEventListener("mouseenter", function () {
      isHovering = true;
      const bsCarousel = bootstrap.Carousel.getInstance(carousel);
      if (bsCarousel) bsCarousel.pause();
    });

    carousel.addEventListener("mouseleave", function () {
      if (isHovering) {
        isHovering = false;
        const bsCarousel = bootstrap.Carousel.getInstance(carousel);
        if (bsCarousel) bsCarousel.cycle();
      }
    });
  }

  // ✅ 4. PAUSE ON TOUCH (Mobile)
  carousel.addEventListener("touchstart", function () {
    const bsCarousel = bootstrap.Carousel.getInstance(carousel);
    if (bsCarousel) bsCarousel.pause();
  });

  carousel.addEventListener("touchend", function () {
    const bsCarousel = bootstrap.Carousel.getInstance(carousel);
    if (bsCarousel) {
      setTimeout(() => bsCarousel.cycle(), 3000); // Resume after 3s
    }
  });

  // ✅ 5. KEYBOARD NAVIGATION
  carousel.addEventListener("keydown", function (e) {
    const bsCarousel = bootstrap.Carousel.getInstance(carousel);
    if (!bsCarousel) return;

    if (e.key === "ArrowLeft") {
      e.preventDefault();
      bsCarousel.prev();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      bsCarousel.next();
    }
  });

  // ✅ 6. RESPECT REDUCED MOTION
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    carousel.setAttribute("data-bs-interval", "false");
    carousel.querySelectorAll(".carousel-item").forEach((item) => {
      item.style.transition = "none";
    });
  }

  // ✅ 7. SMOOTH SCROLL FOR BANNER CTA
  const bannerCTAs = carousel.querySelectorAll(
    '.carousel-caption .btn[href^="#"]'
  );
  bannerCTAs.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href && href !== "#") {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      }
    });
  });

  // ✅ 8. FALLBACK: Force load all images after 3s
  setTimeout(() => {
    const unloadedImages = carousel.querySelectorAll(
      ".banner-img:not(.loaded)"
    );
    unloadedImages.forEach((img) => {
      img.classList.add("loaded");
      const parent = img.closest(".carousel-item");
      if (parent) parent.classList.remove("loading");
    });
  }, 3000);

  // ✅ 9. ANALYTICS: Track banner views (if GA4/GTM exists)
  if (typeof gtag !== "undefined") {
    carousel.addEventListener("slid.bs.carousel", function (e) {
      const activeSlide = carousel.querySelector(".carousel-item.active");
      const bannerTitle = activeSlide?.querySelector("h1, h2")?.textContent;

      gtag("event", "banner_view", {
        event_category: "Banner",
        event_label: bannerTitle || `Slide ${e.to + 1}`,
        value: e.to + 1,
      });
    });
  }

  // ✅ 10. PRECONNECT TO CDN (if using Cloudinary/ImgIX)
  const firstBanner = carousel.querySelector(".banner-img");
  if (firstBanner) {
    const src = firstBanner.getAttribute("src") || "";
    if (src.includes("cloudinary.com") || src.includes("imgix.net")) {
      const preconnect = document.createElement("link");
      preconnect.rel = "preconnect";
      preconnect.href = src.includes("cloudinary")
        ? "https://res.cloudinary.com"
        : "https://assets.imgix.net";
      preconnect.crossOrigin = "anonymous";
      document.head.appendChild(preconnect);
    }
  }
});

// ==================== RESPONSIVE IMAGE SOURCE HANDLER ====================
// Force browser to re-evaluate <picture> on resize (debounced)
let resizeTimer;
window.addEventListener("resize", function () {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(function () {
    const carousel = document.getElementById("bannerCarousel");
    if (!carousel) return;

    const pictures = carousel.querySelectorAll("picture");
    pictures.forEach((picture) => {
      const img = picture.querySelector("img");
      if (img) {
        // Force browser to re-check <source> media queries
        img.src = img.src; // Trigger re-evaluation
      }
    });
  }, 250);
});
// ==================== Page-loader ====================
document.addEventListener("DOMContentLoaded", () => {
  const loader = document.getElementById("page-loader");
  if (loader) {
    setTimeout(() => loader.classList.add("hidden"), 1000);
  }
});

// ==================== FEATURED PROJECTS CAROUSEL WITH MOUSE DRAG ====================
(function () {
  "use strict";

  const swiperElement = document.querySelector("#featured-projects .project-slider");

  if (!swiperElement) {
    console.warn("Featured Projects Swiper: Element not found");
    return;
  }

  const projectSwiper = new Swiper(".project-slider", {
    loop: true,
    speed: 700,
    slidesPerView: 1,
    spaceBetween: 0,

    pagination: {
      el: ".project-pagination",
      clickable: true,
    },

    autoplay: {
      delay: 4500,
      disableOnInteraction: false,
      pauseOnMouseEnter: true,
    },

    // Keyboard control
    keyboard: {
      enabled: true,
      onlyInViewport: true,
    },

    // Accessibility
    a11y: {
      prevSlideMessage: 'Dự án trước',
      nextSlideMessage: 'Dự án tiếp theo',
      paginationBulletMessage: 'Đi tới dự án {{index}}',
    },

    // Effect
    effect: 'slide',

    // Events
    on: {
      init: function () {
        console.log('Featured Projects Swiper: Initialized with', this.slides.length, 'slides');
      },
    },
  });

  // Expose to global scope if needed
  window.projectSwiper = projectSwiper;

  console.log("Featured Projects Swiper: Ready");
})();

// ==================== Chatbot Widget ====================
class ChatbotWidget {
  constructor() {
    this.isOpen = false;
    this.isTyping = false;
    this.remainingRequests = 20;

    // DOM elements
    this.chatButton = document.getElementById("chatbotButton");
    this.chatWidget = document.getElementById("chatbotWidget");
    this.closeBtn = document.getElementById("chatbotCloseBtn");
    this.messagesContainer = document.getElementById("chatbotMessages");
    this.userInput = document.getElementById("chatbotInput");
    this.sendBtn = document.getElementById("chatbotSendBtn");
    this.resetBtn = document.getElementById("chatbotResetBtn");
    this.requestCountEl = document.getElementById("requestCount");

    if (!this.chatButton || !this.chatWidget) {
      console.error("Chatbot elements not found");
      return;
    }

    this.init();
  }

  init() {
    this.chatButton.addEventListener("click", () => this.toggleChat());
    this.closeBtn.addEventListener("click", () => this.toggleChat());
    this.sendBtn.addEventListener("click", () => this.sendMessage());
    this.resetBtn.addEventListener("click", () => this.resetChat());

    this.userInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // ❌ XÓA AUTO-FOCUS - KHÔNG CÒN TỰ ĐỘNG MỞ BÀN PHÍM
    // Không dùng transitionend để focus nữa

    console.log("Chatbot initialized successfully");
  }

  toggleChat() {
    this.isOpen = !this.isOpen;
    this.chatWidget.classList.toggle("active");

    // ✅ THÊM/XÓA CLASS VÀO BODY
    if (this.isOpen) {
      document.body.classList.add("chatbot-open");
      this.scrollToBottom();

      // Fix cho iOS: Ngăn body scroll
      if (this.isMobile()) {
        document.body.style.overflow = "hidden";
        document.body.style.position = "fixed";
        document.body.style.width = "100%";
        document.body.style.top = "0";
      }
    } else {
      document.body.classList.remove("chatbot-open");

      // Khôi phục scroll
      if (this.isMobile()) {
        document.body.style.overflow = "";
        document.body.style.position = "";
        document.body.style.width = "";
        document.body.style.top = "";
      }
    }
  }

  isMobile() {
    return window.innerWidth <= 768;
  }

  async sendMessage() {
    const message = this.userInput.value.trim();

    if (!message || this.isTyping) {
      return;
    }

    if (message.length > 500) {
      alert("Tin nhắn quá dài! Vui lòng nhập tối đa 500 ký tự.");
      return;
    }

    this.addMessage(message, "user");
    this.userInput.value = "";
    this.setInputState(false);
    this.showTyping();

    try {
      const response = await fetch("/chatbot/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      });

      const data = await response.json();
      this.hideTyping();

      if (response.ok) {
        this.addMessage(data.response, "bot");

        if (data.remaining_requests !== undefined) {
          this.remainingRequests = data.remaining_requests;
          this.updateRequestCount();
        }
      } else {
        this.addMessage(
          data.error ||
            data.response ||
            "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại! 😊",
          "bot"
        );
      }
    } catch (error) {
      console.error("Chatbot error:", error);
      this.hideTyping();
      this.addMessage(
        "Xin lỗi, không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng! 🔌",
        "bot"
      );
    } finally {
      this.setInputState(true);
      // ❌ KHÔNG FOCUS SAU KHI GỬI - TRÁNH MỞ BÀN PHÍM
      // this.userInput.focus(); // Đã xóa dòng này
    }
  }

  addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `chatbot-message ${sender}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "chatbot-message-content";
    contentDiv.innerHTML = this.escapeHtml(text).replace(/\n/g, "<br>");

    messageDiv.appendChild(contentDiv);
    this.messagesContainer.appendChild(messageDiv);
    this.scrollToBottom();
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  showTyping() {
    this.isTyping = true;

    const typingDiv = document.createElement("div");
    typingDiv.className = "chatbot-message bot";
    typingDiv.id = "chatbotTypingIndicator";

    const typingContent = document.createElement("div");
    typingContent.className = "chatbot-typing";
    typingContent.innerHTML = "<span></span><span></span><span></span>";

    typingDiv.appendChild(typingContent);
    this.messagesContainer.appendChild(typingDiv);
    this.scrollToBottom();
  }

  hideTyping() {
    this.isTyping = false;
    const typingIndicator = document.getElementById("chatbotTypingIndicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  setInputState(enabled) {
    this.userInput.disabled = !enabled;
    this.sendBtn.disabled = !enabled;
    this.sendBtn.style.opacity = enabled ? "1" : "0.5";
  }

  scrollToBottom() {
    setTimeout(() => {
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }, 100);
  }

  async resetChat() {
    if (
      !confirm("Bạn có chắc muốn làm mới hội thoại? Tất cả tin nhắn sẽ bị xóa.")
    ) {
      return;
    }

    try {
      const response = await fetch("/chatbot/reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const messages =
          this.messagesContainer.querySelectorAll(".chatbot-message");
        messages.forEach((msg, index) => {
          if (index > 0) {
            msg.remove();
          }
        });

        this.remainingRequests = 20;
        this.updateRequestCount();
        this.addMessage(
          "Đã làm mới hội thoại! Tôi có thể giúp gì cho bạn? 😊",
          "bot"
        );
      }
    } catch (error) {
      console.error("Reset error:", error);
      alert("Không thể làm mới hội thoại. Vui lòng thử lại!");
    }
  }

  updateRequestCount() {
    if (this.requestCountEl) {
      this.requestCountEl.textContent = `Còn ${this.remainingRequests} tin nhắn`;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("chatbotButton")) {
    new ChatbotWidget();
  }
});
// ==================== ENHANCED EFFECTS FOR INDEX PAGE ==================== /


/*** ==================== MOBILE BLOG CAROUSEL  ============================*/

(function () {
  "use strict";

  // ==================== NAMESPACE ==================== //
  window.BlogCarousel = window.BlogCarousel || {};
  const BC = window.BlogCarousel;

  // ==================== STATE ==================== //
  BC.state = {
    isCreated: false,
    carouselInstance: null,
  };

  // ==================== CONFIG ==================== //
  BC.config = {
    transitionDuration: 400,
    snapThreshold: 0.3, // Kéo 30% thì snap sang slide mới
  };

  // ==================== TẠO CAROUSEL 1 LẦN DUY NHẤT ==================== //
  BC.createOnce = function () {
    if (this.state.isCreated) {
      console.log("📱 Blog Carousel: Already exists, ensuring visibility");
      return;
    }

    const blogSection = document.querySelector("#featured-blogs-section");
    if (!blogSection) {
      console.log("📱 Blog Carousel: Section not found");
      return;
    }

    const originalGrid = blogSection.querySelector(".row.g-4");
    if (!originalGrid) {
      console.log("📱 Blog Carousel: Grid not found");
      return;
    }

    const blogCards = originalGrid.querySelectorAll(".col-lg-4");
    if (blogCards.length === 0) {
      console.log("📱 Blog Carousel: No blog cards found");
      return;
    }

    // Tạo carousel structure
    const wrapper = document.createElement("div");
    wrapper.className = "blog-carousel-wrapper";

    const container = document.createElement("div");
    container.className = "blog-carousel-container";

    const track = document.createElement("div");
    track.className = "blog-carousel-track";

    // Clone blog cards vào carousel
    blogCards.forEach((card) => {
      const slide = document.createElement("div");
      slide.className = "blog-carousel-slide";
      slide.innerHTML = card.innerHTML;
      track.appendChild(slide);
    });

    // Tạo navigation buttons
    const prevBtn = document.createElement("button");
    prevBtn.className = "blog-carousel-nav-btn blog-carousel-prev";
    prevBtn.innerHTML = '<i class="bi bi-chevron-left"></i>';
    prevBtn.setAttribute("aria-label", "Previous");

    const nextBtn = document.createElement("button");
    nextBtn.className = "blog-carousel-nav-btn blog-carousel-next";
    nextBtn.innerHTML = '<i class="bi bi-chevron-right"></i>';
    nextBtn.setAttribute("aria-label", "Next");

    // Lắp ráp
    container.appendChild(track);
    wrapper.appendChild(container);
    wrapper.appendChild(prevBtn);
    wrapper.appendChild(nextBtn);

    // Thêm vào DOM
    originalGrid.parentNode.insertBefore(wrapper, originalGrid);

    // Setup carousel logic
    this.state.carouselInstance = this.setupCarousel(
      track,
      container,
      prevBtn,
      nextBtn
    );
    this.state.isCreated = true;

    console.log(
      `✅ Blog Carousel: Created with ${blogCards.length} cards (PERMANENT)`
    );
  };

  // ==================== SETUP CAROUSEL LOGIC ==================== //
  BC.setupCarousel = function (track, container, prevBtn, nextBtn) {
    const slides = track.querySelectorAll(".blog-carousel-slide");
    let currentIndex = 0;
    let itemsPerView = 1;
    let isDragging = false;
    let startPos = 0;
    let currentTranslate = 0;
    let prevTranslate = 0;
    let dragDistance = 0;

    function updateItemsPerView() {
      const width = window.innerWidth;
      if (width < 768) {
        itemsPerView = 1;
      } else if (width <= 991) {
        itemsPerView = 2;
      }
    }

    function getSlideWidth() {
      return container.offsetWidth / itemsPerView;
    }

    function updateCarousel(animate = true) {
      const slideWidth = getSlideWidth();
      const offset = -currentIndex * slideWidth;

      if (animate) {
        track.style.transition = `transform ${BC.config.transitionDuration}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`;
      } else {
        track.style.transition = "none";
      }

      track.style.transform = `translateX(${offset}px)`;
      currentTranslate = offset;
      prevTranslate = offset;
    }

    function next() {
      const maxIndex = slides.length - itemsPerView;
      if (currentIndex < maxIndex) {
        currentIndex++;
      } else {
        currentIndex = 0; // LOOP về đầu
      }
      updateCarousel();
    }

    function prev() {
      if (currentIndex > 0) {
        currentIndex--;
      } else {
        currentIndex = slides.length - itemsPerView; // LOOP về cuối
      }
      updateCarousel();
    }

    function goToSlide(index) {
      const maxIndex = slides.length - itemsPerView;
      currentIndex = Math.max(0, Math.min(index, maxIndex));
      updateCarousel();
    }

    // ==================== TOUCH/DRAG EVENTS ==================== //
    function getPositionX(event) {
      return event.type.includes("mouse")
        ? event.pageX
        : event.touches[0].clientX;
    }

    function dragStart(event) {
      isDragging = true;
      startPos = getPositionX(event);
      dragDistance = 0;
      track.style.cursor = "grabbing";
      track.style.transition = "none";

      // Prevent default on touch to avoid scroll
      if (event.type === "touchstart") {
        // Don't prevent default - let it scroll naturally
      }
    }

    function dragMove(event) {
      if (!isDragging) return;

      const currentPosition = getPositionX(event);
      dragDistance = currentPosition - startPos;
      currentTranslate = prevTranslate + dragDistance;

      track.style.transform = `translateX(${currentTranslate}px)`;

      // Prevent scroll when dragging horizontally
      if (Math.abs(dragDistance) > 10) {
        event.preventDefault();
      }
    }

    function dragEnd() {
      if (!isDragging) return;

      isDragging = false;
      track.style.cursor = "grab";

      const slideWidth = getSlideWidth();
      const movedBy = dragDistance;
      const movePercentage = Math.abs(movedBy) / slideWidth;

      // SMART SNAP: Kéo > 30% slide width hoặc > 50px → chuyển slide
      if (movePercentage > BC.config.snapThreshold || Math.abs(movedBy) > 50) {
        if (movedBy < 0) {
          // Kéo sang trái = next
          next();
        } else {
          // Kéo sang phải = prev
          prev();
        }
      } else {
        // Snap về vị trí hiện tại
        updateCarousel();
      }
    }

    // ==================== EVENT LISTENERS ==================== //

    // Mouse events
    track.addEventListener("mousedown", dragStart);
    track.addEventListener("mousemove", dragMove);
    track.addEventListener("mouseup", dragEnd);
    track.addEventListener("mouseleave", dragEnd);

    // Touch events - passive: false để có thể preventDefault
    track.addEventListener("touchstart", dragStart, { passive: true });
    track.addEventListener("touchmove", dragMove, { passive: false });
    track.addEventListener("touchend", dragEnd);

    // Prevent click khi đang drag
    track.addEventListener(
      "click",
      function (e) {
        if (Math.abs(dragDistance) > 5) {
          e.preventDefault();
          e.stopPropagation();
          return false;
        }
      },
      true
    );

    // Prevent link click during drag
    track.addEventListener("mousedown", function (e) {
      dragDistance = 0;
    });

    track.addEventListener("touchstart", function (e) {
      dragDistance = 0;
    });

    // Button events
    prevBtn.addEventListener("click", function (e) {
      e.preventDefault();
      prev();
    });

    nextBtn.addEventListener("click", function (e) {
      e.preventDefault();
      next();
    });

    // Cursor style
    track.style.cursor = "grab";
    track.style.userSelect = "none";

    // Keyboard support
    document.addEventListener("keydown", function (e) {
      if (!container.closest(".blog-carousel-wrapper")) return;

      if (e.key === "ArrowLeft") {
        e.preventDefault();
        prev();
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        next();
      }
    });

    // Resize handler
    let resizeTimeout;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        updateItemsPerView();
        goToSlide(currentIndex);
      }, 250);
    });

    // Initialize
    updateItemsPerView();
    updateCarousel();

    return {
      next,
      prev,
      goToSlide,
      updateItemsPerView,
      updateCarousel,
      getCurrentIndex: () => currentIndex,
    };
  };

  // ==================== AUTO INIT ==================== //
  function init() {
    BC.createOnce();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("pageshow", function (event) {
    console.log("📱 pageshow:", event.persisted ? "from cache" : "normal load");
    init();
  });

  console.log("📦 Blog Carousel: Module loaded (Smooth drag + Infinite loop)");
})();

/* ==================== BANNER EFFECTS WITH DRAG/SWIPE ==================== */

(function () {
  "use strict";

  // Namespace để tránh xung đột
  window.BannerEffect = window.BannerEffect || {};

  const BannerEffect = window.BannerEffect;

  // ==================== CONFIGURATION ====================
  BannerEffect.config = {
    carouselId: "bannerCarousel",
    animationDelay: 100, // Delay trước khi animation chạy (ms)
    animationTypes: [
      "banner-fade-in",
      "banner-slide-up",
      "banner-slide-left",
      "banner-zoom-in",
    ],
    defaultAnimation: "banner-fade-in", // Animation mặc định
    observerThreshold: 0.2, // % banner visible để trigger animation
    enableIntersectionObserver: true, // Bật animation khi scroll vào view
    dragThreshold: 50, // Khoảng cách tối thiểu để trigger slide (px)
    enableDrag: true, // Bật/tắt tính năng kéo
  };

  // ==================== STATE ====================
  BannerEffect.state = {
    carousel: null,
    captions: [],
    hasAnimated: false,
    isInitialized: false,
    currentAnimation: null,
    bsCarousel: null, // Bootstrap Carousel instance
    // Drag/Swipe state
    isDragging: false,
    startX: 0,
    currentX: 0,
    dragStartTime: 0,
  };

  // ==================== INITIALIZATION ====================
  BannerEffect.init = function () {
    console.log("🎬 Banner Effect: Initializing...");

    // Tìm carousel element
    this.state.carousel = document.getElementById(this.config.carouselId);

    if (!this.state.carousel) {
      console.warn("Banner Effect: Carousel not found");
      return;
    }

    // Lấy Bootstrap Carousel instance
    if (typeof bootstrap !== "undefined" && bootstrap.Carousel) {
      this.state.bsCarousel =
        bootstrap.Carousel.getInstance(this.state.carousel) ||
        new bootstrap.Carousel(this.state.carousel, {
          ride: "carousel",
          interval: 5000,
          pause: "hover",
        });
    }

    // Lấy tất cả captions
    this.state.captions = Array.from(
      this.state.carousel.querySelectorAll(".carousel-caption")
    );

    if (this.state.captions.length === 0) {
      console.warn("Banner Effect: No captions found");
      return;
    }

    // Setup animation cho caption đầu tiên
    this.setupInitialAnimation();

    // Setup carousel slide event listener
    this.setupCarouselEvents();

    // Setup Intersection Observer (nếu enabled)
    if (this.config.enableIntersectionObserver) {
      this.setupIntersectionObserver();
    } else {
      // Nếu không dùng observer, animate ngay
      this.animateCaption(this.state.captions[0]);
    }

    // Setup Drag/Swipe (nếu enabled)
    if (this.config.enableDrag) {
      this.setupDragEvents();
    }

    this.state.isInitialized = true;
    console.log("✅ Banner Effect: Initialized successfully (with drag/swipe)");
  };

  // ==================== SETUP INITIAL ANIMATION ====================
  BannerEffect.setupInitialAnimation = function () {
    // Đặt animation type cho từng caption (có thể random hoặc theo thứ tự)
    this.state.captions.forEach((caption, index) => {
      // Lấy animation type từ data attribute hoặc dùng mặc định
      const animationType =
        caption.dataset.animation || this.config.defaultAnimation;

      caption.dataset.animationType = animationType;

      // Reset về trạng thái ban đầu
      caption.classList.remove(...this.config.animationTypes);
      caption.style.opacity = "0";
      caption.style.visibility = "hidden";
    });
  };

  // ==================== ANIMATE CAPTION ====================
  BannerEffect.animateCaption = function (caption) {
    if (!caption) return;

    const animationType =
      caption.dataset.animationType || this.config.defaultAnimation;

    // Remove old animations
    caption.classList.remove(...this.config.animationTypes);

    // Small delay để đảm bảo CSS được apply
    setTimeout(() => {
      caption.style.visibility = "visible";
      caption.classList.add(animationType);

      // Store current animation
      this.state.currentAnimation = animationType;
    }, this.config.animationDelay);
  };

  // ==================== CAROUSEL EVENTS ====================
  BannerEffect.setupCarouselEvents = function () {
    // Lắng nghe sự kiện slide của Bootstrap carousel
    this.state.carousel.addEventListener("slide.bs.carousel", (event) => {
      const nextIndex = event.to;
      const nextCaption = this.state.captions[nextIndex];

      if (nextCaption) {
        // Reset caption hiện tại
        this.state.captions.forEach((cap) => {
          cap.classList.remove(...this.config.animationTypes);
          cap.style.opacity = "0";
          cap.style.visibility = "hidden";
        });

        // Animate caption mới
        this.animateCaption(nextCaption);
      }
    });

    // Lắng nghe sự kiện sau khi slide hoàn tất
    this.state.carousel.addEventListener("slid.bs.carousel", (event) => {
      console.log(`Banner slid to index: ${event.to}`);
    });
  };

  // ==================== INTERSECTION OBSERVER ====================
  BannerEffect.setupIntersectionObserver = function () {
    // Chỉ animate lần đầu khi banner xuất hiện trong viewport
    if ("IntersectionObserver" in window) {
      const observerOptions = {
        threshold: this.config.observerThreshold,
        rootMargin: "0px",
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !this.state.hasAnimated) {
            // Lấy caption của slide active
            const activeSlide = this.state.carousel.querySelector(
              ".carousel-item.active"
            );
            const activeCaption = activeSlide
              ? activeSlide.querySelector(".carousel-caption")
              : this.state.captions[0];

            if (activeCaption) {
              this.animateCaption(activeCaption);
              this.state.hasAnimated = true;

              // Unobserve sau khi animate lần đầu
              observer.unobserve(entry.target);
            }
          }
        });
      }, observerOptions);

      observer.observe(this.state.carousel);
    } else {
      // Fallback: animate ngay nếu không support IntersectionObserver
      this.animateCaption(this.state.captions[0]);
      this.state.hasAnimated = true;
    }
  };

  // ==================== DRAG/SWIPE EVENTS ====================
  BannerEffect.setupDragEvents = function () {
    const carousel = this.state.carousel;

    // Set cursor style
    carousel.style.cursor = "grab";

    // Mouse Events
    carousel.addEventListener("mousedown", this.handleDragStart.bind(this));
    carousel.addEventListener("mousemove", this.handleDragMove.bind(this));
    carousel.addEventListener("mouseup", this.handleDragEnd.bind(this));
    carousel.addEventListener("mouseleave", this.handleDragEnd.bind(this));

    // Touch Events
    carousel.addEventListener("touchstart", this.handleDragStart.bind(this), {
      passive: true,
    });
    carousel.addEventListener("touchmove", this.handleDragMove.bind(this), {
      passive: true,
    });
    carousel.addEventListener("touchend", this.handleDragEnd.bind(this));

    // Prevent context menu on long press
    carousel.addEventListener("contextmenu", (e) => {
      if (this.state.isDragging) {
        e.preventDefault();
      }
    });

    // Prevent image drag
    const images = carousel.querySelectorAll("img");
    images.forEach((img) => {
      img.addEventListener("dragstart", (e) => e.preventDefault());
    });

    console.log("👆 Banner Effect: Drag/Swipe enabled");
  };

  // ==================== HANDLE DRAG START ====================
  BannerEffect.handleDragStart = function (e) {
    // Không drag nếu click vào button hoặc link
    if (e.target.closest("a, button")) {
      return;
    }

    this.state.isDragging = true;
    this.state.startX = this.getPositionX(e);
    this.state.currentX = this.state.startX;
    this.state.dragStartTime = Date.now();

    // Change cursor
    this.state.carousel.style.cursor = "grabbing";

    // Pause carousel auto-slide
    if (this.state.bsCarousel) {
      this.state.bsCarousel.pause();
    }
  };

  // ==================== HANDLE DRAG MOVE ====================
  BannerEffect.handleDragMove = function (e) {
    if (!this.state.isDragging) return;

    this.state.currentX = this.getPositionX(e);
  };

  // ==================== HANDLE DRAG END ====================
  BannerEffect.handleDragEnd = function (e) {
    if (!this.state.isDragging) return;

    this.state.isDragging = false;
    this.state.carousel.style.cursor = "grab";

    // Calculate drag distance and time
    const dragDistance = this.state.currentX - this.state.startX;
    const dragTime = Date.now() - this.state.dragStartTime;
    const dragVelocity = Math.abs(dragDistance) / dragTime;

    // Determine if should trigger slide change
    const shouldSlide =
      Math.abs(dragDistance) > this.config.dragThreshold || dragVelocity > 0.5;

    if (shouldSlide && this.state.bsCarousel) {
      if (dragDistance > 0) {
        // Swipe right -> Previous slide
        this.state.bsCarousel.prev();
      } else {
        // Swipe left -> Next slide
        this.state.bsCarousel.next();
      }
    }

    // Resume carousel auto-slide
    setTimeout(() => {
      if (this.state.bsCarousel) {
        this.state.bsCarousel.cycle();
      }
    }, 300);

    // Reset state
    this.state.startX = 0;
    this.state.currentX = 0;
    this.state.dragStartTime = 0;
  };

  // ==================== GET POSITION X (Mouse/Touch) ====================
  BannerEffect.getPositionX = function (e) {
    return e.type.includes("mouse") ? e.pageX : e.touches[0].clientX;
  };

  // ==================== UTILITY: SET ANIMATION TYPE ====================
  BannerEffect.setAnimationType = function (type) {
    if (this.config.animationTypes.includes(type)) {
      this.config.defaultAnimation = type;
      console.log(`Banner Effect: Animation type set to ${type}`);
    } else {
      console.warn(`Banner Effect: Invalid animation type "${type}"`);
    }
  };

  // ==================== UTILITY: TOGGLE DRAG ====================
  BannerEffect.toggleDrag = function (enable) {
    this.config.enableDrag = enable;
    if (enable && this.state.isInitialized) {
      this.setupDragEvents();
    }
    console.log(`Banner Effect: Drag ${enable ? "enabled" : "disabled"}`);
  };

  // ==================== UTILITY: REFRESH ====================
  BannerEffect.refresh = function () {
    if (!this.state.isInitialized) return;

    console.log("🔄 Banner Effect: Refreshing...");
    this.setupInitialAnimation();

    const activeCaption = this.state.carousel.querySelector(
      ".carousel-item.active .carousel-caption"
    );
    if (activeCaption) {
      this.animateCaption(activeCaption);
    }
  };

  // ==================== UTILITY: DESTROY ====================
  BannerEffect.destroy = function () {
    if (!this.state.isInitialized) return;

    console.log("🗑️ Banner Effect: Destroying...");

    // Remove all animation classes
    this.state.captions.forEach((caption) => {
      caption.classList.remove(...this.config.animationTypes);
      caption.style.opacity = "";
      caption.style.visibility = "";
    });

    // Reset cursor
    if (this.state.carousel) {
      this.state.carousel.style.cursor = "";
    }

    // Reset state
    this.state = {
      carousel: null,
      captions: [],
      hasAnimated: false,
      isInitialized: false,
      currentAnimation: null,
      bsCarousel: null,
      isDragging: false,
      startX: 0,
      currentX: 0,
      dragStartTime: 0,
    };
  };

  // ==================== AUTO INITIALIZATION ====================
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      BannerEffect.init();
    });
  } else {
    BannerEffect.init();
  }

  // ==================== WINDOW LOAD FALLBACK ====================
  window.addEventListener("load", () => {
    if (!BannerEffect.state.isInitialized) {
      BannerEffect.init();
    }
  });

  // ==================== CLEANUP ON UNLOAD ====================
  window.addEventListener("beforeunload", () => {
    BannerEffect.destroy();
  });

  console.log("📦 Banner Effect: Module loaded (with drag/swipe support)");
})();

/* ==================== Newsletter ==================== */
(function () {
  "use strict";

  window.Newsletter = window.Newsletter || {};
  const newsletter = window.Newsletter;

  newsletter.init = function () {
    const form = document.getElementById("newsletterForm");
    if (!form) return;

    form.addEventListener("submit", this.handleSubmit.bind(this));

    console.log("✅ Newsletter: Initialized");
  };

  newsletter.handleSubmit = async function (e) {
    e.preventDefault();

    const form = e.target;
    const emailInput = form.querySelector("#newsletter-email");
    const consentCheckbox = form.querySelector("#newsletter-consent");
    const messageEl = document.getElementById("newsletterMessage");
    const submitBtn = form.querySelector("#newsletter-submit-btn");
    const btnText = submitBtn.querySelector(".btn-text");
    const btnIcon = submitBtn.querySelector(".btn-icon");
    const btnSpinner = submitBtn.querySelector(".btn-spinner");

    // Clear previous messages
    messageEl.className = "newsletter-message";
    messageEl.textContent = "";

    // Validation
    if (!emailInput.value.trim()) {
      this.showMessage(messageEl, "Vui lòng nhập email!", "error");
      emailInput.focus();
      return;
    }

    if (!consentCheckbox.checked) {
      this.showMessage(
        messageEl,
        "Vui lòng đồng ý nhận email marketing!",
        "error"
      );
      return;
    }

    // Disable button during submission
    submitBtn.disabled = true;
    btnText.classList.add("d-none");
    btnIcon.classList.add("d-none");
    btnSpinner.classList.remove("d-none");

    try {
      const response = await fetch("/newsletter/subscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          email: emailInput.value.trim(),
          consent: consentCheckbox.checked,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        this.showMessage(messageEl, data.message, "success");
        form.reset();

        // Google Analytics event (nếu có)
        if (typeof gtag !== "undefined") {
          gtag("event", "newsletter_signup", {
            event_category: "Newsletter",
            event_label: "Success",
          });
        }
      } else {
        this.showMessage(messageEl, data.message || "Có lỗi xảy ra!", "error");
      }
    } catch (error) {
      console.error("Newsletter subscription error:", error);
      this.showMessage(
        messageEl,
        "Không thể kết nối đến server. Vui lòng thử lại!",
        "error"
      );
    } finally {
      // Re-enable button
      submitBtn.disabled = false;
      btnText.classList.remove("d-none");
      btnIcon.classList.remove("d-none");
      btnSpinner.classList.add("d-none");
    }
  };

  newsletter.showMessage = function (element, message, type) {
    element.textContent = message;
    element.className = `newsletter-message ${type}`;

    // Auto-hide success message after 5 seconds
    if (type === "success") {
      setTimeout(() => {
        element.style.opacity = "0";
        setTimeout(() => {
          element.className = "newsletter-message";
          element.textContent = "";
          element.style.opacity = "1";
        }, 300);
      }, 5000);
    }
  };

  // Auto-init
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => newsletter.init());
  } else {
    newsletter.init();
  }
})();

/* ==================== Testimonials / Customer Reviews ==================== */

/* ==================== Trust Badges / Certifications ==================== */

/* ==================== BLOG TABLE OF CONTENTS ==================== */

(function() {
  'use strict';

  // ==================== CẤU HÌNH ====================
  const CONFIG = {
    contentSelector: '.blog-content-detail',
    tocContainerId: 'blog-toc-container',
    inlineTocContainerId: 'blog-inline-toc-content', // THÊM: Inline TOC
    headingSelectors: 'h2, h3, h4',
    activeClass: 'active',
    scrollOffset: 100,
    observerRootMargin: '-100px 0px -66%',
    smoothScrollBehavior: 'smooth'
  };

  // ==================== UTILITY FUNCTIONS ====================

  /**
   * Tạo ID từ text heading
   */
  function generateId(text) {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Xóa dấu tiếng Việt
      .replace(/đ/g, 'd')
      .replace(/[^a-z0-9\s-]/g, '') // Xóa ký tự đặc biệt
      .trim()
      .replace(/\s+/g, '-') // Thay khoảng trắng bằng -
      .replace(/-+/g, '-') // Xóa dấu - thừa
      .substring(0, 50); // Giới hạn độ dài
  }

  /**
   * Đảm bảo ID là duy nhất
   */
  function ensureUniqueId(baseId, existingIds) {
    let id = baseId;
    let counter = 1;

    while (existingIds.has(id)) {
      id = `${baseId}-${counter}`;
      counter++;
    }

    existingIds.add(id);
    return id;
  }

  /**
   * Lấy level của heading (2, 3, 4)
   */
  function getHeadingLevel(heading) {
    return parseInt(heading.tagName.substring(1));
  }

  // ==================== MAIN FUNCTIONS ====================

  /**
   * Quét và chuẩn bị các heading
   */
  function prepareHeadings(contentElement) {
    const headings = contentElement.querySelectorAll(CONFIG.headingSelectors);
    const existingIds = new Set();
    const tocData = [];

    headings.forEach((heading, index) => {
      // Tạo ID nếu chưa có
      if (!heading.id) {
        const text = heading.textContent.trim();
        const baseId = generateId(text);
        heading.id = ensureUniqueId(baseId, existingIds);
      } else {
        existingIds.add(heading.id);
      }

      // Lưu thông tin heading
      tocData.push({
        id: heading.id,
        text: heading.textContent.trim(),
        level: getHeadingLevel(heading),
        element: heading
      });
    });

    return tocData;
  }

  /**
   * Tạo HTML cho mục lục sidebar
   */
  function buildSidebarTocHtml(tocData) {
    if (tocData.length === 0) {
      return '<p class="text-muted small">Không có mục lục</p>';
    }

    let html = '<nav class="blog-toc-nav" aria-label="Mục lục bài viết"><ul class="blog-toc-list">';

    tocData.forEach((item, index) => {
      const levelClass = `toc-level-${item.level}`;
      const isFirst = index === 0;

      html += `
        <li class="blog-toc-item ${levelClass}">
          <a href="#${item.id}"
             class="blog-toc-link ${isFirst ? CONFIG.activeClass : ''}"
             data-target="${item.id}"
             title="${item.text}">
            ${item.text}
          </a>
        </li>
      `;
    });

    html += '</ul></nav>';
    return html;
  }

  /**
   * Tạo HTML cho mục lục inline (2 cột)
   */
  function buildInlineTocHtml(tocData) {
    if (tocData.length === 0) {
      return '';
    }

    let html = '<ul class="blog-inline-toc-list">';

    tocData.forEach((item) => {
      const levelClass = `inline-toc-level-${item.level}`;

      html += `
        <li class="blog-inline-toc-item ${levelClass}">
          <a href="#${item.id}"
             class="blog-inline-toc-link"
             data-target="${item.id}"
             title="${item.text}">
            ${item.text}
          </a>
        </li>
      `;
    });

    html += '</ul>';
    return html;
  }

  /**
   * Thiết lập Intersection Observer để highlight mục đang xem
   */
  function setupScrollSpy(tocData) {
    const tocLinks = document.querySelectorAll('.blog-toc-link');

    // Map heading ID -> TOC link
    const linkMap = new Map();
    tocLinks.forEach(link => {
      const targetId = link.getAttribute('data-target');
      linkMap.set(targetId, link);
    });

    // IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const link = linkMap.get(entry.target.id);

          if (entry.isIntersecting) {
            // Remove active từ tất cả
            tocLinks.forEach(l => l.classList.remove(CONFIG.activeClass));

            // Add active cho heading hiện tại
            if (link) {
              link.classList.add(CONFIG.activeClass);

              // Scroll link vào view (nếu cần)
              link.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
              });
            }
          }
        });
      },
      {
        rootMargin: CONFIG.observerRootMargin,
        threshold: [0, 1]
      }
    );

    // Observe tất cả headings
    tocData.forEach(item => {
      observer.observe(item.element);
    });

    return observer;
  }

  /**
   * Thiết lập smooth scroll khi click vào TOC link
   */
  function setupSmoothScroll() {
    document.addEventListener('click', (e) => {
      const link = e.target.closest('.blog-toc-link, .blog-inline-toc-link');
      if (!link) return;

      e.preventDefault();

      const targetId = link.getAttribute('data-target');
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        const offset = CONFIG.scrollOffset;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
          top: offsetPosition,
          behavior: CONFIG.smoothScrollBehavior
        });
      }
    });
  }

  /**
   * Khởi tạo Table of Contents
   */
  function initTableOfContents() {
    // Tìm containers
    const sidebarTocContainer = document.getElementById(CONFIG.tocContainerId);
    const inlineTocContainer = document.getElementById(CONFIG.inlineTocContainerId);
    const contentElement = document.querySelector(CONFIG.contentSelector);

    // Kiểm tra điều kiện
    if (!contentElement) {
      return;
    }

    // Chuẩn bị headings
    const tocData = prepareHeadings(contentElement);

    // Không có heading -> ẩn TOC
    if (tocData.length === 0) {
      if (sidebarTocContainer) sidebarTocContainer.style.display = 'none';
      if (inlineTocContainer) {
        const inlineCard = document.getElementById('blog-inline-toc-container');
        if (inlineCard) inlineCard.style.display = 'none';
      }
      return;
    }

    // Tạo HTML cho sidebar TOC
    if (sidebarTocContainer) {
      const sidebarHtml = buildSidebarTocHtml(tocData);
      sidebarTocContainer.innerHTML = sidebarHtml;
    }

    // Tạo HTML cho inline TOC
    if (inlineTocContainer) {
      const inlineHtml = buildInlineTocHtml(tocData);
      inlineTocContainer.innerHTML = inlineHtml;
    }

    // Thiết lập scroll spy (chỉ cho sidebar)
    if (sidebarTocContainer) {
      const observer = setupScrollSpy(tocData);

      // Cleanup khi unload
      window.addEventListener('beforeunload', () => {
        observer.disconnect();
      });
    }

    // Thiết lập smooth scroll (cho cả 2)
    setupSmoothScroll();
  }

  // ==================== AUTO INIT ====================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTableOfContents);
  } else {
    initTableOfContents();
  }

})();

/* ==================== NavLink Hold Drop ==================== */
(function () {
  "use strict";

  // Namespace riêng
  const holdHienDropdown = {
    holdTimer: null,
    holdDelay: 200, // ms - thời gian giữ để hiện dropdown

    init: function () {
      this.setupEventListeners();
    },

    setupEventListeners: function () {
      // Tìm tất cả nav-item có dropdown
      const dropdownItems = document.querySelectorAll(".nav-item.dropdown");

      dropdownItems.forEach((item) => {
        const link = item.querySelector(".nav-link.dropdown-toggle");
        const menu = item.querySelector(".dropdown-menu");

        if (!link || !menu) return;

        // Thêm class để styling
        item.classList.add("hold-hien-dropdown");

        // Mouse enter - bắt đầu đếm thời gian
        link.addEventListener("mouseenter", () => {
          this.startHoldTimer(item);
        });

        // Mouse leave - hủy timer
        link.addEventListener("mouseleave", () => {
          this.cancelHoldTimer();
        });

        // Giữ dropdown mở khi hover vào menu
        menu.addEventListener("mouseenter", () => {
          this.cancelHoldTimer();
        });

        menu.addEventListener("mouseleave", () => {
          this.hideDropdown(item);
        });

        // Click vẫn hoạt động bình thường (toggle)
        link.addEventListener("click", (e) => {
          e.preventDefault();
          this.toggleDropdown(item);
        });
      });

      // Click ra ngoài để đóng dropdown
      document.addEventListener("click", (e) => {
        if (!e.target.closest(".nav-item.hold-hien-dropdown")) {
          this.hideAllDropdowns();
        }
      });
    },

    startHoldTimer: function (item) {
      this.cancelHoldTimer();
      this.holdTimer = setTimeout(() => {
        this.showDropdown(item);
      }, this.holdDelay);
    },

    cancelHoldTimer: function () {
      if (this.holdTimer) {
        clearTimeout(this.holdTimer);
        this.holdTimer = null;
      }
    },

    showDropdown: function (item) {
      this.hideAllDropdowns();
      item.classList.add("show");
    },

    hideDropdown: function (item) {
      item.classList.remove("show");
    },

    toggleDropdown: function (item) {
      const isShown = item.classList.contains("show");
      this.hideAllDropdowns();
      if (!isShown) {
        item.classList.add("show");
      }
    },

    hideAllDropdowns: function () {
      document
        .querySelectorAll(".nav-item.hold-hien-dropdown.show")
        .forEach((item) => {
          item.classList.remove("show");
        });
    },
  };

  // Khởi chạy khi DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      holdHienDropdown.init();
    });
  } else {
    holdHienDropdown.init();
  }

  // Export namespace (nếu cần truy cập từ bên ngoài)
  window.holdHienDropdown = holdHienDropdown;
})();

/* ==================== Phóng to ảnh sản phẩm ==================== */
document.addEventListener("DOMContentLoaded", function () {
  const lightbox = document.getElementById("productLightbox");
  const lightboxImg = document.getElementById("lightboxImage");
  const modal = new bootstrap.Modal(lightbox);

  document.querySelectorAll(".lightbox-trigger").forEach((trigger) => {
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      const imgSrc = this.getAttribute("data-image");
      const imgTitle = this.getAttribute("data-title");

      lightboxImg.src = imgSrc;
      lightboxImg.alt = imgTitle;
      modal.show();
    });
  });

  // Xóa src khi đóng modal (tránh ảnh cũ hiện khi mở lại)
  lightbox.addEventListener("hidden.bs.modal", function () {
    lightboxImg.src = "";
  });
});

// ==================== SEARCH AUTOCOMPLETE ====================
(function() {
  'use strict';

  class SearchAutocomplete {
    constructor(inputSelector, resultsSelector) {
      this.input = document.querySelector(inputSelector);
      this.resultsContainer = document.querySelector(resultsSelector);
      this.debounceTimer = null;
      this.currentFocus = -1;
      this.cache = new Map();

      if (this.input && this.resultsContainer) {
        this.init();
      }
    }

    init() {
      this.input.addEventListener('input', (e) => this.handleInput(e));
      this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
      this.input.addEventListener('focus', () => {
        if (this.input.value.trim().length >= 2) {
          this.resultsContainer.style.display = 'block';
        }
      });

      document.addEventListener('click', (e) => {
        if (!this.input.contains(e.target) && !this.resultsContainer.contains(e.target)) {
          this.hideResults();
        }
      });

      this.input.closest('form')?.addEventListener('submit', (e) => {
        if (this.currentFocus >= 0) {
          e.preventDefault();
          this.selectItem(this.currentFocus);
        }
      });
    }

    handleInput(e) {
      const keyword = e.target.value.trim();
      clearTimeout(this.debounceTimer);

      if (keyword.length < 2) {
        this.hideResults();
        return;
      }

      this.debounceTimer = setTimeout(() => {
        this.fetchSuggestions(keyword);
      }, 300);
    }

    async fetchSuggestions(keyword) {
      if (this.cache.has(keyword)) {
        this.renderResults(this.cache.get(keyword));
        return;
      }

      try {
        this.showLoading();
        const response = await fetch(`/api/search-suggestions?q=${encodeURIComponent(keyword)}`);
        const data = await response.json();

        this.cache.set(keyword, data.suggestions);
        if (this.cache.size > 20) {
          const firstKey = this.cache.keys().next().value;
          this.cache.delete(firstKey);
        }

        this.renderResults(data.suggestions);
      } catch (error) {
        console.error('Search error:', error);
        this.hideResults();
      }
    }

    showLoading() {
      this.resultsContainer.innerHTML = `
        <div class="search-autocomplete-loading">
          <div class="spinner-border spinner-border-sm text-warning" role="status">
            <span class="visually-hidden">Đang tìm...</span>
          </div>
          <span class="ms-2">Đang tìm kiếm...</span>
        </div>
      `;
      this.resultsContainer.style.display = 'block';
    }

    renderResults(suggestions) {
      if (!suggestions || suggestions.length === 0) {
        this.resultsContainer.innerHTML = `
          <div class="search-autocomplete-empty">
            <i class="bi bi-search"></i>
            <span>Không tìm thấy kết quả phù hợp</span>
          </div>
        `;
        this.resultsContainer.style.display = 'block';
        return;
      }

      const grouped = { page: [], product: [], blog: [] };
      suggestions.forEach(item => {
        if (grouped[item.type]) grouped[item.type].push(item);
      });

      let html = '';

      if (grouped.page.length > 0) {
        html += '<div class="search-autocomplete-group">';
        html += '<div class="search-autocomplete-group-title"><i class="bi bi-file-text"></i> Trang thông tin</div>';
        grouped.page.forEach((item, index) => {
          html += this.renderItem(item, index);
        });
        html += '</div>';
      }

      if (grouped.product.length > 0) {
        html += '<div class="search-autocomplete-group">';
        html += '<div class="search-autocomplete-group-title"><i class="bi bi-box-seam"></i> Sản phẩm</div>';
        grouped.product.forEach((item, index) => {
          html += this.renderItem(item, grouped.page.length + index);
        });
        html += '</div>';
      }

      if (grouped.blog.length > 0) {
        html += '<div class="search-autocomplete-group">';
        html += '<div class="search-autocomplete-group-title"><i class="bi bi-journal-text"></i> Bài viết</div>';
        grouped.blog.forEach((item, index) => {
          html += this.renderItem(item, grouped.page.length + grouped.product.length + index);
        });
        html += '</div>';
      }

      this.resultsContainer.innerHTML = html;
      this.resultsContainer.style.display = 'block';
      this.currentFocus = -1;
    }

    renderItem(item, index) {
      const imageHtml = item.image
        ? `<img src="${item.image}" alt="${item.title}" class="search-autocomplete-image">`
        : '';

      return `
        <a href="${item.url}"
           class="search-autocomplete-item type-${item.type}"
           data-index="${index}">
          ${imageHtml}
          <span class="search-autocomplete-title">${this.highlightKeyword(item.title)}</span>
        </a>
      `;
    }

    highlightKeyword(text) {
      const keyword = this.input.value.trim();
      if (!keyword) return text;
      const regex = new RegExp(`(${keyword})`, 'gi');
      return text.replace(regex, '<mark>$1</mark>');
    }

    handleKeydown(e) {
      const items = this.resultsContainer.querySelectorAll('.search-autocomplete-item');
      if (items.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.currentFocus++;
        if (this.currentFocus >= items.length) this.currentFocus = 0;
        this.setActive(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.currentFocus--;
        if (this.currentFocus < 0) this.currentFocus = items.length - 1;
        this.setActive(items);
      } else if (e.key === 'Enter') {
        if (this.currentFocus >= 0) {
          e.preventDefault();
          items[this.currentFocus].click();
        }
      } else if (e.key === 'Escape') {
        this.hideResults();
        this.input.blur();
      }
    }

    setActive(items) {
      items.forEach((item, index) => {
        if (index === this.currentFocus) {
          item.classList.add('active');
          item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        } else {
          item.classList.remove('active');
        }
      });
    }

    selectItem(index) {
      const items = this.resultsContainer.querySelectorAll('.search-autocomplete-item');
      if (items[index]) items[index].click();
    }

    hideResults() {
      this.resultsContainer.style.display = 'none';
      this.currentFocus = -1;
    }
  }

  // Initialize
  function initSearchAutocomplete() {
    new SearchAutocomplete('.header-search-input', '#search-autocomplete-results');
    new SearchAutocomplete('#searchModal input[name="q"]', '#search-autocomplete-results-mobile');
    console.log('✅ Search Autocomplete: Initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearchAutocomplete);
  } else {
    initSearchAutocomplete();
  }
})();