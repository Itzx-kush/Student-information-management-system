/**
 * Week 8 — Student Management & Git Workflow Lab
 * Interactive Client-Side JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const mobileToggleBtn = document.getElementById('mobileToggleBtn');
    const appSidebar = document.querySelector('.app-sidebar');

    if (mobileToggleBtn && appSidebar) {
        mobileToggleBtn.addEventListener('click', () => {
            appSidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 &&
                appSidebar.classList.contains('open') &&
                !appSidebar.contains(e.target) &&
                e.target !== mobileToggleBtn) {
                appSidebar.classList.remove('open');
            }
        });
    }

    // 2. Alert Dismissal
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 3. Copy to Clipboard
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            let textToCopy = '';

            if (targetId) {
                const targetEl = document.getElementById(targetId);
                textToCopy = targetEl ? targetEl.innerText.trim() : '';
            } else if (btn.getAttribute('data-clipboard-text')) {
                textToCopy = btn.getAttribute('data-clipboard-text');
            } else {
                const row = btn.closest('.command-row');
                if (row) {
                    const cmdEl = row.querySelector('.cmd-text');
                    textToCopy = cmdEl ? cmdEl.innerText.trim() : '';
                }
            }

            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalText = btn.innerText;
                    btn.innerText = 'Copied!';
                    btn.style.backgroundColor = '#10b981';
                    setTimeout(() => {
                        btn.innerText = originalText;
                        btn.style.backgroundColor = '';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                });
            }
        });
    });

    // 4. Modal Confirmation Dialogs for Form Deletion
    const confirmModal = document.getElementById('confirmModal');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');
    const modalItemName = document.getElementById('modalItemName');
    let pendingForm = null;

    document.querySelectorAll('.btn-delete-confirm').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            pendingForm = btn.closest('form');
            const itemName = btn.getAttribute('data-item-name') || 'this item';

            if (confirmModal) {
                if (modalItemName) modalItemName.textContent = itemName;
                confirmModal.classList.add('active');
            } else {
                if (confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                    if (pendingForm) pendingForm.submit();
                }
            }
        });
    });

    if (modalCancelBtn && confirmModal) {
        modalCancelBtn.addEventListener('click', () => {
            confirmModal.classList.remove('active');
            pendingForm = null;
        });
    }

    if (modalConfirmBtn && confirmModal) {
        modalConfirmBtn.addEventListener('click', () => {
            if (pendingForm) {
                pendingForm.submit();
            }
            confirmModal.classList.remove('active');
        });
    }

    // 5. Interactive Git Checklist Toggle (Module E / Question C)
    document.querySelectorAll('.checklist-checkbox').forEach(box => {
        box.addEventListener('change', async () => {
            const itemId = box.getAttribute('data-item-id');
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
            const isChecked = box.checked;

            try {
                const formData = new FormData();
                formData.append('item_id', itemId);
                formData.append('status', isChecked);
                formData.append('csrf_token', csrfToken);

                const response = await fetch('/git/checklist/toggle', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    const countEl = document.getElementById('checklistCompletedCount');
                    const fillEl = document.getElementById('checklistProgressFill');
                    const pctEl = document.getElementById('checklistProgressPct');

                    if (countEl) countEl.textContent = data.completed_count;
                    if (fillEl) fillEl.style.width = `${data.progress_percentage}%`;
                    if (pctEl) pctEl.textContent = `${data.progress_percentage}%`;
                }
            } catch (err) {
                console.error('Error toggling checklist:', err);
            }
        });
    });

    // 6. Interactive Course Registration Live Seat Checker
    const courseSelect = document.getElementById('course_id_select');
    const seatIndicator = document.getElementById('seatIndicator');

    if (courseSelect && seatIndicator) {
        function updateSeatInfo() {
            const selectedOpt = courseSelect.options[courseSelect.selectedIndex];
            if (!selectedOpt || !selectedOpt.value) {
                seatIndicator.innerHTML = '<span class="text-muted">Select a course to view available seats.</span>';
                return;
            }

            const seats = parseInt(selectedOpt.getAttribute('data-seats') || '0', 10);
            const maxSeats = parseInt(selectedOpt.getAttribute('data-max') || '0', 10);

            if (seats <= 0) {
                seatIndicator.innerHTML = `
                    <span class="badge badge-danger">Class Full (0 / ${maxSeats} seats available)</span>
                    <span style="color: var(--danger-600); font-size: 0.82rem; margin-left: 8px;">Registration disabled.</span>
                `;
            } else if (seats <= 5) {
                seatIndicator.innerHTML = `
                    <span class="badge badge-warning">${seats} / ${maxSeats} seats available (Filling Fast!)</span>
                `;
            } else {
                seatIndicator.innerHTML = `
                    <span class="badge badge-success">${seats} / ${maxSeats} seats available</span>
                `;
            }
        }

        courseSelect.addEventListener('change', updateSeatInfo);
        updateSeatInfo();
    }
});
