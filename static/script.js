document.addEventListener('DOMContentLoaded', function() {
    fetch('/attendance')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#attendance-table tbody');
            data.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.first_name} ${record.last_name}</td>
                    <td>${new Date(record.timestamp).toLocaleString()}</td>
                    <td>${record.attendance_type}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching attendance data:', error));
});
