from datetime import datetime

from sqlite_utils import increment_and_get


def check_query_limit(ip_address: str) -> bool:
    """orchestartor for query limit check"""
    day = datetime.now().strftime("%Y-%m-%d")
    query_count = increment_and_get(identifier=ip_address, day=day)
    return query_count > 5
