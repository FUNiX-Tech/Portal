/** @odoo-module */
import { useSetupView } from "@web/views/view_hook";
import { FormController } from "@web/views/form/form_controller";
import { ListController } from "@web/views/list/list_controller";
import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";

// Backup the original setup method of FormController
const oldSetup = FormController.prototype.setup;
// Backup the original onPagerUpdate method of FormController
const oldOnPagerUpdated = FormController.prototype.onPagerUpdate;

// Override the setup method of FormController
const Formsetup = function () {
    // Use the Odoo hook useSetupView to add custom behavior before leaving the view
    useSetupView({
        beforeLeave: () => {
            // Check if the form has unsaved changes
            if (this.model.root.isDirty) {
                // Prompt the user to save changes
                if (confirm("Do you want to save changes ?")) {
                    // If confirmed, save the changes
                    return this.model.root.save({noReload: true, stayInEdition: true});
                } else {
                    // If not confirmed, discard the changes
                    this.model.root.discard();
                    return true;
                }
            }
        },
    });
    // Call the original setup method
    const result = oldSetup.apply(this, arguments);
    return result;
};
// Assign the new setup method to FormController
FormController.prototype.setup = Formsetup;

// Override the onPagerUpdate method of FormController
const onPagerUpdate = await function () {
    // Check for any changes in the form
    this.model.root.askChanges();

    // If there are unsaved changes
    if (this.model.root.isDirty) {
        // Prompt the user to save changes
        if (confirm("Do you want to save changes ?")) {
            // If confirmed, proceed with the original onPagerUpdate method
            return oldOnPagerUpdated.apply(this, arguments);
        }
        // If not confirmed, discard the changes
        this.model.root.discard();
    }
    // Proceed with the original onPagerUpdate method
    return oldOnPagerUpdated.apply(this, arguments);
};

// Assign the new onPagerUpdate method to FormController
FormController.prototype.onPagerUpdate = onPagerUpdate

// Backup the original setup method of ListController
const ListSuper = ListController.prototype.setup
// Override the setup method of ListController
const ListSetup = function () {
    // Use the Odoo hook useSetupView to add custom behavior before leaving the view
    useSetupView({
        beforeLeave: () => {
            // Get the current list and the edited record
            const list = this.model.root;
            const editedRecord = list.getEditedRecord;
            // Check if the edited record is dirty (has unsaved changes)
            if (editedRecord && editedRecord.isDirty) {
                // Prompt the user to save changes
                if (confirm('Do you want to save changes ?')) {
                    // If confirmed, save the changes
                    if (!list.unselectNRecord(true)) {
                        throw new Error('Cannot save record');
                    }
                } else {
                    // If not confirmed, discard the changes
                    this.onClickDiscard();
                    return true;
                }
            }
        }
    })
    // Call the original setup method
    const result = ListSuper.apply(this, arguments)
    return result
}

// Assign the new setup method to ListController
ListController.prototype.setup = ListSetup
