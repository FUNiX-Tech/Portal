# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.addons.website.tools import text_from_html
from odoo.tools import config
import html
from odoo.addons.grading_template.common import (
    PASS_NONE,
    PASS_PASS,
    PASS_FAIL,
    DID_NOT_PASS as CAT_DID_NOT_PASS,
    INCOMPLETE as CAT_INCOMPLETE,
)
from ..common import (
    NOT_GRADED,
    PASSED,
    DID_NOT_PASS,
    UNABLE_TO_REVIEW,
    INCOMPLETE,
    CANCELED,
)

from .project_submission import GRADE_STATUS

logger = logging.getLogger(__name__)


class ProjectCriterionResponse(models.Model):
    _name = "project_criterion_response"
    _description = "project_criterion_response"
    _rec_name = "criterion"

    DEFAULT_RESULT = NOT_GRADED[0]

    submission = fields.Many2one(
        "project_submission",
        string="Submsision",
        required=True,
        readonly=True,
    )

    criterion = fields.Many2one(
        "project_criterion",
        string="Criterion",
        required=True,
        readonly=True,
    )

    specifications = fields.One2many(
        comodel_name="project_specification_response",
        inverse_name="criterion_response",
        string="Specifications",
    )

    feedback = fields.Html(
        string="General Feedback",
        compute="_compute_feedback",
        readonly=False,
        store=True,
        sanitize_attributes=False,
    )

    additional_reading = fields.Html(
        string="Additional Reading",
        sanitize_attributes=False,
        compute="_compute_additional_reading",
        readonly=False,
        store=True,
    )

    feedback_render = fields.Html(
        string="Feedback to display to student",
        compute="_compute_feedback_render",
        store=True,
    )

    number = fields.Integer(string="Number", related="criterion.number")

    submission_result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW],
        related="submission.result",
        string="Submission Result",
    )

    criteria_group = fields.Many2one(
        related="criterion.criteria_group", store=True, string="Criteria Group"
    )

    previously_passed = fields.Boolean(
        string="Previously Passed", compute="_compute_previously_passed"
    )

    previous_feedback = fields.Html(
        string="Previously Feedback", compute="_compute_previous_feedback"
    )

    previous_result = fields.Char(
        string="Previous Result", compute="_compute_previous_result"
    )

    material = fields.One2many(
        "project_criterion_material", related="criterion.material"
    )

    templates = fields.One2many(
        "grading_template", compute="_compute_templates"
    )

    result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, INCOMPLETE],
        string="Result",
        default=DEFAULT_RESULT,
        compute="_compute_result",
        readonly=False,
        store=True,
        required=True,
    )

    display_result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, INCOMPLETE],
        string="Display Result",
        compute="_compute_display_result",
    )

    computed_result = fields.Selection(
        [
            NOT_GRADED,
            PASSED,
            DID_NOT_PASS,
        ],
        string="Computed Result",
        default=DEFAULT_RESULT,
        compute="_compute_computed_result",
    )

    graded_all = fields.Boolean(
        string="Graded All Specifications", compute="_compute_graded_all"
    )

    is_abnormal_result = fields.Boolean(
        string="Is Abnormal Result",
        compute="_compute_is_abnormal_result",
        store=True,
    )

    step = fields.Integer(default=1, string="Step", required=True)

    grading_status = fields.Selection(
        GRADE_STATUS, related="submission.grading_status"
    )

    _sql_constraints = [
        (
            "unique_submission_criterion",
            "unique(submission, criterion)",
            "Duplicated criteria in a submission.",
        )
    ]

    @api.constrains("submission", "criterion")
    def _check_the_same_project(self):
        for record in self:
            if record.criterion.project.id != record.submission.project.id:
                raise ValidationError(
                    "Criterion and submission must belong to an project"
                )

    @api.depends("submission")
    def _compute_previously_passed(self):
        for record in self:
            project = record.submission.project

            submissions = project.submissions.sorted(key=lambda item: item.id)

            nearest_submission = None
            for submission in submissions:
                if (
                    submission.result not in [CANCELED[0], NOT_GRADED[0]]
                    and record.submission.id != submission.id
                ):
                    nearest_submission = submission
                    break

            if nearest_submission is None:
                record.previously_passed = False
                return

            try:
                previously_response = list(
                    filter(
                        lambda response: response.criterion.id
                        == record.criterion.id,
                        nearest_submission.criteria_responses,
                    )
                )[0]
            except IndexError as e:
                # Xảy ra khi project đã có submission nhưng có ai đó sửa thêm tiêu chí vào project
                if (
                    config.get("debug_mode") is True
                    and config.get("allow_to_add_criteria_after_submission")
                    is True
                ):
                    logger.warning(
                        "Bạn đang cho phép thêm tiêu chí cho learning project mặc dù project đã có submission, vì vậy 'previously_passed' sẽ luôn False"
                    )
                    record.previously_passed = False
                    return
                else:
                    raise e

            record.previously_passed = previously_response.result == PASSED[0]

    @api.depends("submission")
    def _compute_previous_feedback(self):
        nearest_response = self._get_nearest_respone()

        for record in self:
            record.previous_feedback = (
                "" if nearest_response is None else nearest_response.feedback
            )

    def _get_nearest_respone(self):
        for record in self:
            project = record.submission.project

            try:
                submissions = list(
                    filter(
                        lambda item: item.id != record.submission.id
                        and item.student.id == record.submission.student.id
                        and item.result != CANCELED[0],
                        project.submissions,
                    )
                )
                submissions.sort(key=lambda item: item.id)
                submission = submissions[-1]

                previous_criterion_response = list(
                    filter(
                        lambda criterion_resopnse: criterion_resopnse.criterion.id
                        == record.criterion.id,
                        submission.criteria_responses,
                    )
                )[0]

                return previous_criterion_response
            except IndexError:
                return None

    @api.depends("submission")
    def _compute_previous_result(self):
        prev_response = self._get_nearest_respone()

        for r in self:
            if prev_response is not None:
                r.previous_result = prev_response.result
            else:
                r.previous_result = "none"

    @api.model
    def create(self, values):
        criterion_response = super(ProjectCriterionResponse, self).create(
            values
        )

        for spec in criterion_response.criterion.specifications:
            self.env["project_specification_response"].sudo().create(
                {
                    "specification": spec.id,
                    "criterion_response": criterion_response.id,
                }
            )

        return criterion_response

    @api.depends("specifications.result")
    def _compute_result(self):
        for r in self:
            if r.step >= 2:
                return

            results = list(map(lambda spec: spec.result, r.specifications))

            if NOT_GRADED[0] in results:
                r.result = NOT_GRADED[0]

            elif INCOMPLETE[0] in results:
                r.result = INCOMPLETE[0]

            elif DID_NOT_PASS[0] in results:
                r.result = DID_NOT_PASS[0]

            else:
                r.result = PASSED[0]

    @api.depends("specifications.result")
    def _compute_computed_result(self):
        for r in self:
            computed_result = PASSED[0]
            for spec in r.specifications:
                if spec.result in [
                    INCOMPLETE[0],
                    DID_NOT_PASS[0],
                    NOT_GRADED[0],
                ]:
                    if spec.result == NOT_GRADED[0]:
                        r.computed_result = NOT_GRADED[0]
                        return
                    else:
                        computed_result = DID_NOT_PASS[0]

            r.computed_result = computed_result

    @api.depends("previous_result", "result")
    def _compute_templates(self):
        for r in self:
            result = r.result
            prev_result = r.previous_result
            template_category = ""

            if result == PASSED[0] and prev_result == PASSED[0]:
                template_category = PASS_PASS[0]

            if result == PASSED[0] and prev_result == "none":
                template_category = PASS_NONE[0]

            if result == PASSED[0] and prev_result in [
                INCOMPLETE[0],
                DID_NOT_PASS[0],
                NOT_GRADED[0],
            ]:  # not_graded = unable to review
                template_category = PASS_FAIL[0]

            if result == DID_NOT_PASS[0]:
                template_category = CAT_DID_NOT_PASS[0]

            if result == INCOMPLETE[0]:
                template_category = CAT_INCOMPLETE[0]

            templates = (
                self.env["grading_template"]
                .sudo()
                .search([("category.code", "=", template_category)])
            )

            r.templates = templates

    @api.depends("templates")
    def _compute_feedback(self):
        for r in self:
            if r.step >= 3:
                return

            if len(r.templates) > 0:
                r.feedback = r.templates[0].content
            else:
                r.feedback = ""

    def button_save(self):
        for r in self:
            if r.step == 1:
                self.write({})

        for r in self:
            return {
                "type": "ir.actions.client",
                "tag": "soft_reload",
            }

    def button_next(self):
        for r in self:
            if r.step == 1:
                # Đang chấm từng đặc tả
                # Click next để sang bước nhập nhận xét chung và additional reading
                # Nếu đặc tả did not pass > required feedback
                # Nếu đặc tả passed > optional feedback

                for spec in r.specifications:
                    if (
                        spec.result == DID_NOT_PASS[0]
                        and text_from_html(spec.feedback).strip() == ""
                    ):
                        raise UserError(
                            "You have to give feedback for did not pass specification."
                        )

                if r.graded_all is True:
                    r.step = 2
                    return True
                else:
                    raise UserError(
                        "You haven't graded all the specifications."
                    )

            if r.step == 2:
                # Đã gom từng đạc tả thành 1 feedback duy nhất
                # Click preview and save để sang bước preview
                if text_from_html(r.feedback).strip() == "":
                    raise UserError("Feedback cannot be empty.")

                if not r.result or r.result == NOT_GRADED[0]:
                    raise UserError(
                        "Result must be in passed, did not pass, incomplete."
                    )

                r.write(
                    {"feedback": r.feedback, "result": r.result, "step": 3}
                )

                return True

            if r.step == 3:
                # Đang preview
                # Click Finish để kết thúc
                r.step = 4
                return {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                }

            if r.step >= 4:
                # đã finish
                raise UserError(
                    "Internal Server Error: Criterion Grading Step cannot be larger than 4."
                )

    def button_back(self):
        for r in self:
            if r.step > 1:
                r.step -= 1
            return True

    @api.depends("specifications.result")
    def _compute_graded_all(self):
        for r in self:
            graded_all = True
            for spec in r.specifications:
                if spec.result not in [
                    PASSED[0],
                    DID_NOT_PASS[0],
                    INCOMPLETE[0],
                ]:
                    graded_all = False
                    break

            self.graded_all = graded_all

    @api.depends("result")
    def _compute_is_abnormal_result(self):
        for r in self:
            results = list(map(lambda spec: spec.result, r.specifications))

            computed_result = []

            if NOT_GRADED[0] in results:
                computed_result = [NOT_GRADED[0]]

            elif INCOMPLETE[0] in results:
                computed_result = [INCOMPLETE[0], DID_NOT_PASS[0]]

            elif DID_NOT_PASS[0] in results:
                computed_result = [DID_NOT_PASS[0]]

            else:
                computed_result = [PASSED[0]]

            self.is_abnormal_result = r.result not in computed_result

    def button_double_back(self):
        for r in self:
            r.step -= 2

    @api.depends("result", "step")
    def _compute_display_result(self):
        for r in self:
            if r.step < 4:
                r.display_result = NOT_GRADED[0]
            else:
                r.display_result = r.result

    def write(self, values):
        if (
            self.env.su
            or self.env.user.login == self.submission.mentor_id.email
        ):
            return super(ProjectCriterionResponse, self).write(values)
        else:
            raise UserError("You are not assigned to this submission.")

    @api.depends("step")
    def _compute_feedback_render(self):
        for r in self:
            if r.step >= 3:
                result = ""
                header = ""
                body = ""
                footer = ""

                header = f'<div class="odoo_criterion_general_response">{r.feedback}</div>'
                footer = f'<div class="odoo_criterion_additional_reading">{r.additional_reading}</div>'

                if r.result == INCOMPLETE[0]:
                    body += "<p>Một số điểm cần thay đổi để hoàn thành tiêu chí:</p>"
                    footer = "<hr/>" + footer

                if r.result == INCOMPLETE[0]:
                    body += '<ul class="odoo_criteria incomplete">'
                else:
                    body += '<ul class="odoo_criteria">'

                i = 1
                for spec in r.specifications:
                    if r.result == INCOMPLETE[0]:
                        ele_class = "odoo_criterion incomplete"
                        li = f'<li class="{ele_class}"><p class="odoo_spec_title"><strong>Đặc tả {i}: {spec.specification.title}</strong></p><div class="odoo_spec_content">{spec.specification.content}</div></li>'
                        body += li

                    else:
                        if text_from_html(spec.feedback).strip() != "":
                            ele_class = (
                                "odoo_criterion passed"
                                if spec.result == "passed"
                                else "odoo_criterion did_not_pass"
                            )
                            li = f'<li class="{ele_class}"><p class="odoo_spec_title"><strong>Đặc tả {i}: {spec.specification.title}</strong></p><div class="odoo_spec_content">{spec.specification.content}</div><hr /><div><p class="odoo_spec_response_title"><strong>Nhận xét:</strong></p><div class="odoo_spec_response_content">{spec.feedback}</div></div></li>'
                            body += li
                    i += 1

                body += "</ul>"

                result = header + body + footer

                r.feedback_render = html.unescape(result)

            else:
                r.feedback_render = ""

    @api.depends("result")
    def _compute_additional_reading(self):
        for r in self:
            default_additional_reading = ""
            for ad in r.criterion.material:
                if ad.auto_append is True:
                    if r.result == INCOMPLETE[0]:
                        default_additional_reading = f"<div><p><strong>Bạn có thể tham khảo thêm các tài liệu dưới đây để cải thiện bài</strong></p><div>{ad.append}</div></div>"
                    else:
                        default_additional_reading = f"<div><p><strong>Đọc thêm</strong></p><div>{ad.append}</div></div>"
                    break
            r.additional_reading = default_additional_reading
