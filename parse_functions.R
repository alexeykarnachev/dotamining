#===============================================================================
# Function to parse team's matches.

# team.id - is the team's id on dotabuff

# features - features (columns) in the output dataframe:
#            Features: "match.date", "match.league", "team.name", 
#                      "team.id", "opponent.name", "opponent.id", "match.result",
#                      "match.time", "team.hero_1", "team.hero_2", "team.hero_3",
#                      "team.hero_4", "team.hero_5", "opponent.hero_1", 
#                      "opponent.hero_2", "opponent.hero_3", "opponent.hero_4", 
#                      "opponent.hero_5"
#                      

# minDate - min. date of the played matches

# minGames - min. team's games. If team has less games, that minGames-value, 
# function will return nothing

# parsePlayers - the logical. Need parse players in every match (parsing will 
# be 20-times longer)


parse.teamsMatchesResults = function(team.id, features, minDate, minGames, 
                                     parsePlayers){
  
  if(!is.null(minDate)){
    minDate = as.POSIXct(minDate)
  }
  
  team.id = as.character(team.id)
  url = paste0("http://dotabuff.com/esports/teams/", team.id, "/matches")
  doc = getNodeSet(htmlParse(url), "//tbody/tr[not(@class)]")
  pages = getNodeSet(doc[[1]], "//*/span[@class='last']/a[@href]")[[1]]
  if(is.null(pages)){
    pages = 1
  }else{
    pages = as.numeric(str_extract_all(xmlAttrs(pages),
                                       "([[:digit:]]+)$")[[1]])
  }
  
  team.name = xmlAttrs(getNodeSet(doc[[1]], "//h1/a/img")[[1]])[['title']]
  teamMatches.m = NULL
  team.m = NULL
  
  team.table = NULL
  for(page in 1:pages){
    
    if(page > 1){
      url = paste0("http://dotabuff.com/esports/teams/", team.id, 
                   "/matches?page=", page)
      doc = getNodeSet(htmlParse(url), "//tbody/tr[not(@class)]")
    }
    
    table = NULL
    rownames = NULL
    for(iRow in seq(along.with = doc)){
      
      row = NULL
      iRow.doc = doc[[iRow]]
      
      if(xmlValue((getNodeSet(iRow.doc, "td[2]")[[1]])[[1]]) == 'Unknown'){next}
      
      team.heroes = gsub(unlist(xmlApply(getNodeSet(iRow.doc, 
                                                    "td[4]/div/a[@href]"), 
                                         function(x) xmlAttrs(x))), 
                         pattern = "/heroes/", replacement = "" )
      
      opponent.heroes = gsub(unlist(xmlApply(getNodeSet(iRow.doc, 
                                                        "td[5]/div/a[@href]"), 
                                             function(x) xmlAttrs(x))), 
                             pattern = "/heroes/", replacement = "" )
      
      if(length(team.heroes) < 5 | length(opponent.heroes) < 5){next}
      
      match.date = xmlValue(getNodeSet(iRow.doc, "td[1]/small")[[1]])
      match.league = xmlValue(getNodeSet(iRow.doc, "td[2]/small")[[1]])
      match.time = xmlValue(getNodeSet(iRow.doc, "td[3]")[[1]])
      match.id = gsub(xmlAttrs(getNodeSet(iRow.doc, "td[1]/a")[[1]])['href'], 
                      pattern = "/matches/", replacement = "")
      match.result = xmlAttrs(getNodeSet(iRow.doc, "td[1]/a")[[1]])['class']
      opponent.id = gsub(xmlAttrs(getNodeSet(iRow.doc, "td[2]/a")[[1]])['href'], 
                         pattern = "/esports/teams/", replacement = "")
      opponent.name = xmlValue(getNodeSet(iRow.doc, "td[2]/a")[[1]])
      
      rownames = append(rownames, match.id)
      row = c(match.date, match.league, team.name, team.id, opponent.name, 
              opponent.id, match.result, match.time, team.heroes, opponent.heroes)
      table = rbind(table, row)
    }
    
    rownames(table) = rownames
    team.table = rbind(team.table, table)  
    print(paste0("Team ID: ", team.id, "; Page: ", page, "/", pages))
    
    if(!is.null(minDate)){
      oldMatches = which(as.POSIXct(team.table[,1]) < minDate)
      if(length(oldMatches) > 0){
        team.table = team.table[-oldMatches,]
        break  
      }
    }
    
  }
  
  if(is.null(minGames)){
    enoughGames = T
  }else if(nrow(team.table) >= minGames){
    enoughGames = T
  }else{
    enoughGames = F
  }
  
  if(!is.null(nrow(team.table)) && enoughGames  && !is.null(team.table)){
    
    colnames(team.table) = c("match.date", "match.league", "team.name", 
                             "team.id", "opponent.name", "opponent.id", 
                             "match.result", "match.time", "team.hero_1", 
                             "team.hero_2", "team.hero_3", "team.hero_4",
                             "team.hero_5", "opponent.hero_1", "opponent.hero_2",
                             "opponent.hero_3", "opponent.hero_4", "opponent.hero_5")
    
    team.table = unfactor.df(data.frame(team.table))
    
    if(parsePlayers){
      
      playersNames.table = NULL
      
      for(match.id_i in 1:nrow(team.table)){
        
        match.id = rownames(team.table)[match.id_i]
        team = team.table$team.id[match.id_i]
        opponent = team.table$opponent.id[match.id_i]
        
        url = paste0("http://dotabuff.com/matches/", match.id)
        doc = htmlParse(url)
        
        team1.names = unlist(xmlApply(
          getNodeSet(doc, "//a[@class='player-radiant']"), xmlValue))
        team2.names = unlist(xmlApply(
          getNodeSet(doc, "//a[@class='player-dire']"), xmlValue))
        team12names = cbind(team1.names, team2.names)
        
        team1.ids = unlist(str_extract_all(unlist(xmlApply(
          getNodeSet(doc, "//a[@class='player-radiant']"), xmlAttrs)), 
          "([[:digit:]]+)"))
        team2.ids = unlist(str_extract_all(unlist(xmlApply(
          getNodeSet(doc, "//a[@class='player-dire']"), xmlAttrs)), 
          "([[:digit:]]+)"))
        team12ids = cbind(team1.ids, team2.ids)
        
        teams.ids = unlist(str_extract_all(unlist(unique(xmlApply(
          getNodeSet(doc, "//header[@style='vertical-align: middle']/a[@ href]"), 
          function(x) xmlAttrs(x)))), "([[:digit:]]+)"))
        
        teamCol = which(teams.ids == team)
        opponentCol = which(teams.ids == opponent)
        
        team.players.names = team12names[,teamCol]
        team.players.ids = team12ids[,teamCol]
        
        opponent.players.names = team12names[,opponentCol]
        opponent.players.ids = team12ids[,opponentCol]
        
        playersNames.row = c(team.players.names, team.players.ids, 
                             opponent.players.names, opponent.players.ids)   
        playersNames.table = rbind(playersNames.table, playersNames.row)
        
        print(paste0("Team ID: ", team.id, "; Match: ", match.id_i, "/", nrow(team.table)))
        
      }
      rownames(playersNames.table) = NULL
      colnames(playersNames.table) = c("team.player_1", "team.player_2", 
                                       "team.player_3", "team.player_4", 
                                       "team.player_5", "team.player_1.id", 
                                       "team.player_2.id", "team.player_3.id", 
                                       "team.player_4.id", "team.player_5.id",
                                       "opponent.player_1", "opponent.player_2", 
                                       "opponent.player_3", "opponent.player_4", 
                                       "opponent.player_5", "opponent.player_1.id", 
                                       "opponent.player_2.id", "opponent.player_3.id", 
                                       "opponent.player_4.id", "opponent.player_5.id")
      if(is.null(features)){
        features = c(colnames(team.table), colnames(playersNames.table))
      }else{
        features = c(features, colnames(playersNames.table))
      }
      
      team.table = unfactor.df(cbind(team.table, playersNames.table))
      
    }
    
    if(!is.null(features)){
      return(team.table[,features]) 
    }else{
      return(team.table) 
    }
    
  }
}










