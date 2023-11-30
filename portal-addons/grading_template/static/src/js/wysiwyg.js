const TEMPLATES_LIB_MODAL_ID = "templates-lib-modal";
const TEMPLATES_LIB_CLASS = 'templates-lib'
const CSS_PATH = 'grading_template/static/src/css/grading_template_html_field.css'
const LIB_COMPONENT_CLASS = 'lib-component'
const STYLE_LINK_ID = 'grading_template_html_field_style'
const FETCH_TEMPLATES_API = "/api/v1/grading_template/templates"
const FETCH_COMPONENTS_API = "/api/v1/grading_template/components"
const BUTTON_CLASS = 'grading_template_btn'
const SVG_SUCCESS = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<path d="m10.6 13.8-2.15-2.15a.948.948 0 0 0-.7-.275.948.948 0 0 0-.7.275.948.948 0 0 0-.275.7c0 .283.092.517.275.7L9.9 15.9c.2.2.433.3.7.3.267 0 .5-.1.7-.3l5.65-5.65a.948.948 0 0 0 .275-.7.948.948 0 0 0-.275-.7.948.948 0 0 0-.7-.275.948.948 0 0 0-.7.275L10.6 13.8zM12 22a9.738 9.738 0 0 1-3.9-.788 10.099 10.099 0 0 1-3.175-2.137c-.9-.9-1.612-1.958-2.137-3.175A9.738 9.738 0 0 1 2 12c0-1.383.263-2.683.788-3.9a10.099 10.099 0 0 1 2.137-3.175c.9-.9 1.958-1.612 3.175-2.137A9.738 9.738 0 0 1 12 2c1.383 0 2.683.263 3.9.788a10.098 10.098 0 0 1 3.175 2.137c.9.9 1.613 1.958 2.137 3.175A9.738 9.738 0 0 1 22 12a9.738 9.738 0 0 1-.788 3.9 10.098 10.098 0 0 1-2.137 3.175c-.9.9-1.958 1.613-3.175 2.137A9.738 9.738 0 0 1 12 22z" fill="#5AA447"/>
</svg>`
const SVG_FAIL = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<path d="m12 13.4 2.9 2.9a.948.948 0 0 0 .7.275.948.948 0 0 0 .7-.275.948.948 0 0 0 .275-.7.948.948 0 0 0-.275-.7L13.4 12l2.9-2.9a.948.948 0 0 0 .275-.7.948.948 0 0 0-.275-.7.948.948 0 0 0-.7-.275.948.948 0 0 0-.7.275L12 10.6 9.1 7.7a.948.948 0 0 0-.7-.275.948.948 0 0 0-.7.275.948.948 0 0 0-.275.7c0 .283.092.517.275.7l2.9 2.9-2.9 2.9a.948.948 0 0 0-.275.7c0 .283.092.517.275.7a.948.948 0 0 0 .7.275.948.948 0 0 0 .7-.275l2.9-2.9zm0 8.6a9.738 9.738 0 0 1-3.9-.788 10.099 10.099 0 0 1-3.175-2.137c-.9-.9-1.612-1.958-2.137-3.175A9.738 9.738 0 0 1 2 12c0-1.383.263-2.683.788-3.9a10.099 10.099 0 0 1 2.137-3.175c.9-.9 1.958-1.612 3.175-2.137A9.738 9.738 0 0 1 12 2c1.383 0 2.683.263 3.9.788a10.098 10.098 0 0 1 3.175 2.137c.9.9 1.613 1.958 2.137 3.175A9.738 9.738 0 0 1 22 12a9.738 9.738 0 0 1-.788 3.9 10.098 10.098 0 0 1-2.137 3.175c-.9.9-1.958 1.613-3.175 2.137A9.738 9.738 0 0 1 12 22z" fill="#D82C0D"/>
</svg>`
const SVG_ANGLE = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<path d="M12 14.95c-.133 0-.258-.02-.374-.062a.877.877 0 0 1-.325-.213l-4.6-4.6a.948.948 0 0 1-.275-.7c0-.283.091-.516.275-.7a.948.948 0 0 1 .7-.275c.283 0 .516.092.7.275l3.9 3.9 3.9-3.9a.948.948 0 0 1 .7-.275c.283 0 .516.092.7.275a.948.948 0 0 1 .275.7.948.948 0 0 1-.275.7l-4.6 4.6c-.1.1-.209.171-.325.213a1.106 1.106 0 0 1-.375.062z" fill="#576F8A"/>
</svg>`
const SVG_CLOSE = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
</svg>
`

let i = 0;

function check_perf() {
    i++;
    console.log("performance number: ", i)
}

// fetch templates
async function _getTempaltes() {
    try {
        const res = await fetch(FETCH_TEMPLATES_API);
        const data = await res.json()
        return data.data
    } catch (error) {
        console.log(error)
        return []
    }
}

// fetch components
async function _getComponents() {
    try {
        const res = await fetch(FETCH_COMPONENTS_API);
        const data = await res.json()
        return data.data
    } catch (error) {
        console.log(error)
        return []
    }
}

odoo.define('grading_template.wysiwyg', function (require) {
    'use strict';

    var Wysiwyg = require('web_editor.wysiwyg');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    var GradingTemplateWysiwyg = Wysiwyg.extend({
        /**
         * @override
         */
        destroy() {
            this._super();
            document.getElementById(TEMPLATES_LIB_MODAL_ID).remove();
            this._loadCss(false)
        },
        /**
         * @override
         */
        async startEdition() {
            await this._super();

            this._loadCss();

            this._enableDraggableAllLibComponentsInEditor();

            const editor = this.$el[0];
            editor.ondrop = e => this._onDropHandler(e)
            editor.onclick = e => this._onClickHandler(e);
            editor.ondragstart = e => this._onDragStartHandler(e)

            this._renderTemplatesLib();
        },
        /**
         * Check mouse pointer đang gần top hay bottom của element
         * @param {MouseEvent} event
         * @param {DOMElement} element
         * @returns {Boolean} True nếu gần top
         */
        _isNearTop(event, element) {
            var rect = element.getBoundingClientRect();

            var distanceToTop = event.clientY - rect.top;
            var distanceToBottom = rect.bottom - event.clientY;

            return distanceToTop < distanceToBottom
        },
        _enableDraggableAllLibComponentsInEditor() {
            const libCompoennts = Array.from(this.$el[0].querySelectorAll(`.${LIB_COMPONENT_CLASS}`))
            libCompoennts.forEach(ele => {
                ele.setAttribute("draggable", "true")
            })
        },
        /**
         * Append hoặc remove link css của html custom field này
         * @param {Boolean} isLoad false là remove
         */
        _loadCss(isLoad = true) {
            if (!isLoad) {
                document.getElementById(STYLE_LINK_ID).remove();
                return
            }

            const link = document.createElement('link')
            link.id = STYLE_LINK_ID
            link.rel = 'stylesheet'
            link.href = CSS_PATH
            document.head.appendChild(link)
        },
        _renderTemplatesLib: async function () {
            const wysisyg = this;

            // create modal
            const modal = document.createElement("div");
            modal.id = TEMPLATES_LIB_MODAL_ID;
            modal.classList.add('is-show')
            modal.innerHTML = "Loading...."
            document.body.appendChild(modal)

            // fetch templates and components
            const templates = await _getTempaltes();
            const components = await _getComponents();

            // create templates lib
            const templatesContainer = document.createElement("div")
            templatesContainer.classList.add(TEMPLATES_LIB_CLASS)

            // templates title
            const templatesTitle = document.createElement("h5")
            templatesTitle.innerText = "Templates"
            templatesContainer.appendChild(templatesTitle)

            // template items
            const templatesUl = document.createElement("ul")
            templates.forEach(template => {
                const li = document.createElement("li")
                li.innerText = template.name
                li.classList.add('template-item')
                li.classList.add('lib-item')

                // if click, replace editor content with the template content
                li.onclick = function () {
                    this.setValue(template.content);
                    this._enableDraggableAllLibComponentsInEditor();
                }.bind(this)
                templatesUl.appendChild(li)
            })
            templatesContainer.appendChild(templatesUl)

            // create components lib
            const componentsContainer = document.createElement("div")
            componentsContainer.classList.add(TEMPLATES_LIB_CLASS)

            // components title
            const componentsTitle = document.createElement("h5")
            componentsTitle.innerText = "Components"
            componentsContainer.appendChild(componentsTitle)

            // component items
            const componentsUl = document.createElement("ul")
            components.forEach(component => {
                const li = document.createElement("li")
                li.innerText = component.name
                li.setAttribute('draggable', 'true');
                li.classList.add('component-item')
                li.classList.add('lib-item')
                li.ondragstart = function (e) {
                    e.dataTransfer.setData("component", JSON.stringify({
                        html: component.content,
                        uniqueId: undefined
                    }));
                }
                componentsUl.appendChild(li)
            })

            componentsContainer.appendChild(componentsUl)

            // remove loading
            modal.innerHTML = ""

            // toggle button
            const toggleBtn = document.createElement('button')
            toggleBtn.innerText = 'Hide library'
            toggleBtn.classList.add(BUTTON_CLASS)
            toggleBtn.onclick = function () {
                modal.classList.toggle("is-show")
                if (modal.classList.contains('is-show')) {
                    toggleBtn.innerText = 'Hide library'
                } else {
                    toggleBtn.innerText = 'Show library'
                }
            }

            // preview btn
            const previewBtn = document.createElement('button')
            previewBtn.innerText = 'Preview'
            previewBtn.classList.add(BUTTON_CLASS)
            previewBtn.onclick = function () {
                console.log('render preview')
                wysisyg._renderFeedbackPreview();
            }

            // finally
            modal.appendChild(toggleBtn)
            modal.appendChild(previewBtn)
            modal.appendChild(templatesContainer)
            modal.appendChild(componentsContainer)
        },
        _renderFeedbackPreview() {
            const backdrop = document.createElement('div')
            backdrop.id = 'preview_criterion_modal';
            backdrop.classList.add('disable_grading_template_html_field_css')


            const modal = document.createElement('div')
            modal.id = 'preview_criterion_container'
            backdrop.appendChild(modal)

            // close modal btn
            const btn = document.createElement('button')
            btn.id = 'close_preview_criterion_modal'
            btn.innerHTML = SVG_CLOSE
            btn.onclick = () => {
                this._closePreviewModal();
            }
            modal.appendChild(btn)

            const criterion = document.createElement('div')
            criterion.id = 'preview_criterion'

            // render header
            const criterionHeader = document.createElement('div')
            criterionHeader.classList.add('preview_criterion_header')
            const criterionName = document.querySelector('.criterion_name span').innerText;

            const criterionResult = this._getCriterionResult();
            let svg;

            if (criterionResult === 'not_graded') {
                // render error message if the reviewer has not graded this criterion
                const errorMsg = document.createElement('p')
                errorMsg.classList.add('preview_criterion_error_message')
                errorMsg.innerText = "You haven't grade this criterion."
                modal.appendChild(errorMsg)
                document.body.appendChild(backdrop)
                return
            } else if (criterionResult === 'passed') {
                svg = SVG_SUCCESS
            } else {
                svg = SVG_FAIL
            }

            criterionHeader.innerHTML = `<div>${svg}<strong>${criterionName}</strong></div>${SVG_ANGLE}`

            // render feedback content including:
            // - reviewer feedback
            // - criterion specifications
            const criterionBody = document.createElement('div')
            criterionBody.classList.add('preview_criterion_body')

            const reviewerFeedback = document.createElement('div')
            reviewerFeedback.classList.add('preview_criterion_feedback')
            if (criterionResult === 'passed') {
                reviewerFeedback.classList.add('passed')
            }
            reviewerFeedback.innerHTML = `<p class='reviewer_note'>Reviewer Note</p>${this.$el.html()}`;

            const criterionSpecifications = document.createElement('div')
            criterionSpecifications.innerHTML = document.querySelector('.criterion_specifications div').innerHTML;

            criterionBody.appendChild(reviewerFeedback)
            criterionBody.appendChild(criterionSpecifications)

            criterion.appendChild(criterionHeader)
            criterion.appendChild(criterionBody)
            modal.appendChild(criterion)
            document.body.appendChild(backdrop)
        },
        _generateUniqueId() {
            // need to change lib?
            return String(Date.now()) + String(Math.round(Math.random() * 100000))
        },
        _closePreviewModal() {
            document.getElementById('preview_criterion_modal').remove();
        },
        _getCriterionResult() {
            // result sẽ có double quotes ở 2 đầu, vd: "passed" thay vì passed, nên slice để bỏ double quotes đi
            return document.querySelector('.criterion_result select').value.slice(1, -1);
        },
        _getParentUntilLibComponent(ele) {
            let parent = ele;

            let limit = 50;
            let i = 0;
            while (parent && !parent.classList.contains(LIB_COMPONENT_CLASS) && i < limit) {
                parent = parent.parentElement;
                i++;
            }

            if (parent?.classList.contains(LIB_COMPONENT_CLASS)) {
                return parent
            }

            return undefined
        },
        /**
         * Handle drag lib component
         * @param {DragStartEvent} e
         */
        _onDragStartHandler(e) {
            check_perf();
            if (e.target.classList.contains(LIB_COMPONENT_CLASS)) {

                e.dataTransfer.setData("component", JSON.stringify({
                    html: e.target.innerHTML,
                    uniqueClass: this._getUniqueClassFromEle(e.target)
                }))
            }
        },
        /**
         * Handle drop lib component
         * @param {DropEvent} e
         */
        _onDropHandler(e) {
            check_perf()
            e.preventDefault();
            var hoveredElement = document.elementFromPoint(e.clientX, e.clientY);

            const gradingComponent = this._getParentUntilLibComponent(hoveredElement);

            const range = this._rangeFromCoord(e.clientX, e.clientY)

            var transferedData = e.dataTransfer.getData("component");
            var uniqueClassToDelete;
            var data;
            if (transferedData) {
                data = JSON.parse(transferedData).html;
                uniqueClassToDelete = JSON.parse(transferedData).uniqueClass;
            }

            const newEle = this._constructNewLibComponent(data);

            if (gradingComponent) {
                if (this._isNearTop(e, gradingComponent) || !gradingComponent.nextSibling) {

                    gradingComponent.parentNode.insertBefore(newEle, gradingComponent);
                } else {
                    gradingComponent.parentNode.insertBefore(newEle, gradingComponent.nextSibling);
                }
            } else {
                range.insertNode(newEle);
            }

            // nếu drag component có sẵn trong editor sang vị trí mới thì xóa ele vị trí cũ đi
            if (uniqueClassToDelete) {
                const willBeDeleted = this.$el[0].querySelector(`.${uniqueClassToDelete}`)
                willBeDeleted.parentElement.removeChild(willBeDeleted)
            }

            this.setValue(this.$el.html());
        },
        /**
         * Để handle click xóa lib component
         * @param {MouseClickEvent} e
         */
        _onClickHandler(e) {
            check_perf();
            if (e.target.classList.contains(LIB_COMPONENT_CLASS)) {
                const target = e.target;
                const rect = target.getBoundingClientRect();
                const mouseX = e.clientX;
                const mouseY = e.clientY;

                if (
                    mouseX >= rect.left &&
                    mouseX <= rect.right &&
                    mouseY >= rect.top &&
                    mouseY <= rect.bottom
                ) {
                    // do nothing
                } else {
                    e.target.remove()
                    const editorContent = this.$el.html();
                    this.setValue(editorContent);
                }
            }
        },
        /**
         * @this_is_not_used_I_just_leave_it_here_for_reference
         */
        _onTemplateClicked: (title) => {
            const section = `<section>${title}</section>`;
            const selection = window.getSelection();
            const range = selection.getRangeAt(0);
            const node = range.createContextualFragment(section);
            range.insertNode(node);
        },
        _constructNewLibComponent(html) {
            const newEle = document.createElement("div")
            newEle.classList.add(LIB_COMPONENT_CLASS);
            const uniqueClass = `${LIB_COMPONENT_CLASS}-${this._generateUniqueId()}`
            newEle.classList.add(uniqueClass);
            newEle.setAttribute("draggable", "true")
            newEle.innerHTML = html

            return newEle
        },
        _getUniqueClassFromEle(ele) {
            return Array.from(ele.classList).find(item => item.startsWith(`${LIB_COMPONENT_CLASS}-`))
        },
        _rangeFromCoord(x, y) {
            const closest = {
                offset: 0,
                xDistance: Infinity,
                yDistance: Infinity,
            };

            const {
                minOffset,
                maxOffset,
                element,
            } = (() => {
                const range = document.createRange();
                range.selectNodeContents(document.elementFromPoint(x, y));
                return {
                    element: range.startContainer,
                    minOffset: range.startOffset,
                    maxOffset: range.endOffset,
                };
            })();

            for (let i = minOffset; i <= maxOffset; i++) {
                const range = document.createRange();
                range.setStart(element, i);
                range.setEnd(element, i);
                const marker = document.createElement("span");
                marker.style.width = "0";
                marker.style.height = "0";
                marker.style.position = "absolute";
                marker.style.overflow = "hidden";
                range.insertNode(marker);
                const rect = marker.getBoundingClientRect();
                const distX = Math.abs(x - rect.left);
                const distY = Math.abs(y - rect.top);
                marker.remove();
                if (closest.yDistance > distY) {
                    closest.offset = i;
                    closest.xDistance = distX;
                    closest.yDistance = distY;
                } else if (closest.yDistance === distY) {
                    if (closest.xDistance > distX) {
                        closest.offset = i;
                        closest.xDistance = distX;
                        closest.yDistance = distY;
                    }
                }
            }

            const range = document.createRange();
            range.setStart(element, closest.offset);
            range.setEnd(element, closest.offset);
            return range;
        }
    });

    return GradingTemplateWysiwyg;
});
