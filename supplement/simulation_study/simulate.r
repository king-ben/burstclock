# simulate.r
#
# Performs tree and sequence simulation together with BEAST analysis
# and its evaluation.
library("argparser")

import::from("src/beast.r", process_beast_template)
import::from("src/utils.r", settmpwd, mkdir, run_beast, run_loganalyser, run_coverage_calculator, run_treeannotator_all)
import::from("src/seqgen.r", seqgen_sampling)

options(scipen=999)

SAMPLING.DIR = "intermediate/sampling/"

main = function(){

    ntax = 20
    nsamples = 100
    simu_sample_interval = 200000
    repeats = 1

    mkdir("intermediate/sampling")
    mkdir("intermediate/bursty")
    mkdir("intermediate/burstfree")
    mkdir("intermediate/bursty/coverage")
    mkdir("intermediate/burstfree/coverage")

    taxa = make_taxa_names(ntax)
    
    # generate template to sample from prior
    simulator_params = list(
        "sample_from_prior" = "true",
        "taxa" = taxa,
        "nsamples" = 1 + nsamples,
        "chain_length" = 1 + simu_sample_interval*nsamples,
        "sample_interval" = simu_sample_interval,
        "n_rates" = 2*ntax - 2
        )
    
    # template_simulator = "templates/direct_simulator.xml"
    template_simulator = "templates/mcmc_simulator.xml"
    template_seqgen = "templates/seqgen_and_analysis.xml"

    config_bursty = "templates/bursty.toml"
    config_burstfree = "templates/burstfree.toml"

    process_beast_template(
        template_simulator,
        config_bursty,
        taxa,
        "intermediate/sampling/SAMPLING.xml",
        simulator_params
        )

    # run beast to sample from prior
    run_beast("intermediate/sampling/SAMPLING.xml")

    # simulate data and reconstruct with bursts
    seqgen_sampling(
        "intermediate/sampling/SAMPLING.log",
        "intermediate/sampling/SAMPLING.trees",
        template_seqgen,
        config_bursty,
        config_bursty,
        taxa,
        "intermediate/bursty/test.xml",
        list(seqlength="5000"),
        repeats = repeats
    )

    # simulate data and reconstruct without bursts
    seqgen_sampling(
        "intermediate/sampling/SAMPLING.log",
        "intermediate/sampling/SAMPLING.trees",
        template_seqgen,
        config_burstfree,
        config_burstfree,
        taxa,
        "intermediate/burstfree/test.xml",
        list(seqlength="5000"),
        repeats = repeats
    )
    
    # evaluate
    run_loganalyser("intermediate/bursty/")
    run_coverage_calculator("intermediate/bursty/")

    run_loganalyser("intermediate/burstfree/")
    run_coverage_calculator("intermediate/burstfree/")
    }

make_taxa_names = function(ntax){
    paste(1:ntax)
    # make.unique(rep(LETTERS, length.out=ntax), sep="")
    }


if(!interactive()){
    main()
    }
