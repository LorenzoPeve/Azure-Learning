from azure.storage.blob import ContainerClient, ContainerSasPermissions
from azure.storage.blob import generate_container_sas
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import requests
import time
import os

load_dotenv(override=True)

ACCT_NAME = 'nytimescovers'
ACCT_URL = 'https://nytimescovers.blob.core.windows.net'
CONTAINER_NAME = 'covers'

def get_authenticated_container_client() -> ContainerClient:
    """Returns an authenticated ContainerClient."""
    permission = ContainerSasPermissions(
        read=True, write=True, delete=True, list=True
    )

    sas = generate_container_sas(
        account_key=os.getenv('acct_key'),
        account_name=ACCT_NAME,
        container_name=CONTAINER_NAME,
        permission=permission,
        start=datetime.now() - timedelta(hours=1),
        expiry=datetime.now() + timedelta(hours=24),
    )

    return ContainerClient(
        account_url=f'https://{ACCT_NAME}.blob.core.windows.net',
        container_name=CONTAINER_NAME,
        credential=sas
    )


def get_cover_page(d: date) -> bytes:
    """
    Returns the front page of the NY Times as bytes.

    If the request fails or encounters an exception, it waits for an increasing
    amount of time before retrying.
    """
    url = (
        f'https://static01.nyt.com/images/'
        f'{d.year}/{str(d.month).zfill(2)}/{str(d.day).zfill(2)}/'
        f'nytfrontpage/scan.pdf'
    )

    c = 0
    while True:

        try:
            response = requests.get(url)
        except Exception:
            pass
        else:
            if response.status_code == 200:
                return response.content
        c += 1
        time.sleep(c*5)

def main():

    date_now = datetime.now().date()
    page = get_cover_page(date_now)
    container_client = get_authenticated_container_client()
    container_client.upload_blob(f"{date_now.strftime('%Y_%m_%d')}.pdf", page)


if __name__ == '__main__':
    main()