#!/usr/bin/env python
"""
Standalone script to create a Brevo Email Campaign.
Run with:
  python create_campaign.py --name "My Campaign" --subject "My Subject" --lists 2,7
"""
import os
import sys
import argparse
import datetime
from django.utils import timezone

# Add current directory to path and setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Error setting up Django environment: {e}")
    sys.exit(1)

from appointment.brevo_campaign import create_email_campaign
from sib_api_v3_sdk.rest import ApiException

def main():
    parser = argparse.ArgumentParser(description="Create a Brevo Email Campaign.")
    parser.add_argument(
        "--name", 
        type=str, 
        default="Campaign sent via the API", 
        help="Internal campaign name reference."
    )
    parser.add_argument(
        "--subject", 
        type=str, 
        default="My subject", 
        help="Email subject line."
    )
    parser.add_argument(
        "--sender-name", 
        type=str, 
        default=None, 
        help="Sender name (defaults to settings.BREVO_SENDER_NAME)."
    )
    parser.add_argument(
        "--sender-email", 
        type=str, 
        default=None, 
        help="Sender email (defaults to settings.BREVO_SENDER_EMAIL)."
    )
    parser.add_argument(
        "--html", 
        type=str, 
        default="Congratulations! You successfully sent this example campaign via the Brevo API.", 
        help="HTML content of the email."
    )
    parser.add_argument(
        "--lists", 
        type=str, 
        default="2,7", 
        help="Comma-separated list of Brevo list IDs (e.g., '2,7')."
    )
    parser.add_argument(
        "--hours-delay", 
        type=float, 
        default=1.0, 
        help="Hours from now to schedule the campaign (can be decimal, e.g. 0.5 for 30 minutes)."
    )

    args = parser.parse_args()

    # Parse lists
    try:
        list_ids = [int(x.strip()) for x in args.lists.split(",") if x.strip()]
    except ValueError:
        print("Error: --lists must be a comma-separated list of integers (e.g., '2,7').")
        sys.exit(1)

    if not list_ids:
        print("Error: At least one list ID must be specified.")
        sys.exit(1)

    # Calculate scheduled time
    # Delay must be positive to ensure it is in the future
    if args.hours_delay < 0:
        print("Error: --hours-delay must be positive.")
        sys.exit(1)

    scheduled_at = timezone.now() + datetime.timedelta(hours=args.hours_delay)
    scheduled_str = scheduled_at.strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 60)
    print("Brevo Email Campaign Creator")
    print("=" * 60)
    print(f"Campaign Name : {args.name}")
    print(f"Subject       : {args.subject}")
    print(f"Recipients    : Lists {list_ids}")
    print(f"Scheduled At  : {scheduled_str} UTC (in {args.hours_delay} hour(s))")
    print("-" * 60)
    print("Creating campaign in Brevo...")

    try:
        api_response = create_email_campaign(
            name=args.name,
            subject=args.subject,
            html_content=args.html,
            list_ids=list_ids,
            sender_name=args.sender_name,
            sender_email=args.sender_email,
            scheduled_at=scheduled_at
        )
        print("\n[OK] Campaign created successfully!")
        from pprint import pprint
        pprint(api_response)
    except ApiException as e:
        print(f"\n[ERROR] Exception when calling EmailCampaignsApi->create_email_campaign: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
