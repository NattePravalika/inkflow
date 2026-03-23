/* BlogVerse – script.js  (jQuery + vanilla) */
$(function () {

  /* ── Navbar scroll shadow ─────────────────────────────────── */
  $(window).on('scroll', function () {
    $('#mainNav').toggleClass('shadow-lg', $(this).scrollTop() > 30);
  });

  /* ── Register form validation ─────────────────────────────── */
  $('#registerForm').on('submit', function (e) {
    let valid = true;

    const name  = $('#regName').val().trim();
    const email = $('#regEmail').val().trim();
    const pwd   = $('#regPassword').val().trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!name) {
      $('#regName').addClass('is-invalid'); valid = false;
    } else {
      $('#regName').removeClass('is-invalid').addClass('is-valid');
    }

    if (!email || !emailRegex.test(email)) {
      $('#regEmail').addClass('is-invalid'); valid = false;
    } else {
      $('#regEmail').removeClass('is-invalid').addClass('is-valid');
    }

    if (pwd.length < 6) {
      $('#regPassword').addClass('is-invalid'); valid = false;
    } else {
      $('#regPassword').removeClass('is-invalid').addClass('is-valid');
    }

    if (!valid) e.preventDefault();
  });

  /* ── Password strength meter ──────────────────────────────── */
  $('#regPassword').on('input', function () {
    const val = $(this).val();
    const bar = $('#strengthBar');
    const lbl = $('#pwdStrengthLabel');

    bar.removeClass('weak medium strong');

    if (val.length === 0) {
      lbl.text('');
      bar.width(0);
    } else if (val.length < 6) {
      bar.addClass('weak');
      lbl.text('Weak').css('color', '#dc3545');
    } else if (val.length < 10 || !/[A-Z]/.test(val) || !/[0-9]/.test(val)) {
      bar.addClass('medium');
      lbl.text('Medium').css('color', '#856404');
    } else {
      bar.addClass('strong');
      lbl.text('Strong').css('color', '#198754');
    }
  });

  /* ── Login form validation ────────────────────────────────── */
  $('#loginForm').on('submit', function (e) {
    let valid = true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const email = $('#loginEmail').val().trim();
    const pwd   = $('#loginPassword').val().trim();

    if (!email || !emailRegex.test(email)) {
      $('#loginEmail').addClass('is-invalid'); valid = false;
    } else {
      $('#loginEmail').removeClass('is-invalid');
    }

    if (!pwd) {
      $('#loginPassword').addClass('is-invalid'); valid = false;
    } else {
      $('#loginPassword').removeClass('is-invalid');
    }

    if (!valid) e.preventDefault();
  });

  /* ── Article / Edit form validation ──────────────────────── */
  $('#articleForm, #editForm').on('submit', function (e) {
    let valid = true;

    const title   = $('#artTitle').val().trim();
    const cat     = $('#artCategory').val();
    const content = $('#artContent').val().trim();

    if (!title) {
      $('#artTitle').addClass('is-invalid'); valid = false;
    } else {
      $('#artTitle').removeClass('is-invalid');
    }

    if (!cat) {
      $('#artCategory').addClass('is-invalid'); valid = false;
    } else {
      $('#artCategory').removeClass('is-invalid');
    }

    if (!content || content.split(/\s+/).filter(w => w).length < 10) {
      $('#artContent').addClass('is-invalid');
      if (content.length === 0) {
        $('.invalid-feedback').last().text('Please write some content.');
      } else {
        $('.invalid-feedback').last().text('Please write at least 10 words.');
      }
      valid = false;
    } else {
      $('#artContent').removeClass('is-invalid');
    }

    if (!valid) e.preventDefault();
  });

  /* Remove is-invalid on typing */
  $('input, textarea, select').on('input change', function () {
    $(this).removeClass('is-invalid');
  });

  /* ── Home page article search ─────────────────────────────── */
  function doSearch() {
    const query = $('#searchInput').val().toLowerCase().trim();
    let shown = 0;

    $('#articles-container .article-card-wrap').each(function () {
      const title = $(this).find('.article-title-link').text().toLowerCase();
      if (!query || title.includes(query)) {
        $(this).show(); shown++;
      } else {
        $(this).hide();
      }
    });

    $('#noResults').toggleClass('d-none', shown > 0);
  }

  $('#searchBtn').on('click', doSearch);
  $('#searchInput').on('keyup', function (e) {
    if (e.key === 'Enter' || $(this).val() === '') doSearch();
  });

  /* ── Alert auto-dismiss after 5 s ────────────────────────── */
  setTimeout(function () {
    $('.alert').fadeOut(600, function () { $(this).remove(); });
  }, 5000);

  /* ── Confirmation modal for delete buttons ────────────────── */
  // Handled inline in each template for specificity.

  /* ── Smooth scroll-reveal animation ──────────────────────── */
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.article-card').forEach(function (card) {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
  });

});
