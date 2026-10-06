/* ==========================================================================
   SmartQuiz 管理后台交互脚本
   只做原生 DOM 操作，不依赖任何前端框架。
   ========================================================================== */
(function () {
  'use strict';

  /* ---------- 主题切换（浅色 / 深色，记忆在 localStorage） ---------- */
  var THEME_KEY = 'smartquiz_admin_theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
  }

  var themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* 隐私模式下忽略 */ }
    });
  }

  /* ---------- 小屏侧边栏展开 / 收起 ---------- */
  var sidebar = document.getElementById('sidebar');
  var sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('is-open');
    });
    // 点击内容区自动收起
    document.addEventListener('click', function (e) {
      if (!sidebar.classList.contains('is-open')) return;
      if (sidebar.contains(e.target) || sidebarToggle.contains(e.target)) return;
      sidebar.classList.remove('is-open');
    });
  }

  /* ---------- 删除等危险操作二次确认 ---------- */
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!window.confirm(form.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  /* ---------- 提示条：成功 / 普通提示几秒后自动淡出 ---------- */
  document.querySelectorAll('.alert-success, .alert-info').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 420);
    }, 4000);
  });

  /* ======================================================================
     题目表单：题型联动
     - fill 填空：隐藏选项区
     - judge 判断：只保留 A/B 两项，并自动填「正确 / 错误」
     - single/multi：显示全部选项
     ====================================================================== */
  var typeSelect = document.getElementById('type_key');
  if (typeSelect) {
    var optionsBox = document.getElementById('optionsBox');
    var pickerBox = document.getElementById('answerPicker');
    var answerInput = document.getElementById('answerInput');
    var answerHint = document.getElementById('answerHint');
    var optionInputs = document.querySelectorAll('[data-option-input]');

    var HINTS = {
      single: '填单个字母，例如 B',
      multi: '填多个字母，例如 ABC（顺序无关，系统会自动排序比对）',
      judge: '填 A（正确）或 B（错误）',
      fill: '直接填答案文本，例如「李白」'
    };

    function visibleLetters() {
      var t = typeSelect.value;
      if (t === 'judge') return ['A', 'B'];
      if (t === 'fill') return [];
      return ['A', 'B', 'C', 'D'];
    }

    function syncType(isInitial) {
      var type = typeSelect.value;
      var letters = visibleLetters();

      // 选项输入行显隐
      optionInputs.forEach(function (input) {
        var row = input.closest('.option-row');
        var show = letters.indexOf(input.getAttribute('data-option-input')) > -1;
        if (row) row.style.display = show ? '' : 'none';
        if (!show) input.value = '';
      });

      // 判断题选项固定为「正确 / 错误」：
      // 用户主动切换题型时强制覆盖；页面初次加载（编辑已有题目）时只在为空时补默认值，
      // 避免把库里已有的内容冲掉。
      if (type === 'judge') {
        var a = document.querySelector('[data-option-input="A"]');
        var b = document.querySelector('[data-option-input="B"]');
        if (a && (a.value === '' || !isInitial)) a.value = '正确';
        if (b && (b.value === '' || !isInitial)) b.value = '错误';
      }

      if (optionsBox) optionsBox.style.display = (type === 'fill') ? 'none' : '';
      if (pickerBox) pickerBox.style.display = (type === 'fill') ? 'none' : '';

      // 答案芯片只保留当前题型可用的字母
      document.querySelectorAll('.letter-chip').forEach(function (chip) {
        var letter = chip.getAttribute('data-letter');
        chip.style.display = (letters.indexOf(letter) > -1) ? '' : 'none';
      });

      if (answerHint) answerHint.textContent = HINTS[type] || '';
      // 填空题没有选项，清空字母答案；仅在用户切换题型时执行，
      // 首次加载要保留库里已有的填空答案
      if (!isInitial && type === 'fill' && answerInput) answerInput.value = '';

      syncChips();
    }

    /* ---------- 答案芯片与输入框双向同步 ---------- */
    function syncChips() {
      if (!answerInput) return;
      var value = (answerInput.value || '').toUpperCase();
      document.querySelectorAll('.letter-chip').forEach(function (chip) {
        var letter = chip.getAttribute('data-letter');
        chip.classList.toggle('is-active', value.indexOf(letter) > -1);
      });
    }

    document.querySelectorAll('.letter-chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        if (!answerInput) return;
        var letter = chip.getAttribute('data-letter');
        var type = typeSelect.value;
        // 单选 / 判断：直接替换；多选：切换该字母
        if (type === 'multi') {
          var set = {};
          (answerInput.value || '').toUpperCase().split('').forEach(function (ch) { set[ch] = true; });
          if (set[letter]) { delete set[letter]; } else { set[letter] = true; }
          answerInput.value = Object.keys(set).sort().join('');
        } else {
          answerInput.value = (answerInput.value === letter) ? '' : letter;
        }
        syncChips();
      });
    });

    if (answerInput) answerInput.addEventListener('input', syncChips);

    typeSelect.addEventListener('change', function () { syncType(false); });
    syncType(true);
  }

  /* ======================================================================
     题目挂载列表：关键词过滤 + 全选 / 清空 + 已选计数
     ====================================================================== */
  var checkList = document.getElementById('checkList');
  if (checkList) {
    var searchInput = document.getElementById('checkSearch');
    var countEl = document.getElementById('checkCount');

    function refreshCount() {
      if (!countEl) return;
      var n = checkList.querySelectorAll('input[type="checkbox"]:checked').length;
      countEl.textContent = n;
    }

    document.querySelectorAll('.check-item').forEach(function (item) {
      var box = item.querySelector('input[type="checkbox"]');
      if (box) box.addEventListener('change', refreshCount);
    });

    if (searchInput) {
      searchInput.addEventListener('input', function () {
        var kw = this.value.trim().toLowerCase();
        document.querySelectorAll('.check-item').forEach(function (item) {
          var text = (item.getAttribute('data-title') || '').toLowerCase();
          item.classList.toggle('is-hidden', kw !== '' && text.indexOf(kw) === -1);
        });
      });
    }

    var selectAll = document.getElementById('checkSelectAll');
    if (selectAll) {
      selectAll.addEventListener('click', function () {
        checkList.querySelectorAll('.check-item:not(.is-hidden) input[type="checkbox"]').forEach(function (box) {
          box.checked = true;
        });
        refreshCount();
      });
    }

    var clearAll = document.getElementById('checkClearAll');
    if (clearAll) {
      clearAll.addEventListener('click', function () {
        checkList.querySelectorAll('input[type="checkbox"]').forEach(function (box) { box.checked = false; });
        refreshCount();
      });
    }

    refreshCount();
  }

  /* ======================================================================
     封面路径实时预览
     输入框加 data-image-preview="预览容器 id" 即可。
     小程序用的是包内路径 /images/xxx.jpg，对应后台 /media/xxx.jpg 预览地址。
     ====================================================================== */
  document.querySelectorAll('input[data-image-preview]').forEach(function (input) {
    var box = document.getElementById(input.getAttribute('data-image-preview'));
    if (!box) return;

    input.addEventListener('input', function () {
      var value = input.value.trim();
      box.textContent = '';
      if (!value) return;
      var img = document.createElement('img');
      // '/images/' 长度为 8，映射到后台的 /media/ 预览路由
      img.src = value.indexOf('/images/') === 0 ? '/media/' + value.slice(8) : value;
      img.alt = '封面预览';
      box.appendChild(img);
    });
  });
})();