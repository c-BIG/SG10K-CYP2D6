#!/usr/bin/env nextflow

nextflow.enable.dsl=2
version = "0.2"   // nf workflow version

/*
----------------------------------------------------------------------
FUNCTIONS
----------------------------------------------------------------------
*/

def help_message(String version) {
    println(
        """
        ==============================================
        call_haplotypes  ~  version ${version}
        ==============================================

        Mandatory arguments:
        --cram_list  Path to file with list of input crams (one file per line). Note: cram index must be available as <cram>.crai.
        --reference  Path to genome reference. Note: reference index must be available as <fasta>.fai or <fa>.fai.
        --genome     Genome build. One of: 19, 37, 38.

        Additional arguments:
        --help
        --version
        """.stripIndent()
    )
}

def version_message(String version) {
    println("call_haplotypes  ~  version ${version}")
}

def complete_message(Map params, nextflow.script.WorkflowMetadata workflow, String version){
    println(
        """
        ==============================================
        EXECUTION SUMMARY
        ==============================================
        Workflow launched : ${workflow.scriptName} ${version}
        Command line      : ${workflow.commandLine}
        Output directory  : ${workflow.launchDir}
        Completed at      : ${workflow.complete}
        Duration          : ${workflow.duration}
        Success           : ${workflow.success}
        Exit status       : ${workflow.exitStatus}
        """.stripIndent()
    )
}

def error_message(nextflow.script.WorkflowMetadata workflow){
    println ""
    println "Workflow execution stopped with the following message:"
    println "   " + workflow.errorMessage

}

def help_or_version(Map params, String version){
    if (params.help) {
        help_message(version)
        System.exit(0)
    }
    if (params.version) {
        version_message(version)
        System.exit(0)
    }
}

def default_params(){
    def params = [:]
    params.help = false
    params.version = false
    params.cram_list = false
    params.reference = false
    params.genome = false
    return params
}

def check_params(Map params, nextflow.script.WorkflowMetadata workflow) {
    // merge defaults with user params
    final_params = default_params() + params

    // print help or version messages if requested
    help_or_version(final_params, version)

    // param checks
    check_mandatory_parameter(final_params, "cram_list")
    check_mandatory_parameter(final_params, "reference")
    check_mandatory_parameter(final_params, "genome")

    // additional pre-sets
    final_params.publish_dir = workflow.launchDir + "/outputs"

    // TODO
    // cram_basename = final_params.cram_list.take(final_params.cram.lastIndexOf('.'))
    // final_params.cram_pattern = cram_basename + "{.cram,.cram.crai}"

    ref_basename = final_params.reference.take(final_params.reference.lastIndexOf('.'))
    ref_extension = final_params.reference.substring(final_params.reference.lastIndexOf("."))
    switch (ref_extension) {
        case ".fasta": pattern = "{.fasta,.fasta.fai}"; break;
        case ".fa": pattern = "{.fa,.fa.fai}"; break;
        default:
            println("ERROR: Unrecognised reference suffix")
            System.exit(1)
    }
    final_params.reference_pattern = ref_basename + pattern

    return final_params
}

def check_mandatory_parameter(Map params, String parameter_name){
    if ( !params[parameter_name] ){
        println "ERROR: Missing mandatory argument; specify '--help' for usage instructions"
        System.exit(1)
    } else {
        return params[parameter_name]
    }
}

/*
----------------------------------------------------------------------
PROCESSES
---------------------------------------------------------------------
*/

process CYRIUS {
    tag "${sample_id}"
    container = "cyrius:1.1.1"
    publishDir "${final_params.publish_dir}/cyrius", mode: "copy"

    input:
    tuple val(sample_id), file(cram)
    tuple val(reference_id), file(reference)

    output:
    path "${sample_id}.*", emit: cyrius_outputs

    script:
    """
    # prepare sample manifest
    echo "${cram[0]}" > manifest.txt

    # run cyrius
    star_caller.py \
        --manifest manifest.txt \
        --genome ${final_params.genome} \
        --reference ${reference[0]} \
        --prefix ${sample_id} \
        --outDir .
    """
}

process ALDY {
    tag "${sample_id}"
    container = "aldy:3.3"
    publishDir "${final_params.publish_dir}/aldy", mode: "copy"

    input:
    tuple val(sample_id), file(cram), file(cram_index)
    tuple val(reference_id), file(reference)

    output:
    path "${sample_id}.*", emit: aldy_outputs

    script:
    """
    aldy genotype \
        --profile illumina \
        --gene CYP2D6 \
        --reference ${reference[0]} \
        --output ${sample_id}.aldy \
        ${cram}
    """
}

/*
----------------------------------------------------------------------
WORKFLOW
---------------------------------------------------------------------
*/

// parameters
final_params = check_params(params, workflow)

// input channels
// cram_ch = channel.fromFilePairs(final_params.cram_pattern)

cram_ch = Channel.fromPath(params.cram_list)
                 .splitText()
                 .map{ [ file(it).getBaseName(), it, it.trim()+".crai"  ] }
cram_ch.view()
reference_ch = channel.fromFilePairs(final_params.reference_pattern)
reference_ch.view()

// main
workflow {
    CYRIUS(cram_ch, reference_ch)
    ALDY(cram_ch, reference_ch)
}

// triggers
workflow.onComplete {
    complete_message(final_params, workflow, version)
}
workflow.onError {
    error_message(workflow)
}