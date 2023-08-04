//This allows us to use a single update form on the page while updating the inputs with a clicked object's data defined via 'data-initial' attribute
// Elements that require this feature are defined with a data-preinit and data-initial attributes to prefill the forms
document.addEventListener("DOMContentLoaded", function() {
   let modals = Array.from(document.querySelectorAll("[data-bs-toggle=modal]"))
       .filter((elem) => elem.hasAttribute("data-preinit"))
       .map(function(elem) {
          const modal_id = elem.getAttribute("data-bs-target").slice(1); // Remove the hashtag(#)
          return document.getElementById(modal_id);
   });
   modals.forEach(function(modal) {
      modal.addEventListener("show.bs.modal", function (event) {
         let modal_trigger = event.relatedTarget;
         let initial_form_data = JSON.parse(modal_trigger.getAttribute("data-initial"));
         Object.keys(initial_form_data).forEach(function (field_name) {
            // Each field corresponds to a model field name, and django assigns each field an id of the form:
            // id_<field_name>, Be wary of pages might have duplicate IDs(it's invalid HTML), and to resolve
            // this, we search below the displayed modal using modal.querySelector() and not the whole document
            // because each modal is bound to have one element with that ID
            let input_id = `#id_${field_name}`
            if (field_name === "phone_no") input_id = `${input_id}_1`; // Special case - renaming caused by prefix widget
            const input_elem = modal.querySelector(input_id);
            if (input_elem !== null) {
               input_elem.value = initial_form_data[field_name];
            }
         });
         // Set submit url of the form contained in the modal
         modal.querySelector("form").action = modal_trigger.getAttribute("data-href")
      });
   });
});
