from odoo import models, fields, api


class StudentOrganization(models.Model):
    _inherit = "student_organization"
    course_ids = fields.Many2many(
        comodel_name="course_management",
        relation="courses_enroll_organizations",
        column1="organization_ids",
        column2="course_ids",
        string="Courses Enrolled",
    )

    @api.model
    def create(self, vals):
        """
        override create method, in case of create organization have list course and student at the same time,
        Logic will be handle to make students and course link each other
        """
        org = super(StudentOrganization, self).create(vals)
        course_ids = org.course_ids.ids
        student_ids = org.student_ids.ids
        if course_ids != [] and student_ids != []:
            for course in org.course_ids:
                course.write(
                    {
                        "student_ids": [
                            (4, student_id) for student_id in student_ids
                        ]
                    }
                )
                course._compute_temp_organization_ids()
            for student in org.student_ids:
                student._compute_temp_organizations()
        return org

    def write(self, vals):
        old_courses = self.course_ids.ids
        new_courses = (
            vals.get("course_ids")[0][2]
            if "course_ids" in vals
            else self.course_ids.ids
        )
        old_students = self.student_ids.ids
        new_students = (
            vals.get("student_ids")[0][2]
            if "student_ids" in vals
            else self.student_ids.ids
        )
        result = super(StudentOrganization, self).write(vals)
        if old_courses != new_courses:
            self._onchange_course_ids(old_courses, new_courses)
        if old_students != new_students:
            self._onchange_student_ids(old_students, new_students)
        return result

    def _onchange_course_ids(self, old_values, new_values):
        """
        A function that is called when the `course_ids` field of the current record is changed.
        param old_values: A list of the previous values of the `course_ids` field.
        param new_values: A list of the new values of the `course_ids` field.
        """
        added_courses = list(set(new_values) - set(old_values))
        removed_courses = list(set(old_values) - set(new_values))
        if len(added_courses) != 0:
            for student in self.student_ids:
                student.write(
                    {
                        "course_ids": [
                            (4, course_id) for course_id in added_courses
                        ]
                    }
                )
            self.update_computed_organization(
                "course_management", added_courses
            )

        if len(removed_courses) != 0:
            for student in self.student_ids:
                student.write(
                    {
                        "course_ids": [
                            (3, course_id) for course_id in removed_courses
                        ]
                    }
                )
            self.update_computed_organization(
                "course_management", removed_courses
            )

    def _onchange_student_ids(self, old_values, new_values):
        added_students = list(set(new_values) - set(old_values))
        removed_students = list(set(old_values) - set(new_values))
        if len(added_students) != 0:
            for course in self.course_ids:
                course.write(
                    {
                        "student_ids": [
                            (4, student_id) for student_id in added_students
                        ]
                    }
                )
            self.update_computed_organization("portal.student", added_students)

        if len(removed_students) != 0:
            for course in self.course_ids:
                course.write(
                    {
                        "student_ids": [
                            (3, student_id) for student_id in removed_students
                        ]
                    }
                )
            self.update_computed_organization(
                "portal.student", removed_students
            )

    def update_computed_organization(self, model, lists):
        if model == "course_management":
            courses = self.env["course_management"].browse(lists)
            for course in courses:
                course._compute_temp_organization_ids()
        elif model == "portal.student":
            students = self.env["portal.student"].browse(lists)
            for student in students:
                student._compute_temp_organizations()
