import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('django.security.csp')

@csrf_exempt
def csp_report(request):
    """
    Endpoint to receive Content Security Policy (CSP) violation reports.
    """
    if request.method == 'POST':
        try:
            # Parse the JSON body
            # Browsers send this with Content-Type: application/csp-report
            if request.body:
                report_data = json.loads(request.body)
                csp_report_data = report_data.get('csp-report', {})

                # Log the formatted report
                logger.warning(
                    f"CSP Violation: "
                    f"Blocked URI: {csp_report_data.get('blocked-uri', 'N/A')} | "
                    f"Violated Directive: {csp_report_data.get('violated-directive', 'N/A')} | "
                    f"Document URI: {csp_report_data.get('document-uri', 'N/A')}"
                )
                
                # You can extend this to save to the database if needed
                
                return JsonResponse({'status': 'ok'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error processing CSP report: {str(e)}")
            return JsonResponse({'status': 'error'}, status=500)

    return JsonResponse({'status': 'ok'}, status=200) # Browsers might send OPTIONS/GET
