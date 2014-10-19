# Data Processing For Machine Learning Routines

################################################################################
# Normalize Data Set;
# df - is data frame;
# by - rows or columns
# type - type of normalization ("0_1")

normalizedf = function(df, by, type = "0_1"){
  
  if(type == "0_1"){
    
    if(!is.data.frame(df)){
      stop("input must be a data frame")
    }
    
    if(by == "rows"){
      df.n = data.frame(t(apply(df, MARGIN = 1, function(x) (x-min(x))/max(x-min(x)))))
      return(df.n)
    }else if(by == "columns"){
      df.n = data.frame((apply(df, MARGIN = 2, function(x) (x-min(x))/max(x-min(x)))))
      return(df.n)
    }else{
      stop("by myst be rows or columns")
    }
    
  }
  
}

################################################################################
# Generate random(or not random) indexes for data splitting
# m - data set lengh (rows)
# p - vector with parts proportions (example: p = c(0.6, 0.2, 0.2))
# random - logical. If TRUE - returns shuffled indexes

generateIndexesForSplit = function(m, p, random){
  
  if(sum(p) != 1){
    stop("sum of p elements must be equal to 1")
  }
  
  if(random){
    ind = sample(1:m, replace = F)
  }else{
    ind = 1:m
  }
  
  ind.list = list()
  for(i in 1:length(p)){
    
    if(i == length(p)){
      
      ind.i = ind
      ind.list[[length(ind.list) + 1]] = ind.i
      
    }else{
      
      ip = p[i]
      ind.i = ind[1:as.integer(ip * m)]
      ind = ind[-(1:as.integer(ip * m))]
      
      ind.list[[length(ind.list) + 1]] = ind.i
      
    }
    
  }
  
  return(ind.list)
  
  
}


unfactor.v <- function(factors,ignore=",",...)
{
  if (!is.factor(factors)) {
    message("In repsych::unfactor: the vector provided is not a factor; no values changed")
    return(factors)
  }
  char.ret <- as.character(factors) #make use of S3 versions of as.character
  #Get rid of those things in ignore
  for (pattern in ignore) {
    char.ret <- gsub(pattern,"",char.ret,...)
  }
  #try to convert to numeric
  num.try <- suppressWarnings(as.numeric(char.ret))
  num.n.fail <- sum(is.na(num.try))
  if (num.n.fail == 0) {
    #none failed to convert, must want numeric
    ret <- num.try
  }
  if (num.n.fail == length(factors)) {
    #none converted, they must want text
    return(char.ret) 
  } else {
    num.ret <- tryCatch(as.numeric(char.ret),
                        warning=function (w) {
                          #see how many we failed to convert    
                          #names(table(as.character(my.ugly.factor)[is.na(})))]))
                          #nameNAvalues(as.numeric(as.character(not.a.factor)))
                        }
    )
  }#end non-numeric error handling
  if (!is.null(num.ret)) return(num.ret) else return(char.ret)
  stop("In repsych::unfactor: no return value was provided, coding error")
}

unfactor.df <- function(df){
  # Find the factors
  id <- sapply(df, is.factor)
  # Convert to characters
  df[id] <- lapply(df[id], as.character)
  df
}

insert.at <- function(a, pos, ...){
  dots <- list(...)
  stopifnot(length(dots)==length(pos))
  result <- vector("list",2*length(pos)+1)
  result[c(TRUE,FALSE)] <- split(a, cumsum(seq_along(a) %in% (pos+1)))
  result[c(FALSE,TRUE)] <- dots
  unlist(result)
}

