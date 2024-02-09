from core.weexceptions import FatalException
from core import messages
from core import config
import string
import utils
import urllib.request, urllib.error, urllib.parse
import os
import secrets

agents_list_path = 'utils/_http/user-agents.txt'

def load_all_agents():
    """Loads all agents from a file.
    Parameters:
        - None
    Returns:
        - list: A list of all agents.
    Processing Logic:
        - Opens file and reads all lines.
        - Splits lines by newline character.
        - Returns list of agents."""
    

    try:

        with open(
            os.path.join(config.weevely_path,
            agents_list_path)
            ) as agents_file:
            return agents_file.read().split('\n')

    except Exception as e:
        raise FatalException(
            messages.generic.error_loading_file_s_s %
            (agents_list_path, str(e)))


def add_random_url_param(url):
    """Adds a random parameter to a given URL.
    Parameters:
        - url (str): The URL to add the random parameter to.
    Returns:
        - str: The updated URL with the added random parameter.
    Processing Logic:
        - Generates a random string for the parameter name.
        - Generates a random string for the parameter value.
        - Checks if the URL already has a query string.
        - Appends the random parameter to the URL.
    Example:
        add_random_url_param('https://www.example.com')
        # Output: 'https://www.example.com?jQpD=6Z9w6Qb9eE'"""
    

    random_param = '%s=%s' % (
        utils.strings.randstr(
            n = 4,
            fixed = False,
            charset = string.ascii_letters
        ),
        utils.strings.randstr(
            n = 10,
            fixed = False
        )
    )

    if '?' not in url:
        url += '?%s' % random_param
    else:
        url += '&%s' % random_param

    return url

def request(url, headers = []):
    """Function to make a request to a given URL with optional headers.
    Parameters:
        - url (str): The URL to make the request to.
        - headers (list): Optional list of headers to include in the request.
    Returns:
        - bytes: The response content from the request.
    Processing Logic:
        - If no 'User-Agent' header is provided, a random one will be chosen from a list of available user agents.
        - The request is made using the urllib.request.build_opener() function.
        - The headers are added to the opener using the addheaders attribute.
        - The response content is returned by calling the read() method on the opener's open() function.
    Example:
        request('https://www.google.com')
        # Returns the HTML content of the Google homepage."""
    
    
    if not next((x for x in headers if x[0] == 'User-Agent'), False):
        headers = [ ('User-Agent', secrets.SystemRandom().choice(load_all_agents())) ]

    opener = urllib.request.build_opener()
    opener.addheaders = headers
    return opener.open(url).read()
