from bin.service import Environment
from bin.service import Map


class Context:
    """Context Calculator"""

    def __init__(self):
        self.environment = Environment.Environment()
        self.mapper = Map.Map()

    def calculate_relevancy_for_tickets(self, tickets, keywords):
        relevancy = []
        keyword_total = len(keywords)
        if keyword_total is not 0:
            for jira_id in tickets:
                relevancy = self.add_to_relevancy(tickets, jira_id, keywords, relevancy)
        sorted_relevancy = self.sort_relevancy(relevancy)
        return sorted_relevancy

    def add_to_relevancy(self, tickets, jira_id, keywords, relevancy):
        ticket_data = tickets[str(jira_id)]
        ticket_relevancy = self.calculate_ticket_relevancy(ticket_data, keywords, jira_id)
        if ticket_relevancy is not None and ticket_relevancy['percentage'] > 0:
            relevancy.append(ticket_relevancy)
        return relevancy

    def calculate_ticket_relevancy(self, ticket, keywords, jira_id):
        relevancy = None
        keyword_total = len(keywords)
        keyword_hits = []
        for keyword in ticket['Keywords']:
            if keyword in keywords:
                keyword_hits.append(keyword)
        hit_count = len(keyword_hits)
        if hit_count >= 2:
            percentage = hit_count / keyword_total * 100
            ticket_link = self.environment.get_endpoint_ticket_link().format(jira_id)
            if percentage > 0:
                relevancy = {
                    "jira_id": str(jira_id),
                    "percentage": percentage,
                    "hits": keyword_hits,
                    "link": ticket_link
                }
                if 'Title' in ticket:
                    relevancy['title'] = ticket['Title']

        return relevancy

    @staticmethod
    def sort_relevancy(relevancy):
        def get_key(item):
            return item['percentage']
        return sorted(relevancy, key=get_key, reverse=True)

    def filter_similar_tickets(self, relevancy, cached_tickets, jira_id):
        similar_tickets = []
        for rel_item in relevancy:
            rel_jira_id = str(rel_item['jira_id'])
            rel_percentage = rel_item['percentage']
            if rel_jira_id != jira_id and rel_jira_id in cached_tickets:
                similar_ticket = cached_tickets[rel_jira_id]
                normalized_similar_ticket = self.mapper.normalize_ticket(similar_ticket, rel_percentage)
                similar_tickets.append(normalized_similar_ticket)
        hits = len(similar_tickets)

        return similar_tickets, hits
