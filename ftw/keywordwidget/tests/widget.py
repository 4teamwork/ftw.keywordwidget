from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
from lxml import etree


@widget
class AsyncKeywordWidget(PloneWidget):

    @staticmethod
    def match(node):
        if not node.tag == 'div' or 'field' not in node.classes:
            return False
        return bool(node.css('.keyword-widget[data-ajaxoptions*="url"]'))

    def fill(self, values):
        select = self.css('select').first
        multiple = select.attrib.get('multiple', None) == 'multiple'

        if isinstance(values, basestring):
            values = [values]

        if not multiple and len(values) > 1:
            raise ValueError('Expect only one item, since the field is '
                             'single valued')

        # Clear options
        for item in self.css('option'):
            item.node.getparent().remove(item.node)

        for value in values:
            option = etree.Element('option')
            option.attrib['value'] = value
            option.attrib['selected'] = 'selected'
            option.text = value
            select.append(option)
