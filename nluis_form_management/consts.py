from django.db import models


class FieldType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    RADIO = "radio", "Radio Button"
    CHECKBOX = "checkbox", "Check Box"
    SELECT = "select", "DropDown"
    DATE = "date", "Date"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone Number"
    IMAGE = "image", "Image"
    FILE = "file", "File"
    TEXTAREA = "textarea", "Text Area"
    MEMBERS = "members", "Members"
    zoning = "zoning", "Zoning"


class WorkFlowCategoryType(models.IntegerChoices):
    REGISTRATION = 1, "registration"
    ASSESSMENT = 2, "assessment"
    APPROVAL = 3, "approval"
    MONITORING = 4, "monitoring"
    REPORTING = 5, "reporting"
    WORKFLOW = 6, "workflow"
    
