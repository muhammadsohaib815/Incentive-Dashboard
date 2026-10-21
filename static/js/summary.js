document.getElementById('summary-csv-btn')?.addEventListener('click', function () {
    const table = document.getElementById('employee-summary-table');
    if (!table) return;
    const rows = Array.from(table.querySelectorAll('tr')).map(row =>
        Array.from(row.querySelectorAll('th, td')).map(cell => cell.textContent.replace(/\s+/g, ' ').trim())
    );
    const escapeCell = value => {
        let text = String(value);
        if (/^[=+@]|^-[^\d]/.test(text)) text = "'" + text;
        return '"' + text.replace(/"/g, '""') + '"';
    };
    const csv = '\uFEFF' + rows.map(row => row.map(escapeCell).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    const params = new URLSearchParams(window.location.search);
    link.href = url;
    link.download = `${params.get('category') || 'PHARMA'}_${params.get('month') || ''}_summary_page_${params.get('page') || '1'}.csv`
        .replace(/[^a-z0-9._-]+/gi, '_');
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
});
