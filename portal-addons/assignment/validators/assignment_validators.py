import re
import logging
import json
from odoo.http import request
from ..utils.utils import json_response

logger = logging.getLogger(__name__)

# student_id:
#   - has student
#   - student has enroll the course
# submission_id


def check_has_student():
    """
    Make sure this function runs after student_id has validated
    """
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            
            request_data = json.loads(request.httprequest.data)

            student_id = request_data.get("student_id")

            try:

                student = request.env['portal_student_management.portal.student'].sudo().search([('id', '=', student_id)])[0]
                self.student = student
                return origin_function(self, *args, **kwargs)
            
            except IndexError:

                logger.info(f"[INFO]: Not found student with id {student_id}")

                return json_response(400, f"Not found student with id {student_id}")
            
            except Exception as e: 

                logger.error(str(e))

                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator

def check_has_assignment():
    """
    Make sure this function runs after assignment_id has validated
    """
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            
            request_data = json.loads(request.httprequest.data)

            assignment_id = request_data.get("assignment_id")

            try:

                assignment = request.env['assignment'].sudo().search([('id', '=', assignment_id)])[0]
                self.assignment = assignment
                return origin_function(self, *args, **kwargs)
            
            except IndexError:

                logger.info(f"[INFO]: Not found assignment with id {assignment_id}")

                return json_response(400, f"Not found assignment with id {assignment_id}")
            
            except Exception as e: 

                logger.error(str(e))

                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator

def check_student_has_enrolled_course():
    """
    Make sure this function runs after check_has_student and check_has_assignment
    """
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            
            course_id =  self.assignment.course.id
            student_id = self.student.id
            try:
                course = (
                    request.env["course_management.course_management"]
                    .sudo()
                    .search([("id", "=", course_id), ("student_ids", "in", [student_id])])
                )[0]
                return origin_function(*args, **kwargs)
            except IndexError: 
                return json_response(400, f"Student with id {student_id} has not enrolled the course with id {course_id}")
            except Exception as e:
                return json_response(500, "Internal Server Error")

        return wrapper

    return decorator