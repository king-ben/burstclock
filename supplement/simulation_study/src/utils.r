# utils.r
#
# shared utility functions
require("whisker")
require("stringr")


# whisker is R implementation of Mustache templating language
process_template = function(template, data, output){
    if(file.exists(template))
        template = readLines(template)
    text = whisker::whisker.render(template, data)

    if(!is.null(output)){
        writeLines(text, output)
        return()
        } else {
        return(text)
        }
    }

find_tags = function(template){
    if(file.exists(template)){
        template = readLines(template)
        }
    tags = stringr::str_extract_all(template, "\\{{2,3}[/#]?[.\\w]*\\}{2,3}")
    tags = unlist(tags)
    tags = stringr::str_remove_all(tags, "[\\{\\}/#]")
    tags = tags[tags != "." ]
    tags = unique(tags)
    tags
    }

# temporarily set path to particular directory
# path is restored once the calling function/frame ends.
settmpwd = function(wd){
    envir = parent.frame()
    envir$oldwd = getwd()
    do.call("on.exit", list(quote(setwd(oldwd))), envir=envir)
    setwd(wd)
    }

run_beast = function(xml){
    print(paste("...... start beast: ", xml))
    settmpwd(dirname(xml))
    system2(
      command="beast",
      args=c("-overwrite", basename(xml)),
      stdout=paste(basename(xml), ".screenlog", sep="")
    )
    print("...... end beast")
    }

run_loganalyser = function(dir){
  in_path = paste(dir, "test.???.log", sep="")
  out_path = paste(dir, "results.tsv", sep="")
  system2("loganalyser", args=c("-oneline", in_path, ">", out_path))
}

run_coverage_calculator = function(dir){
  samples_path = "intermediate/sampling/SAMPLING.log"
  results_path = paste(dir, "results.tsv", sep="")
  coverage_path = paste(dir, "coverage/", sep="")

  mkdir(coverage_path)
  system2("applauncher", 
          args=c("CoverageCalculator",
                 "-log", samples_path,
                 "-logA", results_path,
                 "-out", coverage_path))
}

run_treeannotator_all = function(dir){
  input_file_pattern = "test.*.trees"
  input_files = list.files(path=dir, pattern=input_file_pattern)
  for (input_file in input_files) {
    run_treeannotator(paste(dir, input_file, sep="/"))
  }
}

run_treeannotator = function(in_file){
  out_file = paste(tools::file_path_sans_ext(in_file), "summary", "tree", sep=".")
  print(in_file)
  print(out_file)
  system2("treeannotator", args=c(in_file, out_file))
}

# similar to mkdir -p
mkdir = function(dir){
    if(!dir.exists(dir))
        dir.create(dir, recursive=TRUE)
    }
