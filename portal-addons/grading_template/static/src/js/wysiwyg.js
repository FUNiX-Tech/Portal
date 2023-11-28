const TEMPLATES_LIB_MODAL_ID = "templates-lib-modal";
const TEMPLATES_LIB_CLASS = 'templates-lib'
const CSS_PATH = 'grading_template/static/src/css/grading_template_html_field.css'
const LIB_COMPONENT_CLASS = 'lib-component'
const STYLE_LINK_ID = 'grading_template_html_field_style'
const FETCH_TEMPLATES_API = "/api/v1/grading_template/templates"
const FETCH_COMPONENTS_API = "/api/v1/grading_template/components"
const TOGGLE_BUTTON_ID = 'grading_template_toggle_btn'

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
            const btn = document.createElement('button')
            btn.innerText = 'Hide library'
            btn.id = TOGGLE_BUTTON_ID
            btn.onclick = function () {
                modal.classList.toggle("is-show")
                if (modal.classList.contains('is-show')) {
                    btn.innerText = 'Hide library'
                } else {
                    btn.innerText = 'Show library'
                }
            }

            // finally
            modal.appendChild(templatesContainer)
            modal.appendChild(componentsContainer)
            modal.appendChild(btn)
        },
        _generateUniqueId() {
            // need to change lib?
            return String(Date.now()) + String(Math.round(Math.random() * 100000))
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
