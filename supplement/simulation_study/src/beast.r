# beast.r
#
# generate XML for BEAST

import::here(.from="utils.r", process_template, settmpwd)
import::here(.from="RcppTOML", parseTOML)
import::here(.from="whisker", whisker.render)
import::here(.from="rlist", list.merge)

process_beast_template = function(template, config, taxa, output, parameters=NULL){
    toml = parseConfig(config, parameters)
    data = toml$data
    defaults = toml$defaults

    if(!is.null(parameters))
        defaults = merge(defaults, parameters)
    data = merge(data, defaults)
    
    data$taxa = taxa
    print(output)
    process_template(template, data, output)
    }


# add elements of list2 into list1
# if elements already exists, merge those elements
add = function(list1, list2){
    merge = function(x){c(list1[[x]], list2[[x]])}
    names = unique(c(names(list1), names(list2)))
    merged = lapply(names, merge)
    names(merged) = names
    merged
    }


# merge two lists, overwriting common elements (recursively)
# return empty list if either or both inputs are empty
merge = function(list1, list2){
    if( !( is.list(list1) || is.list(list2) ) )
        stop("Both elementy must be lists")
    if(is.empty(list1) && is.empty(list2))
        return(list())
    if(is.empty(list1))
        return(list2)
    if(is.empty(list2))
        return(list1)
    list.merge(list1, list2)
    }


# test whether list is null or empty
is.empty = function(x){
    is.null(x) || length(x) == 0
    }


# each TOML consist of XML chunks, path to subtemplates and default parameters
# for all chunks or any subtemplate
parseConfig = function(file, defaults=NULL){
    toml = parseTOML(file, escape=FALSE)
    settmpwd(dirname(file))

    defaults = merge(toml$defaults, defaults)
    data = list()
    if(!is.null(toml$templates))
        data = add(data, process_subtemplates(toml$templates, defaults))
    if(!is.null(toml$xml))
        data = add(data, process_xml_chunks(toml$xml, defaults))
    return(list("data" = data, "defaults" = defaults))
    }


process_subtemplates = function(subtemplates, defaults){  
    data = list()
    for(subtemplate in subtemplates){
        data = add(data, parseConfig(subtemplate, defaults)$data)
        }
    data
    }


process_xml_chunks = function(xml_chunks, defaults){
    lapply(xml_chunks, whisker.render, data=defaults)
    }
