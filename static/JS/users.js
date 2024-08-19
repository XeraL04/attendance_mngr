document.addEventListener('DOMContentLoaded', function () {
    const usersTableBody = document.querySelector('#users-table tbody');

    // Fetch the users data
    fetch('/api/users')
        .then(response => response.json())
        .then(users => {
            users.forEach(user => {
                const row = document.createElement('tr');
                row.dataset.userId = user.id;  // Set the user ID as a data attribute
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.first_name}</td>
                    <td>${user.last_name}</td>
                    <td>${user.email}</td>
                    <td>${user.phone}</td>
                    <td>${user.attendance_id}</td>
                `;
                usersTableBody.appendChild(row);
            });

            // Re-add click event listeners after rows are added
            const tableRows = document.querySelectorAll('#users-table tbody tr');
            tableRows.forEach(row => {
                row.addEventListener('click', function () {
                    const userId = row.dataset.userId;
                    window.location.href = `/attendance?user_id=${userId}`;
                });
            });
        });
});
