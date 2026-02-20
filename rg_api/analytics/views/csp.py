import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

try:
    import geoip2.database
    import geoip2.errors
    GEOIP_LIB = geoip2
except ImportError:
    GEOIP_LIB = None

from ..models import CSPReport
from rg_api.permissions import get_client_ip

logger = logging.getLogger('django.security.csp')


@csrf_exempt
def csp_report(request):
    """
    Endpoint to receive Content Security Policy (CSP) violation reports.
    """
    if request.method == 'POST':
        try:
            # Parse the JSON body
            if request.body:
                report_data = json.loads(request.body)
                csp_report_data = report_data.get('csp-report', {})

                # Log the formatted report
                logger.warning(
                    "CSP Violation: Blocked URI: %s | Violated Directive: %s | Document URI: %s",
                    csp_report_data.get('blocked-uri', 'N/A'),
                    csp_report_data.get('violated-directive', 'N/A'),
                    csp_report_data.get('document-uri', 'N/A')
                )

                # Save the report to the database (avoiding typical duplicates)
                ip_address = get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')

                # Resolve location
                city = None
                country = None
                latitude = None
                longitude = None

                if ip_address and GEOIP_LIB and hasattr(settings, 'GEOIP_PATH'):
                    try:
                        with geoip2.database.Reader(settings.GEOIP_PATH) as reader:
                            response = reader.city(ip_address)
                            city = response.city.name
                            country = response.country.name
                            latitude = response.location.latitude
                            longitude = response.location.longitude
                    except Exception as e:
                        # Log debug info but continue saving the report
                        logger.debug(f"Could not resolve location for IP {ip_address}: {e}")

                # We use get_or_create to filter out identical reports that happen in the same context
                CSPReport.objects.get_or_create(
                    document_uri=csp_report_data.get('document-uri'),
                    violated_directive=csp_report_data.get(
                        'violated-directive'),
                    blocked_uri=csp_report_data.get('blocked-uri'),
                    source_file=csp_report_data.get('source-file'),
                    line_number=csp_report_data.get('line-number'),
                    column_number=csp_report_data.get('column-number'),
                    ip_address=ip_address,
                    defaults={
                        'referrer': csp_report_data.get('referrer'),
                        'effective_directive': csp_report_data.get(
                            'effective-directive'),
                        'original_policy': csp_report_data.get('original-policy'),
                        'status_code': csp_report_data.get('status-code'),
                        'raw_report': report_data,
                        'user_agent': user_agent,
                        'city': city,
                        'country': country,
                        'latitude': latitude,
                        'longitude': longitude,
                    }
                )

                return JsonResponse({'status': 'ok'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except (ValueError, KeyError, TypeError) as e:
            logger.error("Error processing CSP report: %s", str(e))
            return JsonResponse({'status': 'error'}, status=400)

    # Browsers might send OPTIONS/GET
    return JsonResponse({'status': 'ok'}, status=200)
