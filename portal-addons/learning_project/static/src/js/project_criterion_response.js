function onclickSummarizeBtn() {
    document.querySelector('.preview_and_save_btn').classList.toggle('d-none')
    document.querySelector('.back_btn').classList.toggle('d-none')
    document.querySelector('.summarize_btn').classList.toggle('d-none')
    document.getElementById('form_group_preliminary').classList.toggle('d-none')
    document.getElementById('form_group_final').classList.toggle('d-none')
    document.querySelector('button[name=button_save_step_1]').classList.toggle('d-none')


}

function onclickBackBtn() {
    document.querySelector('.preview_and_save_btn').classList.toggle('d-none')
    document.querySelector('.summarize_btn').classList.toggle('d-none')
    document.querySelector('.back_btn').classList.toggle('d-none')
    document.getElementById('form_group_preliminary').classList.toggle('d-none')
    document.getElementById('form_group_final').classList.toggle('d-none')
    document.querySelector('button[name=button_save_step_1]').classList.toggle('d-none')
}

function onClickTemplateItem(event) {
    $('button', event.target.nextSibling).click()
}
