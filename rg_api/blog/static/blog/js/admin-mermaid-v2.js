(function () {
  'use strict';

  var mermaidReady = false;

  function getScriptPrefix() {
    var path = window.location && window.location.pathname ? window.location.pathname : '';
    var match = path.match(/^\/(api)(\/|$)/i);
    return match ? '/' + match[1] : '';
  }

  function withScriptPrefix(url, scriptPrefix) {
    if (!url || !scriptPrefix) return url;
    if (!url.startsWith('/')) return url;
    if (url === scriptPrefix || url.startsWith(scriptPrefix + '/')) return url;
    return scriptPrefix + url;
  }

  function fixMartorDataUrls() {
    var scriptPrefix = getScriptPrefix();
    if (!scriptPrefix) return;

    var fields = document.querySelectorAll('textarea.martor[data-markdownfy-url]');
    fields.forEach(function (textarea) {
      var markdownfyUrl = textarea.getAttribute('data-markdownfy-url');
      var uploadUrl = textarea.getAttribute('data-upload-url');
      var searchUsersUrl = textarea.getAttribute('data-search-users-url');

      textarea.setAttribute('data-markdownfy-url', withScriptPrefix(markdownfyUrl, scriptPrefix));
      if (uploadUrl) {
        textarea.setAttribute('data-upload-url', withScriptPrefix(uploadUrl, scriptPrefix));
      }
      if (searchUsersUrl) {
        textarea.setAttribute('data-search-users-url', withScriptPrefix(searchUsersUrl, scriptPrefix));
      }
    });
  }

  function getLocalMermaidUrl() {
    var currentScript = document.currentScript;
    if (!currentScript) {
      currentScript = document.querySelector('script[src*="admin-mermaid-v2.js"]');
    }

    if (currentScript && currentScript.src) {
      return currentScript.src.replace('/js/admin-mermaid-v2.js', '/vendor/mermaid.min.js');
    }

    return '/static/blog/vendor/mermaid.min.js';
  }

  function ensureMermaid(callback) {
    if (window.mermaid) {
      if (!mermaidReady) {
        window.mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          flowchart: { useMaxWidth: true, htmlLabels: true },
          sequence: { useMaxWidth: true },
          gantt: { useMaxWidth: true },
          er: { useMaxWidth: true },
          pie: { useMaxWidth: true },
          mindmap: { useMaxWidth: true },
        });
        mermaidReady = true;
      }
      callback();
      return;
    }

    var script = document.createElement('script');
    script.src = getLocalMermaidUrl();
    script.onload = function () {
      if (!mermaidReady) {
        window.mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          flowchart: { useMaxWidth: true, htmlLabels: true },
          sequence: { useMaxWidth: true },
          gantt: { useMaxWidth: true },
          er: { useMaxWidth: true },
          pie: { useMaxWidth: true },
          mindmap: { useMaxWidth: true },
        });
        mermaidReady = true;
      }
      callback();
    };
    script.onerror = function () {
      console.error('admin-mermaid-v2: failed to load mermaid');
    };
    document.head.appendChild(script);
  }

  function normalizeSvg(svg) {
    if (!svg) return;
    svg.removeAttribute('width');
    svg.removeAttribute('height');
    svg.style.removeProperty('max-width');
    svg.style.display = 'block';
    svg.style.maxWidth = '100%';
    svg.style.height = 'auto';
  }

  function renderMermaid(root) {
    var scope = root && root.querySelectorAll ? root : document;
    var elements = scope.querySelectorAll('.mermaid:not([data-processed])');
    if (elements.length === 0) return;

    ensureMermaid(function () {
      elements.forEach(function (el, idx) {
        var code = el.textContent || '';
        var id = 'mermaid-admin-v2-' + Date.now() + '-' + idx;
        window.mermaid
          .render(id, code)
          .then(function (result) {
            el.innerHTML = result.svg;
            el.setAttribute('data-processed', 'true');
            normalizeSvg(el.querySelector('svg'));
          })
          .catch(function (err) {
            console.error('admin-mermaid-v2 render error:', err);
          });
      });
    });
  }

  function resizeAceEditors() {
    if (!window.ace) return;
    var fields = document.querySelectorAll('.martor-field[id^="martor-"]');
    fields.forEach(function (node) {
      try {
        var editor = window.ace.edit(node.id);
        editor.getSession().setUseWrapMode(true);
        editor.setOption('wrap', true);
        editor.resize(true);
      } catch (_e) {
        // editor might not be initialized yet
      }
    });
  }

  function bindScrollSync() {
    if (!window.ace) return;

    var fields = document.querySelectorAll('.martor-field[id^="martor-"]');
    fields.forEach(function (node) {
      if (node.dataset.syncBound === 'true') return;

      var fieldName = node.id.replace(/^martor-/, '');
      var preview = document.getElementById('nav-preview-' + fieldName);
      if (!preview) return;

      var editor;
      try {
        editor = window.ace.edit(node.id);
      } catch (_e) {
        return;
      }

      var syncSource = null;

      function getEditorMetrics() {
        var renderer = editor.renderer;
        var lineHeight = renderer && renderer.lineHeight ? renderer.lineHeight : 16;
        var scrollerHeight =
          renderer && renderer.$size && renderer.$size.scrollerHeight
            ? renderer.$size.scrollerHeight
            : node.clientHeight;
        var contentHeight = editor.session.getScreenLength() * lineHeight;
        var maxScrollable = Math.max(1, contentHeight - scrollerHeight);
        var top = renderer && renderer.getScrollTop ? renderer.getScrollTop() : (editor.session.getScrollTop() || 0);
        return { top: top, maxScrollable: maxScrollable };
      }

      function withSync(source, fn) {
        syncSource = source;
        fn();
        requestAnimationFrame(function () {
          syncSource = null;
        });
      }

      function syncPreviewFromEditor() {
        if (syncSource === 'preview') return;

        var editorMetrics = getEditorMetrics();
        var editorTop = editorMetrics.top;
        var editorMax = editorMetrics.maxScrollable;
        var previewMax = Math.max(1, preview.scrollHeight - preview.clientHeight);

        withSync('editor', function () {
          preview.scrollTop = (editorTop / editorMax) * previewMax;
        });
      }

      function syncEditorFromPreview() {
        if (syncSource === 'editor') return;

        var previewMax = Math.max(1, preview.scrollHeight - preview.clientHeight);
        var editorMax = getEditorMetrics().maxScrollable;
        var nextTop = (preview.scrollTop / previewMax) * editorMax;

        withSync('preview', function () {
          editor.session.setScrollTop(nextTop);
          editor.renderer.scrollToY(nextTop);
        });
      }

      editor.session.on('changeScrollTop', syncPreviewFromEditor);
      preview.addEventListener('scroll', syncEditorFromPreview, { passive: true });

      node.dataset.syncBound = 'true';
    });
  }

  function bindMartorPreviewEvent() {
    var $ = window.django && window.django.jQuery ? window.django.jQuery : null;
    if (!$) return;

    $(document).on('martor:preview', function (_event, currentTab) {
      try {
        var root = currentTab && currentTab.length ? currentTab.get(0) : document;
        renderMermaid(root);
      } catch (_e) {
        renderMermaid(document);
      }
      setTimeout(resizeAceEditors, 0);
      setTimeout(bindScrollSync, 0);
    });
  }

  function observePreviewMutations() {
    var observer = new MutationObserver(function (mutations) {
      var changed = mutations.some(function (m) {
        return Array.from(m.addedNodes).some(function (node) {
          return node.nodeType === 1 &&
            (node.classList && node.classList.contains('mermaid') ||
              (node.querySelector && node.querySelector('.mermaid')));
        });
      });
      if (changed) {
        renderMermaid(document);
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  document.addEventListener('DOMContentLoaded', function () {
    fixMartorDataUrls();

    bindMartorPreviewEvent();
    observePreviewMutations();

    setTimeout(resizeAceEditors, 0);
    setTimeout(resizeAceEditors, 200);
    setTimeout(resizeAceEditors, 600);
    setTimeout(bindScrollSync, 0);
    setTimeout(bindScrollSync, 300);

    renderMermaid(document);

    var sidebarToggle = document.querySelector('.toggle-nav-sidebar');
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', function () {
        setTimeout(resizeAceEditors, 50);
        setTimeout(resizeAceEditors, 250);
        setTimeout(bindScrollSync, 300);
      });
    }
  });

  window.addEventListener('resize', function () {
    resizeAceEditors();
  });
})();
