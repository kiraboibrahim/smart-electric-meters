const initialize_select2_field = function (select2_options) {
    const {field_selector, field_placeholder, dropdown_parent_selector} = select2_options;
    const options = {
        width: "100%",
        minimumInputLength: 2,
        placeholder: `${field_placeholder}`,
        dropdownParent: $(`${dropdown_parent_selector}`),
        allowClear: true
    }
    $(`${field_selector}`).select2(options);
}

const initialize_select2_manager_list_field = function (field_selector, dropdown_parent_selector) {
    const options = {
        field_selector: `${field_selector}`,
        field_placeholder: "Type a manager's name to select",
        dropdown_parent_selector: `${dropdown_parent_selector}`
    }
    initialize_select2_field(options);
}

const disable_form_submit_elem_on_submit = function (form) {
    const submit_elem_selector = "[type=submit]";
    form.addEventListener("submit", function (event) {
        const submit_elem = form.querySelector(submit_elem_selector);
        if (submit_elem !== null) submit_elem.setAttribute("disabled", "disabled");
    });
}

const initialize_form_in_modal = function (form, modal, field_id_mapping = {}) {
    modal.addEventListener("show.bs.modal", function (event) {
        let modal_trigger = event.relatedTarget;
        const initial_data = JSON.parse(modal_trigger.getAttribute("data-form-initial"));
        Object.keys(initial_data).forEach(function (field_name) {
            let field_id = field_id_mapping[`${field_name}`] || `#id_${field_name}`;  // Derive the ID assigned by django forms
            const field_elem = form.querySelector(field_id);
            if(field_elem !== null) {
                const field_value = initial_data[field_name];
                if(field_elem.classList.contains("select2-hidden-accessible")) { // Select2 JS field
                    const jquery_field_elem = $(`${field_id}`);
                    jquery_field_elem.val(`${field_value}`);
                    jquery_field_elem.trigger("change");
                } else {
                    field_elem.value = field_value;
                }
            }
        });
        // Set submit url of the form contained in the modal. The submission url is saved in the data-form-action attribute
        form.action = modal_trigger.getAttribute("data-form-action")
    });
}

const inject_styles = function (styles) {
    const stylesheet = document.createElement("style");
    stylesheet.innerText = styles;
    document.head.appendChild(stylesheet);
}

// Credit goes to: https://stackoverflow.com/users/1312346/francesco-frassinelli
// Answered on: https://stackoverflow.com/questions/8029532/how-to-prevent-submitting-the-html-forms-input-field-value-if-it-empty/64029534#64029534
const remove_form_empty_values_on_submit = function (form) {
    form.addEventListener('formdata', function (event) {
        let form_data = event.formData;
        for (let [name, value] of Array.from(form_data.entries())) {
            if (value === '') form_data.delete(name);
        }
    });
}

const show_modal = function (modal_selector) {
    bootstrap.Modal.getOrCreateInstance(document.querySelector(modal_selector)).show();
}

window.legitsystems_utils = {
    show_modal,
    inject_styles,
    initialize_form_in_modal,
    initialize_select2_field,
    initialize_select2_manager_list_field,
    disable_form_submit_elem_on_submit,
    remove_form_empty_values_on_submit,
}
