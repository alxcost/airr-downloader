import pandas

class AIRRNormalizer:
    @staticmethod
    def normalize_builtin_filters(filter_study, filter_disease, filter_organism, filter_cell):
        normalized_filters = []

        for fs in filter_study:
            normalized_filters.append(("study.study_id", fs))

        for fd in filter_disease:
            normalized_filters.append(("subject.diagnosis.disease_diagnosis.value", fd))

        for fo in filter_organism:
            normalized_filters.append(("subject.organism.value", fo))

        for fc in filter_cell:
            normalized_filters.append(("sample.pcr_target.pcr_target_locus", fc))

        return tuple(normalized_filters)

    @staticmethod
    def normalize_repertoires(repertoire_list):
        samples = pandas.json_normalize(repertoire_list, record_path="sample")

        data_processing = pandas.json_normalize(repertoire_list, record_path="data_processing")

        repertoires = []

        for idr, repertoire in enumerate(repertoire_list):
            for ids, sample in samples.iterrows():
                repertoire_list[idr].update(sample)
                repertoires.append(repertoire_list[idr])

        #repertoires = pandas.io.json.json_normalize(repertoires)
        repertoires = pandas.json_normalize(repertoire_list)

        return repertoires