def get_profile_key(user_id):
    return f"general.user_profile_{user_id}"


def get_home_services_key():
    return "general.home_services"


def get_user_configs_key(user_id):
    return f"general.user_configs_{user_id}"


def get_user_information_key(user_id: str):
    return f"users.get_user_{user_id}"


def get_dashboard_key(access: str, page: str):
    return f"general.dashboard_{page}_{access}"


GENERAL_CONFIGS_PATTERN = "general.user_configs_*"
