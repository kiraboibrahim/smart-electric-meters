/* This allows us to use a single update form for numerous entities of the same type i.e. users, meters on the same page
* by just updating the form inputs with the selected(clicked) object's data defined via 'data-initial' attribute.
* The form is expected to be wrapped in a boostrap modal. Once the modal is shown(visible), the form is initialized with
*  the selected entity values. It is assumed that only one form is in the modal. For cases where the there is > 1 form
* in the modal, one can code to handle such cases.
* data-preinit and data-initial attributes should be defined on the element that defines the data-bs-toggle attribute
* in order to use this feature.
*/
document.addEventListener("DOMContentLoaded", function () {
    const get_modals_on_page = function () {
        return Array.from(document.querySelectorAll("[data-bs-toggle=modal]"))
            .filter((elem) => elem.hasAttribute("data-preinit"))
            .map(function (elem) {
                const modal_id = elem.getAttribute("data-bs-target").slice(1); // Remove the hashtag(#)
                return document.getElementById(modal_id);
            });
    }
    const initialize_form_in_modal = function(modal) {
        modal.addEventListener("show.bs.modal", function (event) {
                let modal_trigger = event.relatedTarget;
                let initial_form_data = JSON.parse(modal_trigger.getAttribute("data-initial"));
                Object.keys(initial_form_data).forEach(function (field_name) {
                    /* Each key in initial_form_data corresponds to a form field name, and django assigns each field an id of
                    * the structure: id_<field_name>, Be wary of pages might have duplicate IDs(it's invalid HTML), and to resolve
                    * this, we only search below the displayed modal using modal.querySelector() and not the whole document
                    * because each modal is bound to have one element with that ID.
                    */
                    let input_id = `#id_${field_name}`  // Derive the ID assigned by django
                    /*
                    * This is a special case that defies the ID naming of django forms because it uses a PhoneNumberPrefix
                    * widget from a third party package(django_phone_numbers) that splits the phone number field into 2 parts
                    * (country code & local number part). Besides creating two fields from one, It also modifies their ID's by
                    * appending a 0 on country code field(phone_no_0) and a 1 on the local number field(phone_no_1).
                    * However, they retain the parent field ID in their ID's i.e. phone_no
                    */
                    if (field_name === "phone_no" || field_name === "pay_with") input_id = `${input_id}_1`; // Only fill the national number field
                    const input_elem = modal.querySelector(input_id);
                    if (input_elem !== null) input_elem.value = initial_form_data[field_name];
                });
                // Set submit url of the form contained in the modal. The submission url is saved in the data-href attribute
                modal.querySelector("form").action = modal_trigger.getAttribute("data-href")
            });
    }
    const modals = get_modals_on_page();
    modals.forEach(initialize_form_in_modal);
    /*
    * Disable submit buttons of forms in order to prevent submitting forms more than one due to latency that may be
    * experienced during form submission.
    */
    const disable_submit_btn_on_form_submit = function(form) {
        form.addEventListener("submit", function (event) {
            const submit_btn = form.querySelector("[type=submit]");
            if (submit_btn !== null) submit_btn.setAttribute("disabled", "disabled");
        });
    }
    document.querySelectorAll("form").forEach(disable_submit_btn_on_form_submit)
});
