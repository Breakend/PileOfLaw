#########################################
####       Pile of Law, Figure 2     ####
#          Last updated: June 28        #
#########################################

#### SETUP ####
# Load software
rm(list=ls())
library(psych)
library(tidyverse)
library(ggplot2)
library(stringr)
library(gridExtra)

# Set root
root <- "/Users/MarkKrass/Downloads/"

### Import Toxicity Scores
# Get data: Profanity Checker
pc <- read.csv(paste0(root, "pc_only_scores.csv"),
               colClasses = c("numeric","numeric",
                              "factor","factor",
                              "numeric","character","factor")) %>% 
  mutate(year = as.numeric(str_extract(Date, "^[[:digit:]]{4}"))) %>% 
  select(-Date)

# Get data: Toxigen
tx <- read.csv("/scratch/users/mkrass/pile/perspective_scores_toxigen_only.csv",
               stringsAsFactors = T)

# Get data: Detoxify
dt.max <- read.csv("/scratch/users/mkrass/pile/detoxify_scores.csv",
                   stringsAsFactors = T )%>%
  group_by(DocIndex, SentenceIndex) %>% 
  summarize(Score = max(Score))

# Get data: Perspective
pp <- read.csv("/scratch/users/mkrass/pile/perspective_scores_pc_only.csv",
               stringsAsFactors = T) %>% 
  filter(Category %in% toupper(tox_classes)) %>% 
  group_by(DocIndex, SentenceIndex) %>% 
  summarize(Score = max(Score))

### Merge Toxicity Score
pc <- tx %>% select(DocIndex,SentenceIndex,Score) %>% rename(toxigen=Score) %>% 
  right_join(pc)
pc <- dt.max %>% select(DocIndex,SentenceIndex,Score) %>% rename(detoxify=Score) %>% 
  right_join(pc)
pc <- pp %>% select(DocIndex,SentenceIndex,Score) %>% rename(perspective=Score) %>% 
  right_join(pc)


### Load the Supreme Court Database (Spaeth, Epstein et al. 2021)
load(paste0(root, "SCDB_2021_01_caseCentered_Citation.Rdata"))
load(paste0(root, "SCDB_Legacy_07_caseCentered_Citation.Rdata"))

# Get crosswalk of case names
scdb.xw <- read.csv(paste0(root,"scdb_crosswalk.csv"), stringsAsFactors = T) %>% 
  rename(Name=name) %>% 
  mutate(year = as.numeric(substr(decision_date, start=1,stop=4)))

# Rename
scdb <- SCDB_2021_01_caseCentered_Citation %>% select(dateDecision, caseName, usCite, issueArea) ; rm(SCDB_2021_01_caseCentered_Citation)
scdb.legacy <- SCDB_Legacy_07_caseCentered_Citation %>% select(dateDecision, caseName, usCite, issueArea); rm(SCDB_Legacy_07_caseCentered_Citation)


pc <- pc %>% 
  left_join(scdb.xw[,c("Name","year","usr","scdb")]) %>% 
  distinct(DocIndex,SentenceIndex,.keep_all=T)


pc <- pc %>% rename(caseId = scdb) %>% left_join(scdb)

pcm.cr.long <- pc %>% 
  select(year,DocIndex, issueArea,perspective,detoxify,Score,toxigen) %>% 
  pivot_longer(perspective:toxigen,names_to="model",values_to="score2")



# Save merged
pc %>% saveRDS(file=paste0(root, "merged_maxes.RDS"))

# (Optional: Load merged )
#pc <- readRDS(paste0(root,"merged_maxes.RDS"))


#### Obtain Cohen's K at Multiple Thresholds ####

roundUp <- function(x){round(x/10)*10}
out <- c()
yrs <- c()
w <- c()
ts <- c()
# Group case years into 10-year bins
pc$yr_bin <- sapply(pc$year, roundUp)

# At multiple thresholds, obtain Cohen's K
for(t in c(0.5,0.8,0.9,0.95)){
  pc <- pc %>% mutate(
    detoxify.yn = ifelse(detoxify>t,1,0),
    profanitycheck.yn = ifelse(Score>t,1,0),
    toxigen.yn = ifelse(toxigen>t,1,0),
    perspective.yn = ifelse(perspective>t,1,0),
    iss_desc = case_when(issueArea == 2  ~ "Civil Rights",
                         TRUE ~ "All Others"))
  # Exclude early years with few data points
  for(y in sort(unique(pc$yr_bin))[5:26]){
    # Focus on comparing Perspective and Profanity-Checker,
    # since these are especially popular
    dat <- pc %>% 
      filter(yr_bin == y) %>% 
      select(perspective.yn,profanitycheck.yn) %>% 
      drop_na() %>% 
      as.matrix()
    k <- cohen.kappa(x=as.matrix(dat))$kappa
    out <- c(out,k)
    yrs <- c(yrs,y)
    w <- c(w, nrow(dat))
    ts <- c(ts, t)
  }}

# Collect data
cpdat <- data.frame(k = out, year=yrs, w=w, ts=ts)

#### Plot ####

# Left panel: Cohen's K
cohens <- cpdat %>% 
  # Remove points with too few data points
  filter(ts %in% c(0.5),w>5000) %>% 
  ggplot(aes(x=year,y=k)) + 
  geom_point(aes(size=w)) +
  geom_line() + scale_size(guide="none") + 
  ylab("Cohen's K") + xlim(1880,2010)


# Right panel: issue scores by area over time
plt.issue.area.share <- pcm.cr.long %>% 
  mutate(iss_desc = case_when(issueArea == 2  ~ "Civil Rights",
                              TRUE ~ "All Others"),
         model_desc = case_when(model == "Score" ~ "profanity_checker",
                                TRUE ~ model),
         score.yn = ifelse(score2 > 0.5,1,0)) %>% 
  group_by(year,model_desc,iss_desc) %>% 
  summarize(score=mean(score.yn),n=n()) %>% 
  ungroup() %>% 
  ggplot(aes(x=year,y=score, color=model_desc)) + 
  geom_smooth(span=0.3)+ylab("Share P(Toxic) > 0.5")+
  facet_wrap(~iss_desc) + xlim(1875,2022) + theme(legend.position = "right", legend.text = element_text(size = 6),
                                                  legend.title = element_text(size = 8)) + 
  guides(color = guide_legend(override.aes = list(size = 0.5))) 


ggsave(plt.issue.area.share, filename = paste0(root,"share_toxic_issue.pdf"),
       device="pdf",width=7,height=3)


## Assemble plots
assembled <- grid.arrange(cohens, plt.issue.area.share, nrow=1, widths=c(0.3,0.7))
ggsave(assembled, filename = paste0(root,"combined_cohens_toxic.pdf"),
       device="pdf",width=8,height=3)


