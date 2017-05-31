from plone.batching.batch import Batch
from Products.Five.browser import BrowserView
import json


class SearchSource(BrowserView):

    def __init__(self, context, request):
        super(SearchSource, self).__init__(context, request)
        self.widget = self.context

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setHeader('X-Theme-Disabled', 'True')

        query = self.request.get('q', None)
        page = int(self.request.get('page', 1))
        pagesize = int(self.request.get('pagesize', 20))

        if not query:
            return json.dumps({})

        self.widget.update()
        source = self.widget.choice_field.source(self.widget.context)

        batch = Batch.fromPagenumber(items=source.search(query),
                                     pagesize=pagesize,
                                     pagenumber=page)

        return json.dumps(
            {
                'results': map(self._term_to_dict, batch),
                'total_count': len(batch),
                'page': page,
                'pagination': {'more': (page * pagesize) < len(batch)}
            }
        )

    def _term_to_dict(self, term):
        return {'_resultId': term.token,
                'id': term.token,
                'text': term.title and term.title or term.token}
