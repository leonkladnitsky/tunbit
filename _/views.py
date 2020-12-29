# HarBit Isurance coverage (General, Life, Health) view and result page parser.

from _.utils import *

logger = getLogger(__name__)


def home_view(request):
    """
    Minimal GUI for testing views
    :param request: request
    """
    page = request.GET.get('page') or settings.GUI_START_PAGE
    return render(request, 'index.html', {'page': page})


def control_view(request):
    """
    Collect data from Life Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'control'})

    # take from request
    req_body = request.body.decode()
    # req = json.loads(req_body)
    logger.debug(f'Received content: {req_body}')

    response = {'data': None, 'msg': '', }

    return JsonResponse(response)
