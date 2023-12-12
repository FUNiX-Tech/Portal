/** @odoo-module **/

import { HtmlField } from "@web_editor/js/backend/html_field";
import { registry } from "@web/core/registry";
import { getWysiwygClass } from 'web_editor.loader';
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ProjectGradingHtmlField extends HtmlField {
    async _getWysiwygClass() {
        return getWysiwygClass({ moduleName: 'learning_project.wysiwyg' });
    }
}

ProjectGradingHtmlField.props = {
    ...standardFieldProps,
    ...HtmlField.props,
};

ProjectGradingHtmlField.displayName = "Project Grading Html Field";
ProjectGradingHtmlField.supportedTypes = ["html"];

registry.category("fields").add("project_grading_html", ProjectGradingHtmlField);

export default ProjectGradingHtmlField;
