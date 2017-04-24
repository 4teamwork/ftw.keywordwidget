from ftw.upgrade import UpgradeStep


class RegisterKeywordwidgetJs(UpgradeStep):
    """Register keywordwidget.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
