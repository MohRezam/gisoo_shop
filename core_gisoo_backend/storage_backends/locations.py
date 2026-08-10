from core_gisoo_backend.storage_backends.media_storage import BASE_MEDIA_LOCATION

def avatar_path():
    return f"{BASE_MEDIA_LOCATION}/users/avatars"


def brand_logos_path():
    return f"{BASE_MEDIA_LOCATION}/brands/logos"


def hair_problem_image_path():
    return f"{BASE_MEDIA_LOCATION}/hair/problems"


def hair_type_image_path():
    return f"{BASE_MEDIA_LOCATION}/hair/types"


def product_image_path():
    return f"{BASE_MEDIA_LOCATION}/products/images"


def category_image_path():
    return f"{BASE_MEDIA_LOCATION}/products/categories"


def banner_image_path():
    return f"{BASE_MEDIA_LOCATION}/home/banner"

def home_about_image_path():
    return f"{BASE_MEDIA_LOCATION}/home/about-us"

def customer_satisfaction_path():
    return f"{BASE_MEDIA_LOCATION}/customer/satisfaction"