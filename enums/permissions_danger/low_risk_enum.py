from enum import Enum


class LowRiskPermissionsEnum(Enum):
    AcceptHandover = "ACCEPT_HANDOVER"
    BindConditionProviderService = "BIND_CONDITION_PROVIDER_SERVICE"
    RequestCompanionRunInBackground = "REQUEST_COMPANION_RUN_IN_BACKGROUND"
    RequestCompanionUseDataInBackground = "REQUEST_COMPANION_USE_DATA_IN_BACKGROUND"
    RequestDeletePackages = "REQUEST_DELETE_PACKAGES"
    RequestIgnoreBatteryOptimizations = "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
    RequestPasswordComplexity = "REQUEST_PASSWORD_COMPLEXITY"
    Vibrate = "VIBRATE"
