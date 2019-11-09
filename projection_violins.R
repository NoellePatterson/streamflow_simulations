library(reshape2)
library(vioplot)
library(ggplot2)

workingDir <- "/Users/noellepatterson/apps/Other/Process_flow_projections/"

files = Sys.glob("data/vioplot/*/viodata/*.csv")
for (file in files) {
  data_values <- read.csv(file, header = TRUE, check.names = FALSE, na.strings=c("","NA"))
  df <- data.frame(data_values)
  names(df) <- c("index","historic","future")
  df <- df[c("historic","future")]
  mdf <- melt(df)
  mdf$variable <- as.factor(mdf$variable)
  groups <- c("historic","future")
  groups <- as.factor(groups) 
  name <- strsplit(file, "/")
  folder_name <- paste(name[[1]][1], name[[1]][2],name[[1]][3], "plots", sep="/")
  dir.create(folder_name, showWarnings = FALSE)
  name <- tail(name[[1]], n=1)
  name <- substr(name, 1, nchar(name)-4)
  
  g <- ggplot(mdf,aes(x=variable,y=value)) +
    geom_violin() +
  geom_violin(aes(fill = factor(variable))) +
  geom_boxplot(width=0.1, fill="white") +
  labs(title=name, x="", y="") +
  theme(plot.title = element_text(hjust = 0.5))
  g + scale_fill_manual(name = "", labels= c("1950-2005","2020-2099"),values=c("red", "blue"))

  ggsave(paste(name,".png", sep=""), path=folder_name)
}
