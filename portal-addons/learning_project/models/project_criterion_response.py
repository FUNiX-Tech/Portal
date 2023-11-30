# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import config

logger = logging.getLogger(__name__)

template_categories = [
    ("pass_none", "Pass lần đầu"),
    ("pass_pass", "Pass lần 2, lần trước pass"),
    ("pass_fail", "Pass lần 2, lần trước fail"),
    ("did_not_pass", "Không pass"),
    ("incomplete", "Chưa hòan thành"),
]

# Tạo template trong list dưới
# Xác định default template cho từng category
# xác định tiêu chí thuộc category nào
# auto chọn template
# có thể đổi template
# kéo component khi cần


class ProjectCriterionResponse(models.Model):
    _name = "project_criterion_response"
    _description = "project_criterion_response"
    _rec_name = "criterion"

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    INCOMPLETE = ("incomplete", "Incomplete")
    DEFAULT_RESULT = NOT_GRADED[0]

    submission = fields.Many2one(
        "project_submission", required=True, readonly=True
    )
    criterion = fields.Many2one(
        "project_criterion", required=True, readonly=True
    )
    specifications = fields.Html(
        string="Specifications", related="criterion.specifications"
    )
    feed_back = fields.Html(string="Feedback")
    result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, INCOMPLETE],
        required=True,
        string="Result",
        default=DEFAULT_RESULT,
    )
    number = fields.Integer(related="criterion.number")
    submission_result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW],
        related="submission.result",
    )
    criteria_group = fields.Many2one(
        related="criterion.criteria_group", store=True
    )  # store=True để có thể sort

    previously_passed = fields.Boolean(
        string="Previously Passed", compute="_compute_previously_passed"
    )
    previously_feedback = fields.Html(
        string="Previously Feedback", compute="_compute_previously_feedback"
    )

    previous_result = fields.Char(
        string="Previous Result", compute="_compute_previous_result"
    )

    material = fields.One2many(
        "project_criterion_material", related="criterion.material"
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
                    submission.result
                    not in ["submission_canceled", "not_graded"]
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

            record.previously_passed = previously_response.result == "passed"

    @api.depends("submission")
    def _compute_previously_feedback(self):
        print(
            "compute feedbackkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
        )
        nearest_response = self._get_nearest_respone()

        for record in self:
            record.previously_feedback = (
                "" if nearest_response is None else nearest_response.feed_back
            )

    def _get_nearest_respone(self):
        for record in self:
            project = record.submission.project

            try:
                submissions = list(
                    filter(
                        lambda item: item.id != record.submission.id
                        and item.student.id == record.submission.student.id
                        and item.result != "submission_canceled",
                        project.submissions,
                    )
                )
                submissions.sort(key=lambda item: item.id)
                submission = submissions[-1]
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.id)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                print(submission.result)
                previous_criterion_response = list(
                    filter(
                        lambda criterion_resopnse: criterion_resopnse.criterion.id
                        == record.criterion.id,
                        submission.criteria_responses,
                    )
                )[0]
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)
                print("111111", previous_criterion_response.result)

                return previous_criterion_response
            except IndexError:
                return None

    @api.depends("submission")
    def _compute_previous_result(self):
        prev_response = self._get_nearest_respone()
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        for r in self:
            if prev_response is not None:
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                print("2222", prev_response.result)
                r.previous_result = prev_response.result
            else:
                r.previous_result = "none"
