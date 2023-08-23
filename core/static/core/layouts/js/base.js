document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form").forEach(disable_form_submit_elem_on_submit);
    const tooltip_trigger_list = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    // Initialize tooltips
    const tooltipList = [...tooltip_trigger_list].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
});
