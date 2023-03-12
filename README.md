# Basketball Agent

This is an attempt at a statistically accurate basketball environment (using stats from nba).

To use (if not using the default csvs), CSVs with the following are required:

- AttackPlayer csvs:
	- columns needed are: 
		 - fgp_three_point 
		 - fgp_midrange 
		 - fgp_paint, fgp_restricted_area 
		 - oreb 
		 - ftp 
		 - pass_box_1_2 
		 - pass_box_1_3
		 -  ...
		 - pass_box_5_4 (i.e. probability of making a pass from one region to another for all regions)
- DefendPlayer csvs:
	-   columns needed are:
		- dreb
		- stlp
		- blkp
		- foulp
- Coefficient csvs:
	- columns needed are:
		- shot_clock
