import os, click, pandas

from util.SchemaValidator import SchemaValidator
from util.AIRRRequests import AIRRRequests
from util.AIRRNormalizer import AIRRNormalizer

basedir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
schemas_path = os.path.join(basedir, 'schemas')

@click.command()
@click.option(
    "--input-url", "-i",
    required=True,
    help='URL of the API endpoint to query for AIRR-seq data.')
@click.option(
    "--output-dir", "-o",
    required=True,
    help="Directory for storing incoming data.")
@click.option(
    "--filter", "-f", "filter_airr",
    multiple=True,
    nargs=2,
    default=[],
    type=click.Tuple([str, str]),
    help="(Optional) Filter content according to AIRR compliant specified rules. May be called multiple times. Takes 2 arguments: [field to filter for] [value]")
@click.option(
    "--filter-disease", "-fd",
    multiple=True,
    nargs=2,
    default=[],
    type=str,
    help="(Optional) Filter content according to disease name")
@click.option(
    "--access-token", "-a",
    help="(Optional) Access Token used to access the endpoint in case of non-public data")
def main (input_url, output_dir, filter_airr, filter_disease, access_token=None):
    response = AIRRRequests.request_repertoires(input_url, filter_airr, access_token)

    if "Repertoire" in response:
        SchemaValidator.is_valid(response, os.path.join(schemas_path, "airr_repertoires.json"))

        df = AIRRNormalizer.normalize_repertoires(response["Repertoire"])
        df.to_csv(os.path.join(output_dir, "repertoires.csv"), sep="\t", index=False)

        # Gather ID of the repertoires collected through this request
        repetoire_ids = [r['repertoire_id'] for r in response["Repertoire"]]

        for repertoire in response["Repertoire"]:

            SchemaValidator.is_valid(response, os.path.join(schemas_path, "airr_rearrangements.json"))

            df = pandas.DataFrame(response["Rearrangements"])
            df.to_csv(os.path.join(output_dir, "sequence.csv"), sep="\t", index=False)

if __name__ == "__main__":
    main()