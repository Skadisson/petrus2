from bin.service import ServiceDeskAPI
from bin.service import Map
from bin.service import Cache
from bin.service import Context
from bin.service import SciKitLearn
from bin.service import Analyze


class Estimate:
    """Estimator"""

    def __init__(self, jira_key):
        self.jira_key = jira_key
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()
        self.mapper = Map.Map()
        self.cache = Cache.Cache()
        self.context = Context.Context()
        self.sci_kit = SciKitLearn.SciKitLearn()
        self.analyze = Analyze.Analyze()

    def retrieve_ticket(self):
        ticket_data = self.sd_api.request_ticket_data(self.jira_key)
        mapped_ticket = self.mapper.get_mapped_ticket(ticket_data)
        mapped_ticket = self.mapper.format_related_tickets(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_status(mapped_ticket)
        mapped_ticket = self.mapper.format_status_history(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_worklog(mapped_ticket)
        mapped_ticket, worklog_persons = self.mapper.format_worklog(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_sla(mapped_ticket)
        mapped_ticket = self.mapper.format_sla(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_comments(mapped_ticket)
        mapped_ticket, comment_persons = self.mapper.format_comments(mapped_ticket)
        mapped_ticket = self.mapper.format_text(mapped_ticket)
        mapped_ticket = self.mapper.format_reporter(mapped_ticket)
        mapped_ticket = self.mapper.add_persons(mapped_ticket, (worklog_persons + comment_persons))
        return mapped_ticket

    def format_tickets(self, mapped_ticket):
        cached_tickets = self.cache.load_cached_tickets()
        relevancy = self.context.calculate_relevancy_for_tickets(cached_tickets, mapped_ticket)
        normalized_ticket = self.mapper.normalize_ticket(mapped_ticket)
        similar_tickets, hits = self.context.filter_similar_tickets(
            relevancy,
            cached_tickets,
            mapped_ticket['ID']
        )
        return normalized_ticket, similar_tickets, hits

    def run(self):
        mapped_ticket = None
        success = False
        estimation = None
        hits = None
        normalized_ticket = None
        ticket_id = None
        days_to_go = None

        try:
            if self.jira_key is not None:
                mapped_ticket = self.retrieve_ticket()
                ticket_id = mapped_ticket['ID']
                jira_id = str(mapped_ticket['ID'])
                self.cache.store_jira_key_and_id(self.jira_key, jira_id)
                success = self.cache.store_ticket(jira_id, mapped_ticket)
                if success:
                    normalized_ticket, similar_tickets, hits = self.format_tickets(mapped_ticket)
                    if hits == 0:
                        estimation = 900
                    else:
                        estimation = self.sci_kit.estimate(
                            normalized_ticket,
                            similar_tickets,
                            'Time_Spent',
                            ['Relevancy', 'Key', 'Priority', 'State_Changes', 'Type', 'Organization']
                        )
                    success = self.sd_api.update_ticket_times(jira_id, estimation, mapped_ticket)
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)

        if estimation is not None:
            estimation = float(estimation)

        if normalized_ticket is not None and ticket_id is not None and mapped_ticket is not None:
            normalized_ticket['Diff'] = 0.0
            tickets = self.analyze.load_tickets_for_days(30)
            diff_normalized_tickets = []
            normalized_tickets = self.mapper.normalize_tickets(tickets)
            for diff_normalized_ticket in normalized_tickets:
                if diff_normalized_ticket['Created'] > 0 and diff_normalized_ticket['Closed'] > 0:
                    diff_normalized_ticket['Diff'] = diff_normalized_ticket['Closed'] - diff_normalized_ticket['Created']
                    if diff_normalized_ticket['Diff'] > 0:
                        diff_normalized_tickets.append(diff_normalized_ticket)
            diff_estimation = self.sci_kit.estimate(
                normalized_ticket,
                diff_normalized_tickets,
                'Diff',
                ['Priority', 'Organization']
            )
            if diff_estimation > 0:
                days_to_go = int(round(diff_estimation / 60 / 60 / 24))
                if days_to_go > 14:
                    days_to_go = 14
                """else:
                    self.sd_api.post_ticket_comment(mapped_ticket['ID'], mapped_ticket['Priority'], days_to_go)"""

        ticket_score = self.analyze.rank_ticket(mapped_ticket)
        todays_score = self.cache.add_to_todays_score(self.jira_key, ticket_score)
        highest_day, highest_score = self.cache.get_high_score()
        score = {
            'ticket': str(ticket_score),
            'today': str(todays_score),
            'highest_score': str(highest_score),
            'highest_day': str(highest_day)
        }
        if '_id' in mapped_ticket:
            del(mapped_ticket['_id'])
        items = [{
            'ticket': mapped_ticket,
            'estimation': estimation,
            'days_to_go': days_to_go,
            'hits': hits,
            'normal_ticket': normalized_ticket,
            'score': score
        }]
        return items, success
