odoo.define('learning_project.wysiwyg', function (require) {
    'use strict';

    var Wysiwyg = require('web_editor.wysiwyg');

    var core = require('web.core');
    var _lt = core._lt;

    // id để nhận biết feedback có additional reading chưa
    // = APPEND_ID ở material_field.js
    var APPEND_ID = '94713822-9650-11ee-b9d1-0242ac120002'

    var GradingProjectWysiwyg = Wysiwyg.extend({
        async startEdition() {
            await this._super();

            // this.$el[0].addEventListener('material', e => {
            //     this._handle_material(e.detail)
            // })

            this._inform_editor_started()

            this.ntav = this.onMeterialListenerHanlder.bind(this)

            document.addEventListener('material',this.ntav)

        },destroy() {
            this._super()
            console.log('DESTROY WYYYYY')
            document.removeEventListener('material',this.ntav)

        }, onMeterialListenerHanlder(e) {
            console.log('new material event')
            this._handle_material(e.detail)
        },
        _handle_material(event_data) {
            const action_type = event_data.action_type

            if (action_type === 'copy_url') {
                this._copy_material_url(event_data.url)
            }

            if (action_type === 'insert_label' || action_type === 'insert_sentence') {
                this._insert_material(event_data.action_type, event_data.label, event_data.url)
            }

            if (action_type === 'unappend') {
                this._unappend_material(event_data.material_id)
            }

            if (action_type === 'append') {
                this._append_material(event_data.append_data, event_data.material_id)
            }
        },
        _inform_editor_started() {
            Array.from(document.querySelectorAll('.material_item')).forEach(material_item => {
                material_item.dispatchEvent(new CustomEvent("editor_started"))
            })
        },
        _insert_material(insert_type, label, url) {
            let element = document.createElement('span')

            if (insert_type === 'insert_label') {
                element.innerHTML = `<a href="${url}">${label}</a>`
            } else {
                element.innerHTML = `${_lt('You can read more about')} ${label} ${_lt('at')} <a href="${url}">${_lt('HERE')}</a>.`
            }

            this.odooEditor.execCommand('insert', element);
        },
        _append_material(append_data, material_id) {
            this._unappend_material()
            this._select_end()
            const element = this._create_material_ele(append_data, material_id)
            this.odooEditor.execCommand('insert', element);
            this._inform_append(material_id)
        },
        _unappend_material() {
            const appended_ele = this._get_appended_ele()

            if (appended_ele) {
                appended_ele.remove()
                this.setValue(this.getValue())
            }

            this._inform_append("")
        },
        _copy_material_url(url) {
            navigator.clipboard.writeText(url)
        },
        _get_appended_ele() {
            return document.querySelector(`div[data-append-id="${APPEND_ID}"]`)
        },
        _create_material_ele(innerHTML, material_id) {
            const element = document.createElement('div')
            element.style.display = 'inline'
            element.dataset.appendId = APPEND_ID
            element.dataset.materialId = material_id
            element.innerHTML = innerHTML

            return element
        },
        _select_end() {
            const sel = this.odooEditor.document.getSelection();
            sel.removeAllRanges();
            const range = new Range()
            range.setStart(this.$el[0], this.$el[0].childElementCount)
            range.setEnd(this.$el[0], this.$el[0].childElementCount)
            sel.addRange(range);
        },
        _get_append_btns() {
            return Array.from(document.querySelectorAll(`button.append_material_btn`))
        },
        _inform_append(material_id = "") {
            this._get_append_btns().forEach(btn => {
                btn.dispatchEvent(new CustomEvent("append", { detail: { material_id } }))
            })
        },
    });

    return GradingProjectWysiwyg;
});
