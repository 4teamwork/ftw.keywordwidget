from ftw.upgrade import UpgradeStep


class UpdatePlone5Registry(UpgradeStep):
    """Update Plone5 registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
