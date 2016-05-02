# plot1090

Takes in BaseStation-like output and produces a graph of all positions captured.

## Basic usage

1. Capture SBS output into a file. For example, `nc localhost 30003 | grep '^MSG,3' > capture.csv`.
1. Graph it: `./draw_graph.py capture.csv` will produce a file named `map.png` in the current directory.

BaseStation output documentation: http://woodair.net/SBS/Article/Barebones42_Socket_Data.htm
