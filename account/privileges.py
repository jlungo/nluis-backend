from enum import Enum

class PrivilegeEnum(Enum):
    # Administration
    IS_ADMIN = "is_admin"
    IS_STAFF = "is_staff"
    ADMIN_CREATE = "admin_create"   
    ADMIN_UPDATE = "admin_update"
    ADMIN_DELETE = "admin_delete"   
    ADMIN_VIEW = "admin_view"
    ADMIN_LIST_VIEW = "admin_list_view"
    
    # User Management
    USER_CREATE_ = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_VIEW = "user_view"
    USERS_list_VIEW_ = "users_list_view"
    UPLOAD_USERS = "users_upload"
    
    # Switch board management
    SWITCH_BOARD_USER_MANAGEMENT_VIEW = "switch_board_user_management_view"
    SWITCH_BOARD_LAND_USE_PLANNING_VIEW = "switch_board_land_use_planning_view"
    SWITCH_BOARD_CCRO_MANAGEMENT_VIEW = "switch_board_ccro_management_view"
    


    @classmethod
    def choices(cls):
        return [(tag.value, tag.name) for tag in cls]

    @classmethod
    def values(cls):
        return [tag.value for tag in cls]
