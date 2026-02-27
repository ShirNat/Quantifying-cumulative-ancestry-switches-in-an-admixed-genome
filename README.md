# Quantifying cumulative ancestry switches in an admixed genome

For more information about our research please refer to our work titled ["Analytical expectations for ancestry junction accumulation in admixed genomes"](https://www.biorxiv.org/content/10.1101/2025.10.28.685223v2.full.pdf)

Below we will describe the files included in this repository

## Parameter dymanics:
1. You can look at the parameter dymanics of Equation 3 via the file `"parameter_dynamics/main_param_dynamics.ipynb"`
  * This will output Figure 1 (main text) if you set `final_g = 50` and Figure S1 (supplemental text) if  you set `final_g = 500`
2. You can look at the parameter dymanics of Equation 2 via the file `"parameter_dynamics/supp_param_dynamics_per_gen.ipynb"`
  * This will output Figure S2 (supplemental text)
    
## Simulated framework and ancestry switch estimation
### Getting tree sequences from SLiM
#### Constant recombination:
1. SLiM simulation files are located in `"simulations/slim_scripts"`
2. You can run the SLiM files (with replicates) via the file `“simulations/constant_recomb_run_slim_reps.ipynb”`
    * The SLiM simulations will output tree sequences files in `“simulations/tree_outputs/constant_recomb”`
#### Variable recombination (i.e. using recombination maps):
1. You generate a simple recombination map using the file `“simulations/generate_recomb_map.ipynb”`
    * This will output a text file called `“simple_recomb_map.txt”`, which will be used for the simulations and theoretical calculations.
    * NOTE: The seed could not be recovered for the recombination map used for our actual analysis. To replicate our exact pipeline please use file `“simple_recomb_map_used_in analysis.txt”.`
2. SLiM simulation files are located in `“simulations/slim_scripts”`
3. You can run the SLiM files (with replicates) via the file `“simulations/recomb_map_run_slim_reps.ipynb”`
    * SLiM will output tree sequences files in  `“simulations/tree_outputs/recomb_map”`

### Processing tree sequences and extracting the number of switches
1. You can process the `.tree` files by running `“simulations/sim_switch_analysis_reps.sh”` 
    * This will output `.csv` files for each generation of each replicate in either `“tree_outputs/constant_recomb“` or `“obs_switches/recomb_map“`
    * NOTE: both the constant recombination case and the variable recombination case can be run with the same file, but you must specify the path names correctly. See comments in script for more details.
  
### Calculating the expected number of switches from theory
#### Constant recombination:
1. You can calculate the theoretical switch count using the file `“simulations/constant_recomb_theory_exp.ipynb”`
    * This will output a single `.csv` file in `“simulations/exp_switches/constant_recomb”`
#### Variable recombination (i.e. using recombination maps):
1. You can calculate the theoretical switch count using the file `“simulations/recomb_map_theory_exp.ipynb”`
    * This will output a single `.csv` file in `“simulations/exp_switches/recomb_map”`
  
### Comparing simulated and empirical switch counts
1. You can compare the number of switches for both the constant recombination case and the variable recombination case (i.e. using recombination maps) via the file `"simulations/main_switches_cases_pop_sizes.ipynb"`
    * This will output Figure 3 (main text)
2. You can compare results for the number of switches for populations of different sizes ($N_e = [100, 1000, 10000]$) via the file `"simulations/main_switches_cases_pop_sizes.ipynb"`
    * This will output Figure S3 (supplemental text) for the constant recombination case and Figure S4 (supplemental text) for the variable recombination case (i.e. using recombination maps)

## Application to African American populations
### Calculating the expected number of switches from empirical data
#### Inferring local ancestry with FLARE:
the relative path is `"empirical/empirical_predictions/local_ancestry_infer/*"`
1. `“config.yaml”` contains a list of the admixed populations and filepaths to their reference populations
2. `“GRCh38_Map.zip”` contains the genetic map used in FLARE calls
3. `“refPanels.zip”` contains reference panels for each population created using the inds in the files listed in the config
4. `“Snakefile”` is the pipeline file
#### Calling ancestry tracts from FLARE
the relative path is `"empirical/empirical_predictions/calling_ancestry_tracts/*"`
1. `“submit_get_anc_runs.sh”` calls `“get_anc_runs.sh”` and then  `“combines_anc_runs.sh”`
2. `“get_anc_runs.sh”` takes in the FLARE data generated when inferring local ancestry and calls `“get_anc_runs.R”` to create a file of nonoverlapping ancetry tracts per haplpotype, per population
#### Analyzing switch counts
the relative path is `"empirical/empirical_predictions/analyzing_switch_counts/*"`
1. `“analyze_anc.Rmd”` takes in the ancestry tracts generated from FLARE data as well as files that identify the unrelated individuals to generate filtered switch counts
2. `“Rmd_auxiliary.R”` contains some function that`“analyze_anc.Rmd”` uses

## Theoretical switch counts (relative path :
the relative path is `"empirical/theoretical_predictions/*"`
1. You can get theoretical switch counts for parameters estimated for chromosome 1 via the file `"main_theoretical_switches_multi_case.ipynb"`
    * This will output Figure 4 (main text)
2. You can get theoretical switch counts for all autosomes via the file `"supp_theoretical_switches_multi_case.ipynb"`
    * This will output the information present in Table S1 (supplemental text)
