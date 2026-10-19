let celebrationAnimationId = null;
        let scrollListenerAttached = false;
        let userManuallyToggled = false;
        let isClosedByScroll = false;

        function toggleFilters() {
            const box = document.getElementById('filter-panel-box');
            const btn = document.getElementById('filter-toggle-btn');
            if (!box || !btn) return;
            const isOpen = box.classList.toggle('is-open');
            btn.classList.toggle('is-open', isOpen);
            btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }

        function toggleCritRemark(headerEl) {
            const bar = headerEl.closest('.crit-remark-bar');
            if (bar) {
                const isOpen = bar.classList.toggle('is-open');
                headerEl.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            }
        }

        function setUpdatingState(isUpdating) {
            const indicator = document.getElementById('updating-indicator');
            const contentArea = document.getElementById('dashboard-content-area');

            if (indicator) {
                indicator.style.display = isUpdating ? 'inline-flex' : 'none';
            }

            if (contentArea) {
                if (isUpdating) {
                    contentArea.classList.add('is-updating');
                } else {
                    contentArea.classList.remove('is-updating');
                }
            }
        }

        async function applyFilterUpdate(pushHistory = true) {
            const form = document.getElementById('filter-form');
            if (!form) return;

            setUpdatingState(true);

            try {
                const formData = new FormData(form);
                const empVal = form.employee ? form.employee.value : '';
                const monthVal = form.month ? form.month.value : '';

                const response = await fetch(form.action || window.location.pathname, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}`);
                }

                const htmlText = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlText, 'text/html');

                // 1. Update Title
                if (doc.title) {
                    document.title = doc.title;
                }

                // 1b. Update Dynamic Header Title & Subtitle
                const newHeaderTitle = doc.getElementById('header-title');
                const curHeaderTitle = document.getElementById('header-title');
                if (newHeaderTitle && curHeaderTitle) {
                    curHeaderTitle.textContent = newHeaderTitle.textContent;
                }

                const newHeaderSub = doc.getElementById('header-subtitle');
                const curHeaderSub = document.getElementById('header-subtitle');
                if (newHeaderSub && curHeaderSub) {
                    curHeaderSub.textContent = newHeaderSub.textContent;
                    curHeaderSub.style.display = newHeaderSub.textContent.trim() ? '' : 'none';
                }

                // 2. Update Content Area
                const newContent = doc.getElementById('dashboard-content-area');
                const curContent = document.getElementById('dashboard-content-area');
                if (newContent && curContent) {
                    curContent.innerHTML = newContent.innerHTML;
                }

                // 2b. Sync Employee Select Options & Value (when team changes)
                const newEmpSelect = doc.getElementById('employee');
                const curEmpSelect = document.getElementById('employee');
                if (newEmpSelect && curEmpSelect) {
                    curEmpSelect.innerHTML = newEmpSelect.innerHTML;
                    curEmpSelect.value = newEmpSelect.value;
                    const empPillVal = document.querySelector('.search-select[data-label="employee"] .ss-value');
                    if (empPillVal) {
                        empPillVal.textContent = curEmpSelect.value || 'ALL';
                        empPillVal.classList.toggle('is-empty', !curEmpSelect.value);
                    }
                }

                // 2c. Sync Team Select
                const newTeamSelect = doc.getElementById('team');
                const curTeamSelect = document.getElementById('team');
                if (newTeamSelect && curTeamSelect) {
                    curTeamSelect.value = newTeamSelect.value;
                    const teamPillVal = document.querySelector('.search-select[data-label="team"] .ss-value');
                    if (teamPillVal) {
                        const selTeamOpt = curTeamSelect.options[curTeamSelect.selectedIndex];
                        teamPillVal.textContent = selTeamOpt ? selTeamOpt.textContent.trim() : 'ALL TEAMS';
                        teamPillVal.classList.toggle('is-empty', !curTeamSelect.value);
                    }
                }

                // 3. Update Celebration Container
                const newOverlay = doc.getElementById('celebration-overlay-container');
                const curOverlay = document.getElementById('celebration-overlay-container');
                if (newOverlay && curOverlay) {
                    curOverlay.innerHTML = newOverlay.innerHTML;
                } else if (curOverlay) {
                    curOverlay.innerHTML = '';
                }

                // 4. Update Filter Active Badge
                const newCount = doc.getElementById('filter-active-count');
                const curCount = document.getElementById('filter-active-count');
                if (newCount && curCount) {
                    curCount.textContent = newCount.textContent;
                }

                // 5. Update browser URL without reload
                if (pushHistory) {
                    const params = new URLSearchParams();
                    const teamVal = form.team ? form.team.value : '';
                    if (teamVal) params.set('team', teamVal);
                    if (empVal) params.set('employee', empVal);
                    if (monthVal) params.set('month', monthVal);
                    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
                    window.history.pushState({ team: teamVal, employee: empVal, month: monthVal }, '', newUrl);
                }

                // 6. Rebind events & restart celebration if applicable
                attachDynamicEventListeners();
                initCelebrationAnimation();

            } catch (err) {
                console.error('AJAX update error, submitting form normally:', err);
                form.submit();
                return;
            } finally {
                setUpdatingState(false);
            }
        }

        function togglePharmaDrawer(btn) {
            const card = btn.closest('.pharma-prod-card');
            if (!card) return;
            const drawer = card.querySelector('.pharma-drawer');
            const chevron = btn.querySelector('.pharma-chevron');
            const textSpan = btn.querySelector('.toggle-text');
            if (!drawer) return;

            const isOpen = drawer.classList.toggle('open');
            btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            if (chevron) chevron.classList.toggle('rotated', isOpen);
            if (textSpan) textSpan.textContent = isOpen ? 'Hide Details' : 'Show Details & Remarks';
        }

        function toggleAllPharmaDrawers(expand) {
            document.querySelectorAll('.pharma-prod-card').forEach(function(card) {
                const drawer = card.querySelector('.pharma-drawer');
                const btn = card.querySelector('.pharma-drawer-toggle');
                const chevron = btn ? btn.querySelector('.pharma-chevron') : null;
                const textSpan = btn ? btn.querySelector('.toggle-text') : null;
                if (!drawer) return;

                if (expand) {
                    drawer.classList.add('open');
                    if (btn) btn.setAttribute('aria-expanded', 'true');
                    if (chevron) chevron.classList.add('rotated');
                    if (textSpan) textSpan.textContent = 'Hide Details';
                } else {
                    drawer.classList.remove('open');
                    if (btn) btn.setAttribute('aria-expanded', 'false');
                    if (chevron) chevron.classList.remove('rotated');
                    if (textSpan) textSpan.textContent = 'Show Details & Remarks';
                }
            });
        }


        function onTeamFilterChange(select) {
            const form = document.getElementById('filter-form');
            if (!form) return;
            // Clear employee selection so server picks the first employee from the newly selected team
            if (form.employee) form.employee.value = '';
            applyFilterUpdate();
        }

        function attachDynamicEventListeners() {
            // Final Remark accordions
            document.querySelectorAll('.crit-remark-header').forEach(function (header) {
                const bar = header.closest('.crit-remark-bar');
                if (bar) {
                    header.setAttribute('aria-expanded', bar.classList.contains('is-open') ? 'true' : 'false');
                }
                header.onkeydown = function (e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggleCritRemark(header);
                    }
                };
            });

            // Field Force Incentive Policy Rules accordion
            const policyToggle = document.getElementById('policy-rules-toggle');
            const policySection = document.querySelector('.incentive-table');
            if (policyToggle && policySection) {
                policyToggle.onclick = function () {
                    const isOpen = policySection.classList.toggle('is-open');
                    policyToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                };
            }

            // ASM Privilege Club accordion
            const asmPrivToggle = document.getElementById('asm-privilege-toggle');
            const asmPrivPanel = document.getElementById('asm-privilege-detail-panel');
            if (asmPrivToggle && asmPrivPanel) {
                asmPrivToggle.onclick = function () {
                    const isOpen = asmPrivPanel.classList.toggle('is-open');
                    asmPrivToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                };
            }

            // RSM Privilege Club accordion
            const rsmPrivToggle = document.getElementById('rsm-privilege-toggle');
            const rsmPrivPanel = document.getElementById('rsm-privilege-detail-panel');
            if (rsmPrivToggle && rsmPrivPanel) {
                rsmPrivToggle.onclick = function () {
                    const isOpen = rsmPrivPanel.classList.toggle('is-open');
                    rsmPrivToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                };
            }

            // Employee Info Preview Bar (closed by default; only opens on explicit Preview click)
            const infoBar = document.getElementById('emp-info-bar');
            const toggleBtn = document.getElementById('emp-info-toggle');
            if (infoBar) {
                userManuallyToggled = false;
                isClosedByScroll = true;
                infoBar.classList.remove('is-open');
                if (toggleBtn) {
                    toggleBtn.classList.remove('active');
                    toggleBtn.setAttribute('aria-expanded', 'false');
                    toggleBtn.onclick = function (e) {
                        e.preventDefault();
                        userManuallyToggled = true;
                        const isOpen = infoBar.classList.toggle('is-open');
                        toggleBtn.classList.toggle('active', isOpen);
                        toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                        isClosedByScroll = !isOpen;
                    };
                }

                if (!scrollListenerAttached) {
                    scrollListenerAttached = true;
                    window.addEventListener('scroll', function () {
                        const currentInfoBar = document.getElementById('emp-info-bar');
                        const currentToggleBtn = document.getElementById('emp-info-toggle');
                        if (!currentInfoBar) return;
                        const scrollY = window.scrollY || window.pageYOffset;
                        if (scrollY > 45 && !isClosedByScroll) {
                            currentInfoBar.classList.remove('is-open');
                            if (currentToggleBtn) {
                                currentToggleBtn.classList.remove('active');
                                currentToggleBtn.setAttribute('aria-expanded', 'false');
                            }
                            isClosedByScroll = true;
                        }
                    }, { passive: true });
                }
            }
        }

        function closeCelebration() {
            const overlay = document.getElementById('celebration-overlay');
            if (overlay) {
                overlay.style.opacity = '0';
                overlay.style.pointerEvents = 'none';
                setTimeout(() => {
                    overlay.remove();
                    if (celebrationAnimationId) {
                        cancelAnimationFrame(celebrationAnimationId);
                        celebrationAnimationId = null;
                    }
                }, 500);
            }
        }

        function initCelebrationAnimation() {
            if (celebrationAnimationId) {
                cancelAnimationFrame(celebrationAnimationId);
                celebrationAnimationId = null;
            }

            const overlay = document.getElementById('celebration-overlay');
            if (!overlay) return;

            const moneyContainer = document.getElementById('money-rain-container');
            if (moneyContainer) {
                moneyContainer.innerHTML = '';
                const moneyEmojis = ['💵', '💰', '💸', '🪙', '💲'];
                const clapEmojis = ['👏', '👏🏻', '🙌'];
                const numMoney = 42;

                for (let i = 0; i < numMoney; i++) {
                    const isClap = Math.random() < 0.3;
                    const item = document.createElement('div');
                    item.className = 'money-item' + (isClap ? ' money-rise' : '');
                    const pool = isClap ? clapEmojis : moneyEmojis;
                    item.textContent = pool[Math.floor(Math.random() * pool.length)];
                    const left = Math.random() * 95;
                    const delay = Math.random() * 5;
                    const duration = isClap ? (6 + Math.random() * 6) : (4.5 + Math.random() * 5);
                    const fontSize = (isClap ? 22 : 24) + Math.random() * 22;

                    item.style.left = left + '%';
                    item.style.fontSize = fontSize + 'px';
                    item.style.animationDelay = delay + 's';
                    item.style.animationDuration = duration + 's';

                    moneyContainer.appendChild(item);
                }
            }

            const canvas = document.getElementById('confetti-canvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');

            let width = canvas.width = window.innerWidth;
            let height = canvas.height = window.innerHeight;

            const particles = [];
            const cashBlues = ['#123C7A', '#2563EB', '#123C7A'];
            const coinGolds = ['#f1c40f', '#fbbf24', '#f59e0b'];
            const clapGlyphs = ['👏', '💰', '💵', '🪙'];

            for (let i = 0; i < 130; i++) {
                const roll = Math.random();
                const type = roll < 0.45 ? 'cash' : (roll < 0.75 ? 'coin' : 'clap');
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height - height,
                    size: Math.random() * 10 + 8,
                    type: type,
                    glyph: clapGlyphs[Math.floor(Math.random() * clapGlyphs.length)],
                    color: type === 'cash'
                        ? cashBlues[Math.floor(Math.random() * cashBlues.length)]
                        : coinGolds[Math.floor(Math.random() * coinGolds.length)],
                    vx: (Math.random() - 0.5) * 2,
                    vy: Math.random() * 3.2 + 2,
                    rotation: Math.random() * 360,
                    vRot: (Math.random() - 0.5) * 6,
                    oscSpeed: Math.random() * 0.05 + 0.02,
                    oscStep: Math.random() * Math.PI * 2
                });
            }

            function render() {
                if (!document.getElementById('confetti-canvas')) {
                    celebrationAnimationId = null;
                    return;
                }

                ctx.clearRect(0, 0, width, height);

                particles.forEach(p => {
                    p.y += p.vy;
                    p.oscStep += p.oscSpeed;
                    p.x += Math.sin(p.oscStep) * 1.8 + p.vx;
                    p.rotation += p.vRot;

                    if (p.y > height) {
                        p.y = -30;
                        p.x = Math.random() * width;
                    }

                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate((p.rotation * Math.PI) / 180);

                    if (p.type === 'cash') {
                        // Cash note: blue note with gold border + Rs text
                        const w = p.size * 3.2;
                        const h = p.size * 1.7;
                        ctx.fillStyle = p.color;
                        ctx.strokeStyle = '#fbbf24';
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.rect(-w / 2, -h / 2, w, h);
                        ctx.fill();
                        ctx.stroke();
                        ctx.fillStyle = '#ffffff';
                        ctx.font = `bold ${Math.round(h * 0.55)}px Inter, Arial, sans-serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('Rs', 0, 1);
                    } else if (p.type === 'coin') {
                        // Gold coin with Rs symbol
                        const r = p.size * 0.95;
                        ctx.beginPath();
                        ctx.arc(0, 0, r, 0, Math.PI * 2);
                        ctx.fillStyle = p.color;
                        ctx.fill();
                        ctx.lineWidth = 2.5;
                        ctx.strokeStyle = '#92400e';
                        ctx.stroke();
                        ctx.fillStyle = '#0B1F44';
                        ctx.font = `bold ${Math.round(r * 1.1)}px Inter, Arial, sans-serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('₹', 0, 1);
                    } else {
                        ctx.font = `${Math.round(p.size * 2.4)}px "Segoe UI Emoji", "Apple Color Emoji", sans-serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(p.glyph, 0, 0);
                    }
                    ctx.restore();
                });

                celebrationAnimationId = requestAnimationFrame(render);
            }

            render();

            setTimeout(() => {
                const curOverlay = document.getElementById('celebration-overlay');
                if (curOverlay) {
                    curOverlay.classList.add('faded');
                }
            }, 9000);
        }

        // Intercept form submit and popstate
        document.addEventListener('DOMContentLoaded', function () {
            attachDynamicEventListeners();
            initCelebrationAnimation();

            const filterForm = document.getElementById('filter-form');
            if (filterForm) {
                filterForm.addEventListener('submit', function (e) {
                    e.preventDefault();
                    applyFilterUpdate();
                });
            }

            window.addEventListener('popstate', function (e) {
                const form = document.getElementById('filter-form');
                if (!form) return;
                const urlParams = new URLSearchParams(window.location.search);
                const teamParam = urlParams.get('team') || '';
                const empParam = urlParams.get('employee') || '';
                const monthParam = urlParams.get('month') || 'July,26';
                if (form.team) form.team.value = teamParam;
                if (form.employee) form.employee.value = empParam;
                if (form.month) form.month.value = monthParam;

                // Sync custom select display labels
                document.querySelectorAll('.search-select').forEach(function (wrap) {
                    var select = wrap.querySelector('.ss-native-select');
                    var valEl = wrap.querySelector('.ss-value');
                    if (select && valEl) {
                        var idx = select.selectedIndex;
                        var sel = idx >= 0 ? select.options[idx] : null;
                        if (sel && sel.value !== '') {
                            valEl.textContent = sel.textContent.trim();
                            valEl.classList.remove('is-empty');
                        } else {
                            valEl.textContent = 'ALL';
                            valEl.classList.add('is-empty');
                        }
                    }
                });

                applyFilterUpdate(false);
            });
        });

/* ==========================================================================
           Searchable filter dropdowns (Employee & Reporting Month)
           ========================================================================== */
        (function () {
            function initSearchSelects() {
                var wraps = document.querySelectorAll('.search-select');
                if (!wraps.length) return;

                wraps.forEach(function (wrap) {
                    var select = wrap.querySelector('.ss-native-select');
                    var trigger = wrap.querySelector('.search-select-trigger');
                    var valueEl = wrap.querySelector('.ss-value');
                    var panel = wrap.querySelector('.ss-panel');
                    var optionsBox = wrap.querySelector('.ss-options');
                    var searchInput = wrap.querySelector('.ss-search-input');
                    var emptyMsg = wrap.querySelector('.ss-empty');

                    if (!select || !trigger || !panel || !optionsBox || !searchInput) return;

                    function makeOptionRow(value, label) {
                        var row = document.createElement('div');
                        row.className = 'ss-option';
                        row.setAttribute('role', 'option');
                        row.tabIndex = 0;
                        row.dataset.value = value;
                        row.textContent = label;
                        return row;
                    }

                    function renderAll() {
                        optionsBox.innerHTML = '';
                        Array.prototype.forEach.call(select.options, function (opt) {
                            optionsBox.appendChild(makeOptionRow(opt.value, opt.textContent.trim()));
                        });
                        markSelected();
                    }

                    function markSelected() {
                        var rows = optionsBox.querySelectorAll('.ss-option');
                        rows.forEach(function (row) {
                            row.classList.toggle('is-selected', row.dataset.value === select.value);
                        });
                    }

                    function syncLabel() {
                        var idx = select.selectedIndex;
                        var sel = idx >= 0 ? select.options[idx] : null;
                        if (sel && sel.value !== '') {
                            valueEl.textContent = sel.textContent.trim();
                            valueEl.classList.remove('is-empty');
                        } else {
                            valueEl.textContent = 'ALL';
                            valueEl.classList.add('is-empty');
                        }
                    }

                    function isOpen() {
                        return wrap.classList.contains('is-open');
                    }

                    function open() {
                        wrap.classList.add('is-open');
                        trigger.setAttribute('aria-expanded', 'true');
                        renderAll();
                        searchInput.value = '';
                        showAll();
                        searchInput.focus();
                    }

                    function close() {
                        wrap.classList.remove('is-open');
                        trigger.setAttribute('aria-expanded', 'false');
                        syncLabel();
                    }

                    function showAll() {
                        Array.prototype.forEach.call(optionsBox.children, function (row) { row.hidden = false; });
                        emptyMsg.hidden = true;
                    }

                    function filter() {
                        var query = (searchInput.value || '').toLowerCase().trim();
                        var visible = 0;
                        Array.prototype.forEach.call(optionsBox.children, function (row) {
                            var match = row.textContent.toLowerCase().indexOf(query) !== -1;
                            row.hidden = !match;
                            if (match) visible++;
                        });
                        emptyMsg.hidden = visible > 0;
                    }

                    function visibleRows() {
                        return Array.prototype.filter.call(optionsBox.children, function (row) { return !row.hidden; });
                    }

                    function selectRow(row) {
                        select.value = row.dataset.value;
                        markSelected();
                        close();
                        // Trigger the change event which seamlessly calls applyFilterUpdate()
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                    trigger.addEventListener('click', function (e) {
                        e.stopPropagation();
                        if (isOpen()) { close(); } else { open(); }
                    });

                    trigger.addEventListener('keydown', function (e) {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            if (isOpen()) { close(); } else { open(); }
                        } else if (e.key === 'Escape') {
                            close();
                        }
                    });

                    searchInput.addEventListener('input', filter);

                    searchInput.addEventListener('keydown', function (e) {
                        if (e.key === 'Escape') { close(); return; }
                        if (e.key === 'Enter' || e.key === 'ArrowDown') {
                            e.preventDefault();
                            var rows = visibleRows();
                            if (rows.length > 0) {
                                if (e.key === 'Enter') { selectRow(rows[0]); }
                                else { rows[0].focus(); }
                            }
                        }
                    });

                    optionsBox.addEventListener('click', function (e) {
                        var row = e.target.closest('.ss-option');
                        if (row) selectRow(row);
                    });

                    optionsBox.addEventListener('keydown', function (e) {
                        var rows = visibleRows();
                        if (rows.length === 0) return;
                        var idx = rows.indexOf(document.activeElement);

                        if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            rows[Math.min(idx + 1, rows.length - 1)].focus();
                        } else if (e.key === 'ArrowUp') {
                            e.preventDefault();
                            rows[Math.max(idx - 1, 0)].focus();
                        } else if (e.key === 'Enter') {
                            e.preventDefault();
                            if (idx >= 0) selectRow(rows[idx]);
                        } else if (e.key === 'Escape') {
                            close();
                        } else if (e.key === 'Tab') {
                            close();
                        }
                    });

                    document.addEventListener('click', function (e) {
                        if (!wrap.contains(e.target)) close();
                    });

                    // Initial state
                    renderAll();
                    syncLabel();
                });
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initSearchSelects);
            } else {
                initSearchSelects();
            }
        })();

        // Pharma RSM Table Filter
        function filterPharmaRSMRows(type, btn) {
            document.querySelectorAll('.pharma-rsm-filter-btn').forEach(function (b) { b.classList.remove('active'); });
            if (btn) btn.classList.add('active');
            var rows = document.querySelectorAll('#pharma-rsm-staff-table tbody tr.pharma-rsm-row');
            rows.forEach(function (r) {
                var desg = (r.getAttribute('data-desg') || '').toUpperCase();
                var isQual = r.getAttribute('data-qual') === '1';
                if (type === 'all') {
                    r.style.display = '';
                } else if (type === 'qualified') {
                    r.style.display = isQual ? '' : 'none';
                } else if (type === 'asm') {
                    r.style.display = (desg === 'ASM') ? '' : 'none';
                } else if (type === 'mio') {
                    r.style.display = (desg === 'MIO' || desg === 'PS') ? '' : 'none';
                }
            });
        }

