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
        --cram_list   Path to file with list of input crams (one file per line). Note: cram index must be available as <cram>.crai.
        --reference   Path to genome reference. Note: reference index must be available as <fasta>.fai or <fa>.fai.
        --genome      Genome build. One of: 19, 37, 38.

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
    publishDir "${final_params.publish_dir}/${sample_id}/cyrius", mode: "copy"

    input:
    tuple val(sample_id), file(cram), file(crai), file(fa), file(fai)

    output:
    path "${sample_id}.*", emit: cyrius_outputs

    script:
    """
    # prepare sample manifest
    echo "${cram}" > manifest.txt

    # run cyrius
    star_caller.py \
        --manifest manifest.txt \
        --genome ${final_params.genome} \
        --reference ${fa} \
        --prefix ${sample_id} \
        --outDir .
    """
}

process ALDY {
    tag "${sample_id}"
    container = "aldy:3.3"
    publishDir "${final_params.publish_dir}/${sample_id}/aldy", mode: "copy"

    input:
    tuple val(sample_id), file(cram), file(crai), file(fa), file(fai)

    output:
    path "${sample_id}.*", emit: aldy_outputs

    script:
    """
    aldy genotype \
        --profile illumina \
        --gene CYP2D6 \
        --reference ${fa} \
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
reference = channel.fromPath(final_params.reference)
    .map{ fa -> tuple( file(fa), file(fa + ".fai") ) }

cram = channel.fromPath(final_params.cram_list)
    .splitText(by: 1)
    .map{ cram -> tuple( file(cram).getBaseName(), file(cram.trim()), file(cram.trim() + ".crai") ) }

inputs = cram.combine(reference)

// main
workflow {
    CYRIUS(inputs)
    ALDY(inputs)
}

// triggers
workflow.onComplete {
    complete_message(final_params, workflow, version)
}
workflow.onError {
    error_message(workflow)
}