# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
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

    specifications_description = fields.Html(
        "Specifications Description", related="criterion.sumarized_content"
    )

    feedback_lead = fields.Html(
        string="Feedback Opening",
        compute="_compute_feedback_lead",
        readonly=False,
        store=True,
    )

    feedback_body = fields.Html(
        string="Feedback Body",
        compute="_compute_feedback_body",
        readonly=False,
        store=True,
    )

    feedback = fields.Html(
        string="Feedback Total",
        compute="_compute_feedback",
        readonly=False,
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
    )  # store=True để có thể sort

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

    is_final_step = fields.Boolean(string="Is Final Step", default=False)

    graded_all = fields.Boolean(
        string="Graded All Specifications", compute="_compute_graded_all"
    )

    is_abnormal_result = fields.Boolean(
        string="Is Abnormal Result", compute="_compute_is_abnormal_result"
    )

    step = fields.Integer(default=1, string="Step", required=True)

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

    @api.depends("specifications.result", "is_final_step")
    def _compute_result(self):
        for r in self:
            if r.is_final_step:
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

    @api.depends("result", "templates")
    def _compute_feedback_lead(self):
        for r in self:
            if len(r.templates) > 0:
                r.feedback_lead = r.templates[0].content
            else:
                r.feedback_lead = ""

    @api.depends("feedback_lead", "feedback_body")
    def _compute_feedback(self):
        for r in self:
            r.feedback = r.feedback_lead + r.feedback_body

    @api.depends("result", "is_final_step")
    def _compute_feedback_body(self):
        for r in self:
            if r.is_final_step:
                return

            result = "<ul>"

            for spec in r.specifications:
                if text_from_html(spec.feedback).strip() != "":
                    result += f"<li>{spec.feedback}</li>"

            result += "</ul>"

            r.feedback_body = html.unescape(result)

    def button_save(self):
        for r in self:
            if r.step == 1:
                self.write({})

        for r in self:
            return {
                "type": "ir.actions.act_window",
                "res_model": "project_submission",
                "domain": [],
                "view_mode": "form",
                "res_id": r.submission.id,
                "target": "current",
                "reload": True,
            }

    def button_finish_grading(self):
        self.ensure_one()
        self.write(
            {
                "feedback_lead": self.feedback_lead,
                "feedback_body": self.feedback_body,
                "result": self.result,
                "step": 4,
            }
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "project_submission",
            "domain": [],
            "view_mode": "form",
            "res_id": self.submission.id,
        }

    def button_next(self):
        for r in self:
            if r.graded_all is True:
                r.step += 1
            else:
                raise Exception("You haven't graded all the specifications.")

    def button_back(self):
        for r in self:
            r.step -= 1

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

            computed_result = ""

            if NOT_GRADED[0] in results:
                computed_result = NOT_GRADED[0]

            elif INCOMPLETE[0] in results:
                computed_result = INCOMPLETE[0]

            elif DID_NOT_PASS[0] in results:
                computed_result = DID_NOT_PASS[0]

            else:
                computed_result = PASSED[0]

            self.is_abnormal_result = computed_result != r.result

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
