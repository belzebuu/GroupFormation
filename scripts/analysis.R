priorities <- read.csv("../out/output4.csv",header=FALSE,na.strings="NA",dec=".", sep=";")
priorities <- priorities[,c(1:5,6:(5+16))]
names(priorities) <- c("ProNr","Titel","Type","Inst","Prio i alt","1. prio","2. prio","3. prio","4. prio","5. prio","6. prio","7. prio","8. prio","9. prio","10. prio","11. prio","12. prio","13. prio","14. prio","15. prio","16. prio")
names <- c("1. prio","2. prio","3. prio","4. prio","5. prio","6. prio","7. prio","8. prio","9. prio","10. prio","11. prio","12. prio","13. prio","14. prio","15. prio","16. prio")

library(dplyr)
#priorities <- priorities %>% mutate(Titel=substr(Titel,start=0,stop=30)) %>% filter(Inst %in% c("IMADA")) %>% select(-Type)
priorities <- priorities[order(priorities["Inst"],-priorities[names[1]],-priorities[names[2]],-priorities[names[3]],-priorities[names[4]]),]



library(googleVis)
Table <- gvisTable(priorities)
print(Table,file="../out/popularity.html")
#plot(Table)

