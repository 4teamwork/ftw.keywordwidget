from ftw.upgrade import UpgradeStep


class UpdateSelect2Location(UpgradeStep):
    """Update select2 location.
    """

    def __call__(self):
        self.install_upgrade_profile()
