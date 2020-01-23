from bin.service import Cache
from bin.service import Context
from bin.module import Estimate


class Search:
    """Context search"""

    def __init__(self, keywords):
        self.cache = Cache.Cache()
        self.context = Context.Context()
        self.keywords = keywords

    def run(self):
        tickets = self.cache.load_cached_tickets()
        commits = self.cache.load_cached_commits()
        formatted_keywords = self.format_keywords()
        if len(formatted_keywords) == 1:
            mod_estimate = Estimate.Estimate(formatted_keywords[0])
            items, success = mod_estimate.run()
        else:
            relevancy = self.context.calculate_relevancy_for_tickets(tickets, {'Keywords': formatted_keywords, 'Related': []})
            relevancy = self.context.add_relevancy_for_commits(commits, formatted_keywords, relevancy)
            items = [{
                'relevancy': relevancy,
                'keywords': formatted_keywords
            }]

        success = True
        return items, success

    def format_keywords(self):
        formatted_keyword_string = self.keywords.replace(" ", ",")
        formatted_keywords = formatted_keyword_string.split(",")
        formatted_keywords = list(filter(None, formatted_keywords))
        return formatted_keywords
