import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.utils import timezone

def get_brevo_client():
    """
    Instantiate and return the Brevo EmailCampaignsApi instance
    configured with the API Key from settings.
    """
    api_key = getattr(settings, 'BREVO_API_KEY', '')
    if not api_key:
        raise ValueError("BREVO_API_KEY is not defined in Django settings or environment.")
    
    # Configure API key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    
    # Initialize client
    api_client = sib_api_v3_sdk.ApiClient(configuration)
    return sib_api_v3_sdk.EmailCampaignsApi(api_client)

def create_email_campaign(
    name,
    subject,
    html_content,
    list_ids,
    sender_name=None,
    sender_email=None,
    scheduled_at=None
):
    """
    Create an email campaign in Brevo.
    
    :param name: Name of the campaign (for internal reference)
    :param subject: Subject line of the email
    :param html_content: HTML body of the email campaign
    :param list_ids: List of list IDs (integers) to send the campaign to
    :param sender_name: Name of the sender (defaults to settings.BREVO_SENDER_NAME)
    :param sender_email: Email of the sender (defaults to settings.BREVO_SENDER_EMAIL)
    :param scheduled_at: A datetime object or formatted string. Defaults to 1 hour in the future.
    :return: API response dict or raises ApiException/ValueError
    """
    # 1. Initialize API client
    api_instance = get_brevo_client()
    
    # 2. Resolve sender
    sender_name = sender_name or getattr(settings, 'BREVO_SENDER_NAME', 'VitalBook')
    sender_email = sender_email or getattr(settings, 'BREVO_SENDER_EMAIL', 'noreply@vitalbook.in')
    
    # 3. Resolve list IDs
    if not isinstance(list_ids, list):
        if isinstance(list_ids, (int, str)):
            list_ids = [int(list_ids)]
        else:
            raise ValueError("list_ids must be a list of integers")
    
    # Ensure they are integers
    list_ids = [int(lid) for lid in list_ids]
    
    # 4. Resolve scheduling date/time
    # Brevo expects a UTC time string. Usually YYYY-MM-DDTHH:mm:ss.SSSZ or YYYY-MM-DD HH:mm:ss
    if scheduled_at is None:
        # Default to 1 hour in the future in UTC
        future_time = timezone.now() + datetime.timedelta(hours=1)
        scheduled_at_str = future_time.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(scheduled_at, (datetime.datetime, datetime.date)):
        # Make sure it's converted to UTC string format
        if hasattr(scheduled_at, 'astimezone'):
            scheduled_at = scheduled_at.astimezone(datetime.timezone.utc)
        scheduled_at_str = scheduled_at.strftime("%Y-%m-%d %H:%M:%S")
    else:
        scheduled_at_str = str(scheduled_at)

    # 5. Define the campaign settings
    email_campaigns = sib_api_v3_sdk.CreateEmailCampaign(
        name=name,
        subject=subject,
        sender={"name": sender_name, "email": sender_email},
        html_content=html_content,
        recipients={"listIds": list_ids},
        scheduled_at=scheduled_at_str
    )
    
    # 6. Make the call to the client
    try:
        api_response = api_instance.create_email_campaign(email_campaigns)
        return api_response
    except ApiException as e:
        print(f"Exception when calling EmailCampaignsApi->create_email_campaign: {e}")
        raise e
