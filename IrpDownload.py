import os, click, pandas

from util.SchemaValidator import SchemaValidator
from util.AIRRRequests import AIRRRequests

basedir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
schemas_path = os.path.join(basedir, 'schemas')

supportedTypes = {
    "Rearragements": "airr_rearrangements.json"
}

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
    "--access-token", "-a",
    help="(Optional) Access Token used to access the endpoint in case of non-public data")
def main (input_url, output_dir, access_token=None):
    response = AIRRRequests.request(input_url)

    SchemaValidator.is_valid(response, os.path.join(schemas_path, "airr_rearrangements.json"))

    df = pandas.DataFrame(response['Rearrangements'])
    df.to_csv(os.path.join(output_dir, "sequence.tsv"), sep="\t")

if __name__ == "__main__":
    main()