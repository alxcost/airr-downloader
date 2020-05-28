import os, sys, click, pandas, json

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
    help="Filter content according to AIRR compliant specified rules. May be called multiple times. Takes 2 arguments: [field to filter for] [value]")
@click.option(
    "--filter-disease", "-fd",
    multiple=True,
    nargs=1,
    default=[],
    type=str,
    help="Filter content according to disease name. May be called multiple times. Takes 1 argument: [value or disease name]")
@click.option(
    "--access-token", "-a",
    help="Access Token used to access the endpoint in case of non-public data")
def main (input_url, output_dir, filter_airr, filter_disease, access_token=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filter_airr += AIRRNormalizer.normalize_disease_filter(filter_disease)

    response = AIRRRequests.request_repertoires(input_url, filter_airr, access_token)

    if "Repertoire" not in response:
        print("Unable to acquire \"/repertoires\" from specified URL: {0}".format(input_url))
        sys.exit(1)

    try:
        SchemaValidator.is_valid(response, os.path.join(schemas_path, "airr_repertoires.json"))
    except Exception as e:
        print("The \"/repertoire\" response returned from the API is not AIRR compliant: ", e)
        sys.exit(1)

    df_repertoires = AIRRNormalizer.normalize_repertoires(response["Repertoire"])
    df_repertoires["filename"] = None

    # Gather ID of the repertoires collected through this request
    repertoire_ids = [r['repertoire_id'] for r in response["Repertoire"]]

    if not len(repertoire_ids):
        print("No repertoires found to specified query")
        sys.exit(1)

    response = AIRRRequests.stream_rearrangements_by_repertoire_ids(input_url, repertoire_ids)
    rsvp = ""

    for raw_rsvp in response:
        rsvp += raw_rsvp
        print("{0}            ".format(AIRRRequests.sizeof_fmt(len(rsvp))), end="\r" )

    print("Finished fetching {0} of rearrangements".format(AIRRRequests.sizeof_fmt(len(rsvp))))

    if rsvp:
        response = json.loads(rsvp)

    if "Rearrangement" not in response:
        print("No rearragements found for reportoires")
        sys.exit(1)

    rearrangements = {}

    try:
        SchemaValidator.is_valid(response, os.path.join(schemas_path, "airr_rearrangements.json"))
    except Exception as e:
        print("The \"/rearrangement\" response returned from the API is not AIRR compliant: ", e)
        sys.exit(1)

    df_rearrangements = pandas.DataFrame(response["Rearrangement"])
    for repertoire_id, df_rearrangement in df_rearrangements.groupby("repertoire_id"):
        rearragement_output_dir = os.path.join(output_dir, "rearragements_{0}.csv".format(repertoire_id))
        df_rearrangement.to_csv(rearragement_output_dir, sep="\t", index=False)

        repertoire_row = df_repertoires.loc[df_repertoires['repertoire_id'] == repertoire_id, "filename"] = rearragement_output_dir

    df_repertoires.to_csv(os.path.join(output_dir, "metadata.csv"), sep="\t", index=False)

if __name__ == "__main__":
    main()