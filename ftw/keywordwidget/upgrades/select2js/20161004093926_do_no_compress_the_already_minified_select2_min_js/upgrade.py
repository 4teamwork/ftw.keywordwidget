from ftw.upgrade import UpgradeStep


class DoNoCompressTheAlreadyMinifiedSelect2MinJs(UpgradeStep):
    """Disable compression of the already minified "select2.min.js".
    """

    def __call__(self):
        self.install_upgrade_profile()
