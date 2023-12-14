{
    "name": "Student and Course Management",
    "version": "1.0",
    "summary": "Bridge module for Student and Course relationship",
    "description": """Bridge module to connect portal_student_management with course_management""",
    "depends": ["portal_student_management", "course_management"],
    "data": [
        "views/course_view.xml",
        "views/student_view.xml",
        "data/migrate_student_course_relation.xml",
    ],
    "installable": True,
    "application": False,
    # Automatically install this module when all dependencies are installed
    "auto_install": True,
}
