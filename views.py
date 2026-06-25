import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from issues.models import CriticalIssue, Issue, LowPriorityIssue, Reporter
from issues.storage import read_json, write_json


REPORTERS_FILE = 'reporters.json'
ISSUES_FILE = 'issues.json'


def _error(message, status=400):
    return JsonResponse({'error': message}, status=status)


def _find_by_id(records, record_id):
    for record in records:
        if record['id'] == record_id:
            return record
    return None


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def reporters(request):
    if request.method == 'GET':
        reporters_list = read_json(REPORTERS_FILE)
        reporter_id = request.GET.get('id')
        if reporter_id is not None:
            record = _find_by_id(reporters_list, int(reporter_id))
            if record is None:
                return _error('Reporter not found', 404)
            return JsonResponse(record, status=200)
        return JsonResponse(reporters_list, safe=False, status=200)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return _error('Invalid JSON')

    reporter = Reporter(
        id=data['id'],
        name=data['name'],
        email=data['email'],
        team=data['team'],
    )

    try:
        reporter.validate()
    except ValueError as exc:
        return _error(str(exc))

    reporters_list = read_json(REPORTERS_FILE)
    if _find_by_id(reporters_list, reporter.id) is not None:
        return _error('id already exists')

    reporters_list.append(reporter.to_dict())
    write_json(REPORTERS_FILE, reporters_list)
    return JsonResponse(reporter.to_dict(), status=201)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def issues(request):
    if request.method == 'GET':
        issues_list = read_json(ISSUES_FILE)
        issue_id = request.GET.get('id')
        status_filter = request.GET.get('status')

        if issue_id is not None:
            record = _find_by_id(issues_list, int(issue_id))
            if record is None:
                return _error('Issue not found', 404)
            return JsonResponse(record, status=200)

        if status_filter is not None:
            filtered = [i for i in issues_list if i.get('status') == status_filter]
            return JsonResponse(filtered, safe=False, status=200)

        return JsonResponse(issues_list, safe=False, status=200)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return _error('Invalid JSON')

    priority = data['priority']
    if priority == 'critical':
        issue = CriticalIssue(
            data['id'], data['title'], data['description'],
            data['status'], priority, data['reporter_id'],
        )
    elif priority == 'low':
        issue = LowPriorityIssue(
            data['id'], data['title'], data['description'],
            data['status'], priority, data['reporter_id'],
        )
    else:
        issue = Issue(
            data['id'], data['title'], data['description'],
            data['status'], priority, data['reporter_id'],
        )

    try:
        issue.validate()
    except ValueError as exc:
        return _error(str(exc))

    issues_list = read_json(ISSUES_FILE)
    if _find_by_id(issues_list, issue.id) is not None:
        return _error('id already exists')

    response_data = issue.to_dict()
    response_data['message'] = issue.describe()
    issues_list.append(response_data)
    write_json(ISSUES_FILE, issues_list)
    return JsonResponse(response_data, status=201)
