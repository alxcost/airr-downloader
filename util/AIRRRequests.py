import requests

class AIRRRequests:
    """
    Class for handling requests to AIRR compliant APIs
    """
    @staticmethod
    def request(url, access_token=None):
        """
        :param url: URL corresponding to a AIRR compliant endpoint

        :return: airr_data
        """
        header = {}

        if access_token:
            header["Authorization"] = "Bearer {0}".format(access_token)

        airr_request = requests.get(url, header);
        airr_request.raise_for_status()
        return airr_request.json()