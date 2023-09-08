library(readxl)
library(rms)
library(ggplot2)
library(survival)
library(car)
library(rms)
library(Rnalytica)
library(CoxR2)

npm_survival <- read.csv("survival_metric_com_fill_update.csv")

View(npm_survival)

npm_survival$age_start = c(0, unlist(lapply(2:nrow(npm_survival),
                                            function(x){ ifelse(npm_survival[(x-1),"package_name"] == npm_survival[x,"package_name"],
                                                                npm_survival[(x-1),"Age"],
                                                                0) })))

View(npm_survival.f)

npm_survival.f = subset(npm_survival, age_start!=Age)

npm_survival.f$License_code = as.factor(npm_survival.f$License_code)

npm_survival.f$Commits = as.numeric(npm_survival.f$Commit)

Data_all = npm_survival.f[, c('Contributor', 'Commit', "Issue",	"Non.Developer.Issue",	"core_size",	"Dormant",	"License_code",	"add_client_issue",	"add_client_pr",	"add_dependency_issue",	"add_dependency_pr",	"add_library_issue",
                              "add_library_pr",	"add_nonmaintain_issue",	"add_nonmaintain_pr",	"down_client_issue",	"down_client_pr",	"down_dependency_issue",	"down_dependency_pr",	"down_library_issue",	"down_library_pr",	"down_nonmaintain_issue",	"down_nonmaintain_pr",	"remove_client_issue",	"remove_client_pr",
                              "remove_dependency_issue",	"remove_dependency_pr",	"remove_library_issue",	"remove_library_pr",	"up_client_issue",	"up_client_pr",	"up_dependency_issue",	"up_dependency_pr",	"up_library_issue",
                              "up_library_pr",	"up_nonmaintain_issue",	"up_nonmaintain_pr",	"remove_nonmaintain_issue",	"remove_nonmaintain_pr")]

View(Data_all)

hist(log(npm_survival.f$Contributor+1)) #manually check the confunding factors one by one, i.e., Contributor here.

qqPlot(npm_survival.f$Commit)

model_fit <- coxph(Surv(age_start, Age, Dormant) ~ Commit + log(Contributor+1) + log(Non.Developer.Issue+1) + core_size + License_code +
                add_client_issue + add_client_pr + add_dependency_pr + add_library_issue + add_library_pr + add_nonmaintain_issue +
                add_nonmaintain_pr + 
                down_client_issue + down_client_pr +  down_dependency_pr + down_library_issue + down_library_pr + down_nonmaintain_issue +
                down_nonmaintain_pr + 
                remove_client_issue + remove_client_pr + remove_dependency_pr + remove_library_issue + remove_library_pr + remove_nonmaintain_issue +
                remove_nonmaintain_pr +
                up_client_issue + up_client_pr + up_dependency_pr  + up_library_pr + up_nonmaintain_issue +
                up_nonmaintain_pr,
              data = npm_survival.f)

cox.zph(model_fit) %>%
  extract2("table") %>%
  txtRound(digits = 2) %>%
  knitr::kable(align = "r")
test.ph = cox.zph(model_fit)
test.ph
ggcoxzph(test.ph[14])

coxr2(model_fit)

summary(model_fit)

vif(model_fit)

Anova(model_fit, type=2)

round(exp(model_fit$coefficients), 2)

#Data_all$resid_mart <- residuals(model_fit, type = "schoenfeld")

#Data_all$index <- seq.int(nrow(Data_all))

#figure = ggplot(data = Data_all, mapping = aes(x = index, y = resid_mart)) +
#  geom_point() +
#  geom_smooth() +
#  labs(title = "index") +
#  theme_bw() + theme(legend.key = element_blank())

library(survminer)
library(ggpubr)
ggsurvplot(test_auto)
test.ph = cox.zph(test_auto)
ggcoxzph(test.ph)


#Below basic one without taking confounding factors

s = Surv(npm_survival.f$age_start, npm_survival.f$Age, npm_survival.f$Dormant)
sfit = survfit(s ~ 1)

p = ggsurvplot(
  sfit,
  # sfit0,
  data = npm_survival.f,
  # data = sd.0,
  size = 1,                 # change line size
  palette = c("#2E9FDF"),
  #c("#E7B800", "#2E9FDF"),# custom color palettes
  conf.int = TRUE,          # Add confidence interval
  # pval = TRUE,              # Add p-value
  # risk.table = TRUE,        # Add risk table
  # risk.table.col = "strata",# Risk table color by groups
  # legend.labs =
  # c("Male", "Female"),    # Change legend labels
  # risk.table.height = 0.25, # Useful to change when you have multiple groups
  legend = "none",
  xlab = "Time in months",   # customize X axis label.
  break.time.by = 12,     # break X axis in time intervals by 500.
  ggtheme = theme_light()
  # ggtheme = theme_bw()      # Change ggplot2 theme
)
show(p)
