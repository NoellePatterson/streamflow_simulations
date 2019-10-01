library(reshape2)

workingDir <- "/Users/noellepatterson/apps/Process_flow_projections/"
setwd(workingDir)

files = Sys.glob("data/vioplot/*.csv")
file = files[1]
for (file in files) {
  data_values <- read.csv(file, header = TRUE, check.names = FALSE, na.strings=c("","NA"))
  df <- data.frame(data_values)
  mdf <- melt(df)
  mdf$variable <- as.factor(mdf$variable)
  groups <- c("hist","fut")
  groups <- as.factor(groups) 
  a=boxplot(mdf$value ~ mdf$variable)
  
}