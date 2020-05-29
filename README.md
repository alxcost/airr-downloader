# AirrDownloader

Script collection for downloading and acquiring data from AIRR-compliant repository services, compatible with the iReceptor Plus repositories.

Allows the user to provide a URL to the service in order to output metadata and data into a CSV to a specified directory. The amount of data may be filtered by following the ADC schemas as well as through the default filters implemented in the script (i.e. filter by disease). All filters may be called multiple times to chain filtering conditions.

## Requirements

- Python 3
  - requests
  - clicks
  - pandas

The list of Python requirements can be found on `requirements.txt`. Requirements may be installed with a package manager such as PIP by doing: `pip install -r requirements.txt`.

## Usage

- Default usage

`python3 AirrDownloader.py -i <URL to AIRR data repository> -o <output directory>`

### Options

```
  -i, --input-url TEXT         URL of the API endpoint to query for AIRR-seq
                               data.  [required]
  -o, --output-dir TEXT        Directory for storing incoming data.
                               [required]
  -f, --filter <TEXT TEXT>...  Filter content according to AIRR compliant
                               specified rules. Takes 2 arguments: [field to
                               filter for] [value]
  -fs, --filter-study TEXT     Filter content according to a study ID.
  -fd, --filter-disease TEXT   Filter content according to disease name.
  -fo, --filter-organism TEXT  Filter content by organism.
  -fc, --filter-cell TEXT      Filter content according to cell type.
  -a, --access-token TEXT      Access Token used to access the endpoint in
                               case of non-public data.
```

### Usage examples

#### Built-in Filters

- Filtering by study

`python3 AirrDownloader.py -i <URL> -o <output directory> -fs PRJNA000000`

- Filtering by disease

`python3 AirrDownloader.py -i <URL> -o <output directory> -fd "multiple sclerosis"`

- Filtering by organism

`python3 AirrDownloader.py -i <URL> -o <output directory> -fo "homo sapiens"`

- Filtering by cell-type

`python3 AirrDownloader.py -i <URL> -o <output directory> -fc "IGH"`

#### Filtering by AIRR schemas
- Filter by Locus 

`python3 AirrDownloader.py -i <URL> -o <output directory> -f sample.pcr_target.pcr_target_locus TRB`

`python3 AirrDownloader.py -i <URL> -o <output directory> -f sample.pcr_target.pcr_target_locus IGH`

- Filter by Study ID

`python3 AirrDownloader.py -i <URL> -o <output directory> -f study.study_id PRJNA000000`
