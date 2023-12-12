/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onMounted, useRef } from "@odoo/owl";

// field này = APPEND_ID ở wysiwyg.js
const APPEND_ID = '94713822-9650-11ee-b9d1-0242ac120002'
const EDITOR_SELECTOR = '#feedback'

export class MaterialField extends CharField {
    setup() {
        super.setup();

        this.state = useState({ is_appended: false });

        this.append_btn = useRef('append_btn')
        this.material_item = useRef("material_item")

        onMounted(this.onMounted)
    }

    onMounted() {
        this.append_btn.el.addEventListener('append', this.on_append_result.bind(this))
        this.material_item.el.addEventListener('editor_started', this.initState.bind(this))
    }

    on_append_result(event) {
        this.state.is_appended = this.props.record.data.id == event.detail.material_id
    }

    initState() {
        this.state.is_appended = !!document.querySelector(`div[data-append-id="${APPEND_ID}"][data-material-id="${this.props.record.data.id}"]`)
    }

    onMaterial(e) {
        e.stopPropagation()

        const btn = e.currentTarget
        const url = this.props.record.data.url
        const label = this.props.record.data.label
        const append_data = this.props.record.data.append
        const material_id = String(this.props.record.data.id)

        let action_type

        if ($(btn).data('action-type') !== 'append') {
            action_type = $(btn).data('action-type')
        } else {
            action_type = this.state.is_appended ? 'unappend' : 'append'
        }

        const event = new CustomEvent("material", {
            detail: {
                url,
                label,
                action_type,
                append_data,
                material_id
            }
        });

        document.querySelector(EDITOR_SELECTOR).dispatchEvent(event);
    }

}

MaterialField.template = "learning_project.MaterialField";
MaterialField.props = {
    ...standardFieldProps,
    ...CharField.props,
};

MaterialField.displayName = "Material Field";

registry.category("fields").add("material_field", MaterialField);

export default MaterialField;
