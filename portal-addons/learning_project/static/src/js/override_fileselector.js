/** @odoo-module **/

import { FileSelector } from '@web_editor/components/media_dialog/file_selector';

const domain = new URL(window.location.href).origin;

function hasDomain(path) {
    return path.toLowerCase().startsWith("https://") || path.toLowerCase().startsWith("http://")
}

FileSelector.prototype.onUploaded = async function (attachment) {

    if (!hasDomain(attachment.image_src)) {
        attachment.image_src = domain + attachment.image_src
    }

    this.state.attachments = [attachment, ...this.state.attachments];

    this.selectAttachment(attachment);

    if (!this.props.multiSelect) {
        await this.props.save();
    }

    if (this.props.onAttachmentChange) {
        this.props.onAttachmentChange(attachment);
    }
}
