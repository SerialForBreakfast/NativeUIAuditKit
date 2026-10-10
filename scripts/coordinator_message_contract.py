"""Validate read acknowledgments without granting work authority."""
import re


def cursor_number(value):
    if not isinstance(value, str) or not re.fullmatch(r'0|[1-9][0-9]{0,18}', value):
        raise ValueError('Invalid cursor')
    number = int(value)
    if number > 9223372036854775807:
        raise ValueError('Invalid cursor')
    return number


def validate_ack(request):
    if not isinstance(request, dict) or set(request) != {'method', 'body'}:
        raise ValueError('Invalid acknowledgment')
    body = request['body']
    if request['method'] != 'message.ack' or not isinstance(body, dict) or set(body) != {'cursor'}:
        raise ValueError('Invalid acknowledgment')
    cursor_number(body['cursor'])


def validate_ack_result(request, result):
    validate_ack(request)
    if not isinstance(result, dict) or result.get('state') != 'read' or result.get('work_accepted') is not False:
        raise ValueError('Unconfirmed acknowledgment')
    if not isinstance(result.get('actor'), str) or not result['actor']:
        raise ValueError('Unconfirmed actor')
    if cursor_number(result.get('read_cursor')) < cursor_number(request['body']['cursor']):
        raise ValueError('Unconfirmed cursor')
    return result
