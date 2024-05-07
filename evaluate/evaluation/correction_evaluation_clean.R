if (!require("pacman")) install.packages("pacman")
pacman::p_load(pacman, rjson, extrafont)
Sys.setenv(LANG = "en") # set language to english
wd <- "M:\\Bachelorarbeit\\python\\empirical_line_correction\\evaluate\\evaluation"
setwd(wd)
loadfonts()

output_factors <- fromJSON(file = "zonal_stats_output_factors.json")
skip_non_veg <- fromJSON(file = "zonal_stats_skip_non_veg.json")
skip_veg <- fromJSON(file = "zonal_stats_skip_veg.json")
data <- list(output_factors, skip_non_veg, skip_veg)

data_types <- c("output_factors", "skip_non_veg", "skip_veg")

r_squared_veg <- fromJSON(file = paste0(wd, "\\..\\..\\plots\\skip_non_veg\\r_squared.json"))
r_squared_non_veg <- fromJSON(file = paste0(wd, "\\..\\..\\plots\\skip_veg\\r_squared.json"))

r_squared_table <- data.frame(
  wavelength = names(r_squared_veg),
  veg = unlist(r_squared_veg),
  non_veg = unlist(r_squared_non_veg)
)


for (location in names(data[[1]])) {
  
  max_values <- c()
  mean_values <- c()
  avg_reflactance <- c()
  values_percentage <- c()
  hmr <- c()
  hmf <- c()
  data_type <- c()
  
  j <- 1
  for (d in data) {
    for (probe in names(d[[location]])) {
      probe <- d[[location]][[probe]]
      max_values <- c(max_values, probe$max)
      mean_values <- c(mean_values, probe$mean)
      avg_reflactance <- c(avg_reflactance, probe$average_reflectance)
      values_percentage <- c(values_percentage, probe$value_percentage)
      hmr <- c(hmr, probe$hmr)
      hmf <- c(hmf, probe$hmf)
      data_type <- c(data_type, data_types[[j]])
    }
    j <- j + 1
  }
  
  if (!dir.exists("plots_final")) {
    dir.create("plots_final")
  }
  
  png(paste0("plots_final/", location, ".png"), width = 1600, height = 1600)
  par(cex = 3.5)
  # create empty plot
  plot(0, 0, type = "n", ylim = c(0, 1), xlim = c(390, 870), xaxs = "i", yaxs = "i", 
       xlab = "Wavelength [nm]", ylab = "Reflectance", main = location)
  
  # legend top left
  legend("topleft", legend = c("output_factors", "skip_veg", "skip_non_veg", "measurement"), 
         col = c("black", "blue", "green", "red"), lwd = 5)
  
  # plot r_squared as line
  lines(r_squared_table$veg ~ r_squared_table$wavelength, col = "blue", lwd = 5)
  
  for (i in 1:length(hmr)) {
    segments(hmr[i], avg_reflactance[i], hmf[i], avg_reflactance[i],
             col = "red", lwd = 6)
    
    color <- "black"
    if (data_type[i] == "skip_veg") {
      color <- "blue"
    }
    else if (data_type[i] == "skip_non_veg") {
      color <- "green"
    }
    
    segments(hmr[i], values_percentage[i], hmf[i], 
             values_percentage[i], col = color, lwd = 4)
    
    rect(hmr[i] , avg_reflactance[i], hmf[i], values_percentage[i], col = rgb(0,0,0,0.1), border = "transparent")
  }
  dev.off()
}