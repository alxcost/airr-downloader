import os, sys, click, pandas, json

from util.SchemaValidator import SchemaValidator
from util.AIRRRequests import AIRRRequests
from util.AIRRNormalizer import AIRRNormalizer
from util.TempStorage import TempFile

basedir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
temp_path = os.path.join(basedir, 'temp')
schemas_path = os.path.join(basedir, 'schemas')

@click.command()
@click.option(
    "--input-url", "-i",
    required=True,
    help='URL of an AIRR compliant API endpoint to query for AIRR-seq data.')
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
    help="Filter content according to AIRR compliant specified rules. Takes 2 arguments: [field to filter for] [value]")
@click.option(
    "--filter-study", "-fs",
    multiple=True,
    nargs=1,
    default=[],
    type=str,
    help="Filter content according to a study ID.")
@click.option(
    "--filter-disease", "-fd",
    multiple=True,
    nargs=1,
    default=[],
    type=str,
    help="Filter content according to disease name.")
@click.option(
    "--filter-organism", "-fo",
    multiple=True,
    nargs=1,
    default=[],
    type=str,
    help="Filter content by organism.")
@click.option(
    "--filter-cell", "-fc",
    multiple=True,
    nargs=1,
    default=[],
    type=str,
    help="Filter content according to cell type.")
@click.option(
    "--access-token", "-a",
    help="Access Token used to access the endpoint in case of non-public data.")
def main(input_url, output_dir, filter_airr, filter_study, filter_disease, filter_organism, filter_cell, access_token=None):
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create temp directory
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    filter_airr += AIRRNormalizer.normalize_builtin_filters(filter_study, filter_disease, filter_organism, filter_cell)

    print ("Requesting available repertoires")
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

    print("Requesting rearrangements for {0} repertoire(s)".format(len(repertoire_ids)))
    response = AIRRRequests.stream_rearrangements_by_repertoire_ids(input_url, repertoire_ids)

    f = TempFile(temp_path)
    for raw_rsvp in response:
        f.get().write(raw_rsvp)
        f.get().flush()
        print("{0}            ".format(AIRRRequests.sizeof_fmt(f.get().tell())), end="\r" )

    print("Finished fetching {0} of rearrangements".format(AIRRRequests.sizeof_fmt(f.get().tell())))

    response = json.loads(f.read())

    if "Rearrangement" not in response:
        print("No rearrangements found for repertoires")
        sys.exit(1)

    try:
        SchemaValidator.is_valid(response, os.path.join(schemas_path, "airr_rearrangements.json"))
    except Exception as e:
        print("The \"/rearrangement\" response returned from the API is not AIRR compliant: ", e)
        sys.exit(1)

    df_rearrangements = pandas.DataFrame(response["Rearrangement"])
    for repertoire_id, df_rearrangement in df_rearrangements.groupby("repertoire_id"):
        rearragement_output_dir = os.path.join(output_dir, "rearragements_{0}.tsv".format(repertoire_id))
        df_rearrangement.to_csv(rearragement_output_dir, sep="\t", index=False)

        repertoire_row = df_repertoires.loc[df_repertoires['repertoire_id'] == repertoire_id, "filename"] = rearragement_output_dir

    df_repertoires.to_csv(os.path.join(output_dir, "metadata.csv"), sep="\t", index=False)

if __name__ == "__main__":
    main()