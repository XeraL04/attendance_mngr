document.addEventListener('DOMContentLoaded', function () {
    const tableRows = document.querySelectorAll('#users-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function () {
            const userId = row.dataset.userId;
            window.location.href = `/attendance?user_id=${userId}`;
        });
    });
});