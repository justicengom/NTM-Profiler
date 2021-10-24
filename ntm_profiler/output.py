
import os
from pathogenprofiler import filecheck
import csv
import tbprofiler as tbp
import time

def collate_results(outfile,samples_file=None,directory=".",sep="\t"):
    if samples_file:
        samples = [x.rstrip() for x in open(samples_file).readlines()]
    else:
        samples = [x.replace(".species.txt","") for x in os.listdir(directory) if x[-len(".species.txt"):]==".species.txt"]

    rows = []
    for s in samples:
        tmp = []
        IN = csv.DictReader(open(filecheck(f"{directory}/{s}.species.txt")),delimiter="\t")
        for r in IN:
            tmp.append(r)
        combined_row = {"sample":s}
        for col in IN.fieldnames:
            combined_row[col] = ";".join([str(x[col]) for x in tmp])
        rows.append(combined_row)
            

    with open(outfile,"w") as O:
        writer = csv.DictWriter(O,fieldnames = list(rows[0]),delimiter=sep)
        writer.writeheader()
        writer.writerows(rows)
        
def write_speciation_results(results,outfile):
    with open(outfile,"w") as O:
        O.write("Sample\tSpecies\tCoverage\tCoverage_SD\n")
        for x in results["species"]:
            x["sample"] = results["sample_name"]
            O.write(f"%(sample)s\t%(species)s\t%(mean)s\t%(std)s\n" % x)





def load_text(text_strings):
        return r"""
NTM-Profiler report
=================

The following report has been generated by NTM-Profiler.

Summary
-------
ID: %(id)s
Date: %(date)s

Species report
-----------------
%(species_report)s

Resistance report
-----------------
%(dr_report)s

Resistance genes report
-----------------
%(dr_genes_report)s

Resistance variants report
-----------------
%(dr_var_report)s

Other variants report
---------------------
%(other_var_report)s

Coverage report
---------------------
%(coverage_report)s

Missing positions report
---------------------
%(missing_report)s

Analysis pipeline specifications
--------------------------------
Pipeline version: %(version)s
Species Database version: %(species_db_version)s
Resistance Database version: %(resistance_db_version)s

%(pipeline)s
""" % text_strings


def load_species_text(text_strings):
        return r"""
NTM-Profiler report
=================

The following report has been generated by NTM-Profiler.

Summary
-------
ID: %(id)s
Date: %(date)s

Species report
-----------------
%(species_report)s

Analysis pipeline specifications
--------------------------------
Pipeline version: %(version)s
Species Database version: %(species_db_version)s

%(pipeline)s
""" % text_strings


def write_text(json_results,conf,outfile,columns = None,reporting_af = 0.0):
    if "resistance_genes" not in json_results:
        return write_species_text(json_results,conf,outfile)
    json_results = tbp.get_summary(json_results,conf,columns = columns,reporting_af=reporting_af)
    json_results["drug_table"] = [[y for y in json_results["drug_table"] if y["Drug"].upper()==d.upper()][0] for d in ["macrolides","amikacin"]]
    for var in json_results["dr_variants"]:
        var["drug"] = ", ".join([d["drug"] for d in var["drugs"]])
    text_strings = {}
    text_strings["id"] = json_results["id"]
    text_strings["date"] = time.ctime()
    text_strings["species_report"] = tbp.dict_list2text(json_results["species"],["species","mean"],{"species":"Species","mean":"Mean kmer coverage"})
    text_strings["dr_report"] = tbp.dict_list2text(json_results["drug_table"],["Drug","Genotypic Resistance","Mutations"]+columns if columns else [])
    text_strings["dr_genes_report"] = tbp.dict_list2text(json_results["resistance_genes"],["locus_tag","gene","type","drugs.drug"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction","drugs.drug":"Drug"})
    text_strings["dr_var_report"] = tbp.dict_list2text(json_results["dr_variants"],["genome_pos","locus_tag","gene","change","type","freq","drugs.drug"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction","drugs.drug":"Drug"})
    text_strings["other_var_report"] = tbp.dict_list2text(json_results["other_variants"],["genome_pos","locus_tag","gene","change","type","freq"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction"})
    text_strings["coverage_report"] = tbp.dict_list2text(json_results["qc"]["gene_coverage"], ["gene","locus_tag","cutoff","fraction"]) if "gene_coverage" in json_results["qc"] else "NA"
    text_strings["missing_report"] = tbp.dict_list2text(json_results["qc"]["missing_positions"],["gene","locus_tag","position","position_type","drug_resistance_position"]) if "gene_coverage" in json_results["qc"] else "NA"
    text_strings["pipeline"] = tbp.dict_list2text(json_results["pipeline_software"],["Analysis","Program"])
    text_strings["version"] = json_results["software_version"]
    tmp = json_results["species_db_version"]
    text_strings["species_db_version"] = "%(name)s_%(commit)s_%(Author)s_%(Date)s" % tmp
    tmp = json_results["resistance_db_version"]
    text_strings["resistance_db_version"] = "%(name)s_%(commit)s_%(Author)s_%(Date)s" % tmp
    o = open(outfile,"w")
    o.write(load_text(text_strings))
    o.close()


def write_species_text(json_results,conf,outfile):
    text_strings = {}
    text_strings["id"] = json_results["id"]
    text_strings["date"] = time.ctime()
    text_strings["species_report"] = tbp.dict_list2text(json_results["species"],["species","mean"],{"species":"Species","mean":"Mean kmer coverage"})
    text_strings["pipeline"] = tbp.dict_list2text(json_results["pipeline_software"],["Analysis","Program"])
    text_strings["version"] = json_results["software_version"]
    tmp = json_results["species_db_version"]
    text_strings["species_db_version"] = "%(name)s_%(commit)s_%(Author)s_%(Date)s" % tmp
    o = open(outfile,"w")
    o.write(load_species_text(text_strings))
    o.close()
