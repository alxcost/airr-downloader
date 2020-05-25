import requests

from typing import List, Tuple

class AIRRRequests:
    """
    Class for handling requests to AIRR compliant APIs

    # Quirk #1
    # Some AIRR APIs deny requests if the request has no body, returning
    # a "Unable to parse JSON parameters:Syntax error" message. As such,
    # all requests send an empty object (if no query parameters were requested).
    # This provides that the body always exists, even if it's an empty JSON.
    """
    @staticmethod
    def request_repertoires(url: str, filter_airr: Tuple[Tuple[str, str]] = [], access_token: str = None):
        """
        :param url: URL corresponding to a AIRR compliant API
        :param filter_airr: list of filters to be applied to the request.
                        field filtering should follow the data formats defined
                        by the AIRR standards. More details:
                        https://docs.airr-community.org/en/latest/api/adc_api.html#request-parameters
        :param access_token: Option Access Token for protected APIs

        :return: Repertoire based schema on success
        """
        header = AIRRRequests._build_header(access_token)

        query = {}

        # Quirk #2
        # The filter behaves differently when filter one parameter and when
        # filtering multiple.
        # We need to check two conditions: if there's only one filter, or if
        # there's multiple. Reason being, some APIs do not support sending
        # a single condition in an array. If they did, we could just use the
        # second condition as len(filter_airr) > 0.
        # https://docs.airr-community.org/en/latest/api/adc_api.html#request-parameters
        if len(filter_airr) == 1:
            query = {
                "filters":{
                    "op":"contains",
                    "content": {
                        "field": filter_airr[0][0],
                        "value": filter_airr[0][1]
                    }
                }
            }

        elif len(filter_airr) > 1:
            query = {
                "filters":{
                    "op":"and",
                    "content": []
                }
            }

            for f in filter_airr:
                query["filters"]["content"].append({
                    "op":"contains",
                    "content": {
                        "field": f[0],
                        "value": f[1]
                    }
                })

        airr_request = requests.post(url, json=query, headers=header);
        airr_request.raise_for_status()
        return airr_request.json()

    @staticmethod
    def request_rearrangements_by_repertoire_ids(url: str, repertoire_ids: List[int], access_token: str = None):
        """
        :param url: URL corresponding to a AIRR compliant API
        :param repertoire_ids:
        :param access_token: Option Access Token for protected APIs

        :return: Repertoire based schema on success
        """

        header = AIRRRequests._build_header(access_token)

        query = {
            "filters":{
                "op":"=",
                "content": {
                    "field": "repertoire_id",
                    "value": id_repertoire
                }
            }
        }

        airr_request = requests.post(url, json=query, headers=header);
        airr_request.raise_for_status()
        return airr_request.json()

    @staticmethod
    def _build_header(access_token: str = None):
        header = {
            "Content-Type": "application/json",
        }

        if access_token:
            header["Authorization"] = "Bearer {0}".format(access_token)

        return header