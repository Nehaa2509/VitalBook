document.addEventListener("DOMContentLoaded", function() {
    const appointmentSelect = document.getElementById('id_appointment');
    if (!appointmentSelect) return;

    const medicinesTextarea = document.getElementById('id_medicines');
    const formRow = appointmentSelect.closest('.form-row');

    // Create a container to show the fetched details
    const detailsContainer = document.createElement('div');
    detailsContainer.style.marginTop = '10px';
    detailsContainer.style.padding = '10px';
    detailsContainer.style.backgroundColor = '#f8faff';
    detailsContainer.style.border = '1px solid #cce5ff';
    detailsContainer.style.borderRadius = '5px';
    detailsContainer.style.color = '#004085';
    detailsContainer.style.display = 'none';
    detailsContainer.innerHTML = '<strong><i class="fas fa-spinner fa-spin"></i> Fetching appointment details...</strong>';
    
    formRow.appendChild(detailsContainer);

    function fetchAppointmentDetails(appointmentId) {
        if (!appointmentId) {
            detailsContainer.style.display = 'none';
            return;
        }

        detailsContainer.style.display = 'block';
        detailsContainer.innerHTML = '<strong><i class="fas fa-spinner fa-spin"></i> Fetching appointment details...</strong>';

        fetch(`/api/admin/appointment/${appointmentId}/details/`, { credentials: 'same-origin' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    detailsContainer.style.backgroundColor = '#f8d7da';
                    detailsContainer.style.color = '#721c24';
                    detailsContainer.style.border = '1px solid #f5c6cb';
                    detailsContainer.innerHTML = `<strong>Error:</strong> ${data.error}`;
                    return;
                }

                // Update info block
                detailsContainer.style.backgroundColor = '#d4edda';
                detailsContainer.style.color = '#155724';
                detailsContainer.style.border = '1px solid #c3e6cb';
                detailsContainer.innerHTML = `
                    <div style="font-size: 14px; margin-bottom: 5px;"><strong>Patient:</strong> ${data.patient_name}</div>
                    <div style="font-size: 14px; margin-bottom: 5px;"><strong>Doctor:</strong> Dr. ${data.doctor_name}</div>
                    <div style="font-size: 14px;"><strong>Specialization:</strong> ${data.doctor_specialization}</div>
                `;

                // Auto-fill medicines if empty
                if (medicinesTextarea && medicinesTextarea.value.trim() === '') {
                    medicinesTextarea.value = data.suggested_medicines;
                    // Highlight briefly to show it was auto-filled
                    const originalBg = medicinesTextarea.style.backgroundColor;
                    medicinesTextarea.style.backgroundColor = '#e2ffe2';
                    setTimeout(() => {
                        medicinesTextarea.style.backgroundColor = originalBg;
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('Error fetching appointment details:', error);
                detailsContainer.style.backgroundColor = '#f8d7da';
                detailsContainer.style.color = '#721c24';
                detailsContainer.style.border = '1px solid #f5c6cb';
                detailsContainer.innerHTML = `<strong>Error fetching data.</strong> Please try again.`;
            });
    }

    // Trigger on change
    appointmentSelect.addEventListener('change', function(e) {
        fetchAppointmentDetails(e.target.value);
    });

    // Trigger on initial load if an appointment is pre-selected (e.g. returning to page)
    if (appointmentSelect.value) {
        fetchAppointmentDetails(appointmentSelect.value);
    }
});
