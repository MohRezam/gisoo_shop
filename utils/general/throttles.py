from rest_framework.throttling import UserRateThrottle


class ThrottleScopeNames:
    """
    List of all throttle scopes
    """

    ADD_FAVORITE = "add_favorite"
    GET_FAVORITE = "get_favorite"
    PREDICTION = "prediction"
    OTP = "otp"


class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"


class BurstRateThrottle(UserRateThrottle):
    scope = "burst"


class AddFavoriteRateThrottle(UserRateThrottle):
    """
    Use this scope for all add favorite scopes
    """

    scope = ThrottleScopeNames.ADD_FAVORITE


class GetFavoriteRateThrottle(UserRateThrottle):
    """
    Use this scope for all add favorite scopes
    """

    scope = ThrottleScopeNames.GET_FAVORITE


class PredictionThrottle(UserRateThrottle):
    """
    Use this scope for all add favorite scopes
    """

    scope = ThrottleScopeNames.PREDICTION


class OTPThrottle(UserRateThrottle):
    """
    Use this scope for all add favorite scopes
    """

    scope = ThrottleScopeNames.OTP
