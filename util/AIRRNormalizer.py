import pandas

class AIRRNormalizer:
    @staticmethod
    def normalize_disease_filter(filter_disease):
        normalized_diseases = []
        for fd in filter_disease:
            normalized_diseases.append(("subject.diagnosis.disease_diagnosis.value", fd))

        return normalized_diseases

    @staticmethod
    def normalize_repertoires(repertoire_list):
        samples = pandas.io.json.json_normalize(repertoire_list, record_path="sample")

        data_processing = pandas.io.json.json_normalize(repertoire_list, record_path="data_processing")

        repertoires = []

        for idr, repertoire in enumerate(repertoire_list):
            for ids, sample in samples.iterrows():
                repertoire_list[idr].update(sample)
                repertoires.append(repertoire_list[idr])

        repertoires = pandas.io.json.json_normalize(repertoires)

        return repertoires