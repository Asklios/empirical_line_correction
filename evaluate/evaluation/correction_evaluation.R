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


for (location in names(data[[1]])) {
  
  max_values <- c()
  mean_values <- c()
  avg_reflactance <- c()
  values_percentage <- c()
  hmr <- c()
  hmf <- c()
  data_type <- c()
  r_squared_veg <- c()
  r_squared_non_veg <- c()
  
  j <- 1
  for (d in data) {
    for (probe in names(d[[location]])) {
      r_squared_veg <- c(r_squared_veg, r_squared_veg[[probe]])
      r_squared_non_veg <- c(r_squared_non_veg, r_squared_non_veg[[probe]])
      
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
  
  if (!dir.exists("plots/locations")) {
    dir.create("plots/locations")
  }
  
  png(paste0("plots/locations/", location, ".png"), width = 1600, height = 1600)
  par(cex = 3.5)
  # create empty plot
  plot(0, 0, type = "n", ylim = c(0, 0.6), xlim = c(390, 870), xaxs = "i", yaxs = "i", 
       xlab = "Wavelength [nm]", ylab = "Reflectance")
  
  # legend top left
  legend("topleft", legend = c("output_factors", "skip_veg", "skip_non_veg", "measurement"), 
         col = c("black", "blue", "green", "red"), lwd = 5)
  
  for (i in 1:length(unique(hmr))) {
    for (k in 1:3) {
      index <- (i - 1) * 3 + k
      segments(hmr[index], avg_reflactance[index], hmf[index], avg_reflactance[index],
               col = "red", lwd = 4)
      
      color <- "black"
      if (data_type[index] == "skip_veg") {
        color <- "blue"
      }
      else if (data_type[index] == "skip_non_veg") {
        color <- "green"
      }
      
      segments(hmr[index], values_percentage[index], hmf[index], 
               values_percentage[index], col = color, lwd = 2)
      
      rect_left <- hmr[index] + (k - 1) * (hmf[index] - hmr[index]) / 3
      rect_right <- hmr[index] + k * (hmf[index] - hmr[index]) / 3
      center <- hmr[index] + (k - 0.5) * (hmf[index] - hmr[index]) / 3
      
      # draw transparent rect between avg_reflactance and values_percentage
      #rect(rect_left + .5, avg_reflactance[index], rect_right - .5, values_percentage[index], col = rgb(0,0,1,0.1), border = "transparent")
      
      arrows(center, values_percentage[index], center, avg_reflactance[index], 
             length = 0.1, angle = 30, col = color, code = 2, lwd = 2)
    }
  }
  dev.off()
  
  png(paste0("plots/locations/rect_", location, ".png"), width = 1600, height = 1600)
  par(cex = 3.5)
  # create empty plot
  plot(0, 0, type = "n", ylim = c(0, 0.7), xlim = c(390, 870), xaxs = "i", yaxs = "i", 
       xlab = "Wavelength [nm]", ylab = "Reflectance", main = location)
  
  # legend top left
  legend("topleft", legend = c("output_factors", "skip_veg", "skip_non_veg", "measurement"), 
         col = c("black", "blue", "green", "red"), lwd = 5)
  
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
    
    # draw transparent rect between avg_reflactance and values_percentage
    rect(hmr[i] , avg_reflactance[i], hmf[i], values_percentage[i], col = rgb(0,0,0,0.1), border = "transparent")
  }
  dev.off()
}



j <- 1
for (d in data) {
  
  data_type <- data_types[[j]]
  j <- j + 1
  
  max_values <- c()
  mean_values <- c()
  avg_reflactance <- c()
  values_percentage <- c()
  hmr <- c()
  hmf <- c()
  locations <- c()
  
  for (location in names(d)) {
    for (probe in names(d[[location]])) {
      locations <- c(locations, location)
      probe <- d[[location]][[probe]]
      max_values <- c(max_values, probe$max)
      mean_values <- c(mean_values, probe$mean)
      avg_reflactance <- c(avg_reflactance, probe$average_reflectance)
      values_percentage <- c(values_percentage, probe$value_percentage)
      hmr <- c(hmr, probe$hmr)
      hmf <- c(hmf, probe$hmf)
    }
  }
  
  png(paste0("plots/", data_type, ".png"), width = 1600, height = 1600)
  par(cex = 3.5)
  # create empty plot
  plot(0, 0, type = "n", ylim = c(0, 0.6), xlim = c(390, 870), xaxs = "i", yaxs = "i", 
       xlab = "Wavelength [nm]", ylab = "Reflectance")
  
  # plot horizontal lines from hmr to hmf
  for (i in 1:length(hmr)) {
    segments(hmr[i], avg_reflactance[i], hmf[i], avg_reflactance[i], col = "red")
    segments(hmr[i], values_percentage[i], hmf[i], values_percentage[i], col = "blue")
    
    # draw transparent rect between avg_reflactance and values_percentage
    rect(hmr[i], avg_reflactance[i], hmf[i], values_percentage[i], col = rgb(0,0,1,0.1), border = "transparent")
  }
  
  dev.off()
  
  png(paste0("plots/", data_type, "_small.png"), width = 1600, height = 1600)
  par(cex = 3.5)
  # create empty plot
  plot(0, 0, type = "n", ylim = c(0, 0.6), xlim = c(390, 870), xaxs = "i", yaxs = "i", 
       xlab = "Wavelength [nm]", ylab = "Reflectance")
  
  rect_width <- (hmf - hmr) / 7
  
  # plot horizontal lines from hmr to hmf
  for (i in 1:length(unique(hmr))) {
    for (k in 1:7) {
      index <- (i - 1) * 7 + k
      segments(hmr[index], avg_reflactance[index], hmf[index], avg_reflactance[index], col = "red")
      segments(hmr[index], values_percentage[index], hmf[index], values_percentage[index], col = "blue")
      
      rect_left <- hmr[index] + (k - 1) * rect_width[index]
      rect_right <- hmr[index] + k * rect_width[index]
    
      # draw transparent rect between avg_reflactance and values_percentage
      rect(rect_left + .5, avg_reflactance[index], rect_right - .5, values_percentage[index], col = rgb(0,0,1,0.1), border = "transparent")
    }
  }
  
  dev.off()
  
  
  png(paste0("plots/", data_type, "_arrows.png"), width = 1600, height = 1600)
  par(cex = 3.5)
  # create empty plot
  plot(0, 0, type = "n", ylim = c(0, 0.6), xlim = c(390, 870), xaxs = "i", yaxs = "i", 
       xlab = "Wavelength [nm]", ylab = "Reflectance")
  
  rect_width <- (hmf - hmr) / 7
  
  # plot horizontal lines from hmr to hmf
  for (i in 1:length(unique(hmr))) {
    for (k in 1:7) {
      #segments(hmr[i], avg_reflactance[i], hmf[i], avg_reflactance[i], col = "red")
      #segments(hmr[i], values_percentage[i], hmf[i], values_percentage[i], col = "blue")
      #rect(hmr[i], avg_reflactance[i], hmf[i], values_percentage[i], col = rgb(0, 0, 1, 0.1), border = NA)
      
      index <- (i - 1) * 7 + k
      
      rect_left <- hmr[index] + (k - 1) * rect_width[index]
      rect_right <- hmr[index] + k * rect_width[index]
      center <- hmr[index] + (k - 0.5) * rect_width[index]
      
      #rect(rect_left, avg_reflactance[index], rect_right, values_percentage[index], col = rgb(0, 0, 1, 0.1), border = NA)
      
      arrows(center, values_percentage[index], center, avg_reflactance[index], 
             length = 0.1, angle = 30, col = "blue", code = 2)
      segments(hmr[index], avg_reflactance[index], hmf[index], avg_reflactance[index], col = "red")
      text(center, avg_reflactance[index], labels = locations[index], pos = 4, offset = -0.5, cex = 0.4)
    }
  }
  
  dev.off()
}

