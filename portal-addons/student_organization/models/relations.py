from odoo import models, fields, api


# Add Student Organization into student table
class StudentOrganization_Student(models.Model):
    _inherit = "portal.student"
    student_organization_student_ids = fields.Many2many(
        "student_organization",
        "student_organization_student_rel",
        "student_id",
        "student_organization_id",
        string="Student Organization",
    )
    temp_student_orgs = fields.Many2many(
        "student_organization",
        computed="_compute_temp_organizations",
        string="Temporary Student Organizations",
    )

    @api.depends("student_organization_student_ids")
    def _compute_temp_organizations(self):
        self.temp_student_orgs = self.student_organization_student_ids

    @api.onchange("student_organization_student_ids")
    def _onchange_organization_ids(self):
        """
        This function is an onchange handler for the field "student_organization_student_ids".
        It is triggered when the value of "student_organization_student_ids" is changed.
        Side Effects:
            - Updates the "course_ids" field of the current record with the course IDs of the added organizations.
            - Deletes the course IDs of the removed organizations from the "course_ids" field of the current record.
        """
        old_values = self.temp_student_orgs
        new_values = self.student_organization_student_ids
        added_orgs = list(set(new_values) - set(old_values))
        removed_orgs = list(set(old_values) - set(new_values))
        if len(added_orgs) != 0:
            for org in added_orgs:
                self.write(
                    {
                        "course_ids": [
                            (4, course_id) for course_id in org.course_ids.ids
                        ]
                    }
                )
        if len(removed_orgs) != 0:
            for org in removed_orgs:
                self.write(
                    {
                        "course_ids": [
                            (3, course_id) for course_id in org.course_ids.ids
                        ]
                    }
                )
        self._compute_temp_organizations()



# Add student  into Student Organization table
class Student_Organization_Student(models.Model):
    _inherit = "student_organization"
    student_ids = fields.Many2many(
        "portal.student",
        "student_organization_student_rel",
        "student_organization_id",
        "student_id",
        string="Student List",
    )
