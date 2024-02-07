import struct
import xml.etree.ElementTree as ET
import binascii
from androguard.misc import AnalyzeAPK
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes import dvm
from utils.all_permissions import AllAppPermissions
import numpy as np


class AllIntents:
    pass


class AnalyzeApks:
    def __init__(self):
        self.package_file_path = None
        self.all_activities = []
        self.all_services = []
        self.all_receivers = []
        self.all_providers = []
        self.all_permissions = []
        self.all_apk_signatures = []
        self.all_action_names = []
        self.app_permissions = AllAppPermissions()
        self.app_intents = AllIntents()

    def initialize_variables(self, package_file_path):
        self.package_file_path = package_file_path
        self.all_activities = []
        self.all_services = []
        self.all_receivers = []
        self.all_providers = []
        self.all_permissions = []
        self.all_apk_signatures = []
        self.all_action_names = []
        self.app_permissions = AllAppPermissions()
        self.app_intents = AllIntents()

    def extract_apk_info(self):
        self._extract_manifest_info(self.package_file_path)
        self._extract_signature_info(self.package_file_path)

    def format_data(self):
        all_packages_serialized_array = []
        for i in range(len(self.all_permissions)):
            # For Every App
            package_serialized_array = []
            for app_permission in self.app_permissions.all_permission_names:
                if app_permission in self.all_permissions[i]:
                    package_serialized_array.append(1)
                else:
                    package_serialized_array.append(0)

            for app_intent in self.app_intents.all_intents:
                if app_intent['package_name'] in self.all_intents[i]:
                    package_serialized_array.append(1)
                else:
                    package_serialized_array.append(0)

            all_packages_serialized_array.append(package_serialized_array)

        self.all_train_data = np.array(all_packages_serialized_array)
        self.all_train_data_classes = np.array(self.all_training_classes)
        self.all_train_data_classes = self.all_train_data_classes.astype(int)

    def _extract_manifest_info(self, file):
        try:
            a, d, dx = AnalyzeAPK(file)
            manifest_xml = a.get_android_manifest_axml().get_buff()

            root = ET.fromstring(manifest_xml)

            activities = root.findall(".//activity")
            all_activities = []
            for activity in activities:
                # Extract the android:name attribute from each activity
                activity_name = activity.get("{http://schemas.android.com/apk/res/android}name")

                if activity_name:
                    all_activities.append(activity_name)

            services = root.findall(".//service")
            all_services = []
            for service in services:
                # Extract the android:name attribute from each activity
                service_name = service.get("{http://schemas.android.com/apk/res/android}name")

                if service_name:
                    all_services.append(service_name)

            receivers = root.findall(".//receiver")
            all_receivers = []
            for receiver in receivers:
                receiver_name = receiver.get("{http://schemas.android.com/apk/res/android}name")
                if receiver_name:
                    all_receivers.append(receiver_name)

            providers = root.findall(".//provider")
            all_providers = []
            for provider in providers:
                provider_name = provider.get("{http://schemas.android.com/apk/res/android}name")
                if provider_name:
                    all_providers.append(provider_name)

            permissions = root.findall(".//uses-permission")
            all_permissions = []
            for permission in permissions:
                permission_name = permission.get("{http://schemas.android.com/apk/res/android}name")
                if permission_name:
                    all_permissions.append(permission_name)

            intent_filters = root.findall(".//intent-filter")
            action_names = []
            for intent_filter in intent_filters:
                actions = intent_filter.findall(".//action")
                categories = intent_filter.findall(".//category")
                for action in actions:
                    action_names.append(action.get("{http://schemas.android.com/apk/res/android}name"))

                for category in categories:
                    action_names.append(category.get("{http://schemas.android.com/apk/res/android}name"))

            self.all_activities.append(all_activities)
            self.all_services.append(all_services)
            self.all_receivers.append(all_receivers)
            self.all_providers.append(all_providers)
            self.all_permissions.append(all_permissions)
            self.all_action_names.append(action_names)
        except dvm.InvalidInstruction as e:
            return
        except struct.error as e:
            return

    def _extract_signature_info(self, file):
        a = APK(file)
        signature_binary = a.get_signature()
        rsa_signature_hex = binascii.hexlify(signature_binary).decode('utf-8')
        self.all_apk_signatures.append(rsa_signature_hex)
