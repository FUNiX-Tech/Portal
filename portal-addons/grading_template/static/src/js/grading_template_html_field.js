/** @odoo-module **/

import { HtmlField } from "@web_editor/js/backend/html_field";
import { registry } from "@web/core/registry";
import { getWysiwygClass } from 'web_editor.loader';
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class GradingTemplateHtmlField extends HtmlField {
    async _getWysiwygClass() {
        return getWysiwygClass({ moduleName: 'grading_template.wysiwyg' });
    }
}

GradingTemplateHtmlField.props = {
    ...standardFieldProps,
    ...HtmlField.props,
};

GradingTemplateHtmlField.displayName = "Grading Template Html Field";
GradingTemplateHtmlField.supportedTypes = ["html"];

registry.category("fields").add("grading_template_html", GradingTemplateHtmlField);

export default GradingTemplateHtmlField;
