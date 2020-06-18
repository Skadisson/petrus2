from bin.service import Cache
from bin.service import Analyze


class Info:
    """Basic Information on Petrus"""

    @staticmethod
    def run():
        success = True
        cache = Cache.Cache()
        analyze = Analyze.Analyze()
        tickets = cache.load_cached_tickets()
        ticket_opened_calendar = analyze.ticket_opened_calendar(tickets)
        ticket_closed_calendar = analyze.ticket_closed_calendar(tickets)
        ticket_effort_calendar = analyze.ticket_effort_calendar(tickets)

        ticket_count = 0
        for ticket in tickets:
            ticket_count += 1

        items = [{
            'ticket_count': ticket_count,
            'ticket_opened_calendar': ticket_opened_calendar,
            'ticket_closed_calendar': ticket_closed_calendar,
            'ticket_effort_calendar': ticket_effort_calendar
        }]

        return items, success
