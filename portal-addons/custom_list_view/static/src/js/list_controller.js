/** @odoo-module */

/**
 * 1. patch is a built in utils function provided by web core library of odoo, it is used to modify an object, extend it or add new properties.
 * 2. download is an Odoo custom function that is used to download a file from the server.
 * 3. jsonrpc is an Odoo custom function that is used to make an rpc call to the server.
 *
 */

import {patch} from '@web/core/utils/patch'
import {ListController} from '@web/views/list/list_controller'
import {download} from '@web/core/network/download'
import {jsonrpc} from '@web/core/network/rpc_service'

// Dialog is a built in widget provided by web core library of odoo.
let Dialog = require('web.Dialog')


/**
 * patch method expects 3 arguments
 * 1. obj : the object to be patched
 * 2. patchName: a unique name for the patch
 * 3. patchValue: the patch itself, which is an object containing modified properties or methods.
 * 4. options: the optional object.
 */

const patchingObj = {
    // ============= Duplicate Records =============
        async _onDuplicateSelectedRecords() {
            for (var record in this.model.root.records) {
                if (this.model.root.records[record].selected) {
                    await this.model.root.records[record].duplicate();
                }
            }
            window.location.reload();
        },
        /**
         * Get the action menu items and add a "Duplicate" option.
         *
         * @returns {Object} Action menu items.
         */
        getActionMenuItems() {
            const actionMenuItems = this._super.apply(this, arguments);
            var self = this;
            if (actionMenuItems) {
                actionMenuItems.other.splice(1, 0, {
                    description: this.env._t("Duplicate"),
                    callback: (x) => {
                        this._onDuplicateSelectedRecords();
                    }
                });
            }
            return actionMenuItems;
        },

        _onClickPDF: async function() {
            try {
                // Retrieve the fields to export
                const fields = this.props.archInfo.columns
                    .filter((col) => col.optional === false || col.optional === "show")
                    .map((col) => this.props.fields[col.name]);
                const exportFields = fields.map((field) => ({
                    name: field.name,
                    label: field.label || field.string,
                }));
                const resIds = await this.getSelectedResIds();
                const length_field = Array.from(Array(exportFields.length).keys());

                // Make a JSON-RPC request to retrieve the data for the report
                const data = await jsonrpc(this.env, null, '/get-data', {
                    'model': this.model.root.resModel,
                    'res_ids': resIds.length > 0 && resIds,
                    'fields': exportFields,
                    'grouped_by': this.model.root.groupBy,
                    'context': this.props.context,
                    'domain': this.model.root.domain,
                });


                return this.model.action.doAction({
                    type: "ir.actions.report",
                    report_type: "qweb-pdf",
                    report_name: 'custom_list_view.print_pdf_listview',
                    report_file: "custom_list_view.print_pdf_listview",
                    data: {
                        'length': length_field,
                        'record': data
                    }
                });
            } catch (error) {
                // Handle any errors here
                console.error("Error:", error);
            }
        },
    // ============= Excel Export =============
    _onClickExcel: async function () {
        // Retrieve the fields to export
        // console.log('1. ', this.props.archInfo.columns)
        // console.log('2. ', this.props.archInfo.columns.filter((column) => column.optional === false || column.optional === 'show'))
        // console.log('3. ', this.props.archInfo.columns.filter((column) => column.optional === false || column.optional === 'show').map((column) => this.props.fields[column.name]))
        // console.log('4. ', this.props.archInfo.columns.filter((column) => column.optional === false || column.optional === 'show').map((column) => this.props.fields[column.name]).filter((field) => field.exportable !== false))

        const fields = this.props.archInfo.columns
            .filter((column) => column.optional === false || column.optional === 'show')
            .map((column) => this.props.fields[column.name])
            .filter((field) => field.exportable !== false);

        // console.log('5. ', fields)

        const exportFields = fields.map((field => ({
            name: field.name,
            label: field.label || field.string,
            store: field.store,
            type: field.field_type || field.type
        })))

        // console.log('6. Export fields ',exportFields)

        const resIds = await this.getSelectedResIds();
        // console.log('7. ', resIds)

        const import_compatibility = false

        // Make a request to '/web/export/xlsx' to download the Excel file

        const data_body = {
            import_compat: import_compatibility,
            context: this.props.context,
            domain: this.model.root.domain,
            fields: exportFields,
            groupby: this.model.root.groupBy,
            ids: resIds.length > 0 && resIds,
            model: this.model.root.resModel,
        }

        console.log("8. Data body to download ::",data_body)

        await download({
            data: {
                data: JSON.stringify(data_body)
            },
            url: `/web/export/xlsx`
        })
    },


    // ============= CSV Export ===============
    _onClickCSV: async function () {
      // Same as the Excel export but different URL
        const fields = this.props.archInfo.columns
        .filter((column) => column.optional === false || column.optional === "show")
        .map((column) => this.props.fields[column.name])
        .filter((field) => field.exportable !== false);
    const exportFields = fields.map((field) => ({
        name: field.name,
        label: field.label || field.string,
        store: field.store,
        type: field.field_type || field.type,
    }));
    const resIds = await this.getSelectedResIds();
    const import_compat = false
    // Make a request to download the CSV file

    const data_body = {
        import_compat,
        context: this.props.context,
        domain: this.model.root.domain,
        fields: exportFields,
        groupby: this.model.root.groupBy,
        ids: resIds.length > 0 && resIds,
        model: this.model.root.resModel,
    }

    await download({
        data: {
            data: JSON.stringify(data_body),
        },
        url: `/web/export/csv`,
    });
    },

    _onClickCopy: async function() {
        try {
            // Retrieve the fields to export
            const fields = this.props.archInfo.columns
                .filter((column) => column.type === 'field')
                .map((column) => this.props.fields[column.name]);

            const exportFields = fields.map((field) => ({
                name: field.name,
                label: field.label || field.string
            }))

            const resIds = await this.getSelectedResIds();

            // Use the jsonrpc to make JSON-RPC request for /get-data/copy in controller.py
            // console.log(this.model.root.resModel)
            const data_body = {
                'model': this.model.root.resModel,
                'res_ids':resIds.length > 0 && resIds,
                'fields': exportFields,
                "grouped_by": this.model.root.groupBy,
                'context': this.props.context,
                'domain': this.model.root.domain
            }
            // console.log('data_body', data_body)

            const data = await jsonrpc(this.env,null,'/get-data/copy',data_body)

            // console.log('data response from /get_data/copy', data)

            // Format the data as text and copy it to the clipboard
            const textArray = data.map(record => record.join('\t'))
            // console.log('textArray', textArray)
            const text = textArray.join('\n')
            // console.log('text', text)

            await navigator.clipboard.writeText(text);
            Dialog.alert(this, "Records copied to clipboard",{});

        } catch (error) {
            console.error("Error: ", error);
        }
    },

    _onClickImport: async function() {
            window.location.href = `/web#model=${this.model.root.resModel}&action=import`
    }

}

patch(ListController.prototype,"CustomListView", patchingObj)
