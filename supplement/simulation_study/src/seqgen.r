# seqgen.r
#
# simulate sequences based on parameter values

import::here(.from="beast.r", merge, process_beast_template)
import::here(.from="utils.r", run_beast)
import::here(.from="stringr", str_pad)
import::here(.from="icesTAF", mkdir)
import::here(.from="rlist", list.append)
import::here(.from="parallel", mclapply)
import::here(.from="tools", file_path_sans_ext, file_ext)

seqgen = function(seqgen_template,
                  seqgen_config,
                  taxa,
                  output,
                  parameters = list(),
                  repeats = 1
    ){
    output = normalize_path(output)

    for(i in seq_len(repeats)){
        # repeat_output = repeat_path(output, i) # some temp path
        repeat_output = output
        parameters[["sequence_output"]] = buid_seq_output(repeat_output)
        process_beast_template(
            seqgen_template,
            seqgen_config,
            taxa,
            repeat_output,
            parameters
            )
        run_beast(repeat_output)
        }
    }


seqgen_sampling = function( log,
                            trees_path,
                            seqgen_template,
                            seqgen_config,
                            merge_config,
                            taxa,
                            output,
                            parameters = list(),
                            repeats = 1
    ){
    log = read_log(log)
    
    
    trees = ape::read.nexus(trees_path)[-1]

    if(nrow(log) != length(trees))
        stop("ERROR: rows of log should be identical to the number of trees")
    
    all.run.args = list()
    
    n.taxa = length(taxa)
    n.nodes = 2 * n.taxa - 1

    for(i in seq_along(trees)){
        variables = as.list(log[i,])
        variables[["tree"]] = ape::write.tree(trees[[i]], "")
        variables[["taxa"]] = taxa
        variables[["n_rates"]] = n.nodes - 1
        
        variables = merge(variables, parameters)
        sampling_output = repeat_path(output, i)

        if ("branchRates.1" %in% names(variables)) {
            branchRates = list()
            for (i in 1:(n.nodes-1)) {
                branchRates = list.append(branchRates, variables[[paste("branchRates", i, sep=".")]])
            }
            variables[["branchRates"]] = paste(branchRates, collapse = ' ')
        }

        run.args = list(vars=variables, out=sampling_output)
        all.run.args = list.append(all.run.args, run.args)
    }

    mclapply(X = all.run.args,
             FUN = function(run.args) seqgen(seqgen_template,
                                             seqgen_config,
                                             taxa,
                                             run.args[['out']],
                                             run.args[['vars']],
                                             repeats),
             mc.cores = 4,
             mc.preschedule = FALSE,
             mc.allow.recursive = FALSE)
    }


normalize_path = function(x){
    wd = getwd()
    file.path(wd, x)
    }


repeat_path = function(path, i){
    i_padded = str_pad(i, 3, pad="0")
    paste(file_path_sans_ext(path), i_padded, file_ext(path), sep=".")
}


buid_seq_output = function(path){
  path_stripped <- file_path_sans_ext(path)
  seq_dir <- paste(path_stripped, ".data/", sep="")
  mkdir(seq_dir)
  paste(seq_dir, "data.xml", sep="")
}


read_log = function(log){
    log = read.table(log, header=TRUE, stringsAsFactors=FALSE)
    log = log[-1,] # first values are starting positions
    bad_columns = c("Sample", "posterior", "likelihood", "prior")
    log = log[, !colnames(log) %in% bad_columns]
    log
    }


to_list = function(vec){
    # as.list(vec) would be enough if not for multidimensional parameters
    names = names(vec)
    dotnames = grep("\\.[0-9]+$", names)
    dotvec = vec[dotnames]
    vec = vec[-dotnames]
    dotlist = to_list_dotvec(dotvec)
    list = as.list(vec)
    return(c(vec, dotlist))
    }


to_list_dotvec = function(dotvec){
    unique_dotnames = unique(sub("\\.[0-9]+$", "", names(dotvec)))
    dotlist = lapply(unique_dotnames, to_list_dotname, dotvec)
    names(dotlist) = unique_dotnames
    dotlist
    }


to_list_dotname = function(name, dotvec){
    match = unlist(dotvec[grep(name, names(dotvec))])
    order = strsplit(names(match), split=".", fixed=TRUE)
    order = lapply(order, getElement, 2)
    order = as.numeric(unlist(order))
    names(match) = NULL
    match[order]
    }
