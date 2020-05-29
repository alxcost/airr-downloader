import math, requests

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
        :param access_token: Optional Access Token for protected APIs

        :return: Repertoire based schema on success
        """
        header = AIRRRequests._build_header(access_token)

        query = {}

        # Quirk #2
        # The filter behaves differently when filtering for one parameter and
        # when filtering for multiple parameters.
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

        airr_request = requests.post(url + "/repertoire", json=query, headers=header);
        airr_request.raise_for_status()
        return airr_request.json()

    @staticmethod
    def request_rearrangements_by_repertoire_ids(url: str, repertoire_ids: List[int], access_token: str = None):
        """
        :param url: URL corresponding to a AIRR compliant API
        :param repertoire_ids: List of repertoire ids to query for
        :param access_token: Optional Access Token for protected APIs

        :return: Rearrangement based schema on success
        """
        if not repertoire_ids or not len(repertoire_ids):
            return False

        header = AIRRRequests._build_header(access_token)
        query = AIRRRequests._filter_by_repertoire

        airr_request = requests.post(url + "/rearrangement", json=query, headers=header);
        airr_request.raise_for_status()
        return airr_request.json()

    @staticmethod
    def stream_rearrangements_by_repertoire_ids(url: str, repertoire_ids: List[int], access_token: str = None):
        """
        :param url: URL corresponding to a AIRR compliant API
        :param repertoire_ids: List of repertoire ids to query for
        :param access_token: Optional Access Token for protected APIs

        :return: Response chunk of a Rearrangement based schema, Total length of expected response
        """
        if not repertoire_ids or not len(repertoire_ids):
            return False

        header = AIRRRequests._build_header(access_token)
        query = AIRRRequests._filter_by_repertoires(repertoire_ids)

        airr_request = requests.post(url + "/rearrangement", json=query, headers=header, stream=True);
        airr_request.raise_for_status()

        if airr_request.encoding is None:
            airr_request.encoding = 'utf-8'

        for chunk in airr_request.iter_content(chunk_size=1024*1024):
            if chunk:
                yield chunk

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        if not num:
            return "NaN"

        magnitude = int(math.floor(math.log(num, 1024)))
        val = num / math.pow(1024, magnitude)
        if magnitude > 7:
            return '{:.1f}{}{}'.format(val, 'Yi', suffix)
        return '{:3.1f}{}{}'.format(val, ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi'][magnitude], suffix)

    @staticmethod
    def _filter_by_repertoires(repertoire_ids: List[int]):
        return {
            "filters":{
                "op": "in",
                "content": {
                    "field": "repertoire_id",
                    "value": repertoire_ids
                }
            }
        }

    @staticmethod
    def _build_header(access_token: str = None):
        header = {
            "Content-Type": "application/json",
        }

        if access_token:
            header["Authorization"] = "Bearer {0}".format(access_token)

        return header
