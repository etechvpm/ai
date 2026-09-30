/* Python, From Zero to Industry - site behaviour.
   Theme persistence, mobile nav, copy-to-clipboard on code blocks,
   and a dependency-free full-text search over the generated index. */
(function () {
  "use strict";

  /* ------------------------------------------------------------ theme */
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("pycourse-theme"); } catch (e) {}
  if (!saved && window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches) saved = "dark";
  if (saved) root.setAttribute("data-theme", saved);
  var themeBtn = document.getElementById("theme-btn");
  function paintTheme() {
    themeBtn.innerHTML = root.getAttribute("data-theme") === "dark"
      ? "&#9788;" : "&#9790;";
  }
  if (themeBtn) {
    paintTheme();
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("pycourse-theme", next); } catch (e) {}
      paintTheme();
    });
  }

  /* ------------------------------------------------------- mobile nav */
  var menuBtn = document.getElementById("menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });
    document.addEventListener("click", function (ev) {
      if (document.body.classList.contains("nav-open") &&
          !ev.target.closest(".sidebar") && !ev.target.closest("#menu-btn")) {
        document.body.classList.remove("nav-open");
      }
    });
  }

  /* --------------------------------------------------- copy on blocks */
  document.querySelectorAll("pre").forEach(function (pre) {
    if (pre.parentElement && pre.parentElement.tagName === "PRE") return;
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "copy";
    btn.addEventListener("click", function () {
      var code = pre.querySelector("code");
      var text = (code || pre).innerText;
      function done(ok) {
        btn.textContent = ok ? "copied!" : "press Ctrl+C";
        setTimeout(function () { btn.textContent = "copy"; }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); },
          function () { done(false); });
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; document.body.appendChild(ta); ta.select();
        try { done(document.execCommand("copy")); } catch (e) { done(false); }
        document.body.removeChild(ta);
      }
    });
    pre.appendChild(btn);
  });

  /* ------------------------------------------------------------ search */
  var input = document.getElementById("search");
  var box = document.getElementById("search-results");
  var INDEX = null;

  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    return fetch("assets/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (d) { INDEX = d; return d; })
      .catch(function () { INDEX = []; return []; });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
               "'": "&#39;" }[c];
    });
  }
  function snippet(body, q) {
    var i = body.toLowerCase().indexOf(q.toLowerCase());
    if (i < 0) return "";
    var from = Math.max(0, i - 70), to = Math.min(body.length, i + q.length + 110);
    var s = (from > 0 ? "\u2026" : "") + body.slice(from, to) +
            (to < body.length ? "\u2026" : "");
    s = escapeHtml(s);
    var re = new RegExp("(" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
    return s.replace(re, "<mark>$1</mark>");
  }

  function runSearch(q) {
    if (!INDEX) return;
    q = q.trim();
    if (q.length < 2) { box.hidden = true; box.innerHTML = ""; return; }
    var ql = q.toLowerCase();
    var hits = [];
    for (var i = 0; i < INDEX.length; i++) {
      var p = INDEX[i];
      var ti = p.title.toLowerCase().indexOf(ql);
      var bi = p.body.toLowerCase().indexOf(ql);
      if (ti < 0 && bi < 0) continue;
      hits.push({ slug: p.slug, title: p.title, body: p.body,
                  score: (ti >= 0 ? 0 : 100) + (bi < 0 ? 9999 : bi) });
    }
    hits.sort(function (a, b) { return a.score - b.score; });
    if (!hits.length) {
      box.innerHTML = '<a><span class="sr-t">No match for &ldquo;' +
        escapeHtml(q) + "&rdquo;</span></a>";
      box.hidden = false; return;
    }
    box.innerHTML = hits.slice(0, 9).map(function (h) {
      return '<a href="' + h.slug + '.html"><span class="sr-t">' +
        escapeHtml(h.title) + '</span><div class="sr-c">' +
        snippet(h.body, q) + "</div></a>";
    }).join("");
    box.hidden = false;
  }

  if (input && box) {
    var t = null;
    input.addEventListener("input", function () {
      clearTimeout(t);
      t = setTimeout(function () { loadIndex().then(function () { runSearch(input.value); }); }, 120);
    });
    input.addEventListener("focus", function () {
      if (input.value.trim().length >= 2) loadIndex().then(function () { runSearch(input.value); });
    });
    document.addEventListener("click", function (ev) {
      if (!ev.target.closest(".search-wrap")) box.hidden = true;
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "/" && document.activeElement !== input) {
        ev.preventDefault(); input.focus();
      }
      if (ev.key === "Escape") { box.hidden = true; input.blur(); }
    });
  }

  /* ------------------------------------- highlight current TOC entry */
  var tocLinks = Array.prototype.slice.call(
    document.querySelectorAll(".toc a"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) {
      var id = decodeURIComponent(a.getAttribute("href").slice(1));
      var el = document.getElementById(id);
      if (el) byId[id] = a;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.style.borderLeftColor = ""; a.style.color = ""; });
          var a = byId[en.target.id];
          if (a) { a.style.borderLeftColor = "var(--accent)"; a.style.color = "var(--accent-ink)"; }
        }
      });
    }, { rootMargin: "-10% 0px -80% 0px" });
    Object.keys(byId).forEach(function (id) {
      io.observe(document.getElementById(id));
    });
  }
})();
