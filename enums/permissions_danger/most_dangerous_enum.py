from enum import Enum


class MostDangerousPermissionsEnum(Enum):
    BindServiceAdmin = "BIND_DEVICE_ADMIN"
    CallPhone = "CALL_PHONE"
    Camera = "CAMERA"
    CaptureAudioOutput = "CAPTURE_AUDIO_OUTPUT"
    DeletePackages = "DELETE_PACKAGES"
    InstallPackages = "INSTALL_PACKAGES"
    ModifyPhoneState = "MODIFY_PHONE_STATE"
    NFC = "NFC"
    RecordAudio = "RECORD_AUDIO"
    RequestInstallPackages = "REQUEST_INSTALL_PACKAGES"
    SendSMS = "SEND_SMS"
    SetAlwaysFinish = "SET_ALWAYS_FINISH"
    SetAnimationScale = "SET_ANIMATION_SCALE"
    SetDebugApps = "SET_DEBUG_APP"
    SetProcessLimit = "SET_PROCESS_LIMIT"
    SetTime = "SET_TIME"
    SetTimeZone = "SET_TIME_ZONE"
    SMSFinancialTransactions = "SMS_FINANCIAL_TRANSACTIONS"
    SystemAlertWindow = "SYSTEM_ALERT_WINDOW"
    WriteAPNSettings = "WRITE_APN_SETTINGS"
    WriteCallLog = "WRITE_CALL_LOG"
    WriteContacts = "WRITE_CONTACTS"
    WriteExternalStorage = "WRITE_EXTERNAL_STORAGE"
    WriteGServices = "WRITE_GSERVICES"
    WriteSecureSettings = "WRITE_SECURE_SETTINGS"
    WriteSettings = "WRITE_SETTINGS"
    WriteVoicemail = "WRITE_VOICEMAIL"
