# Week 1
## Jan 29
- Thesis Proposal: Success
- Admin-ish: Set up repo and zotero and obsidian, also dicked around with Emacs (but not ready yet)
- Literature Survey
	- Set up a system for efficient note taking (need to be validated)
	- Got a goldmine of a paper [[liAutomaticTargetlessLiDAR2023]]
		- **Need to finish and continue reading from Ego Motion techniques**
	- Skimmed through [[weiOnlineLiDARcameraExtrinsic2024|ML Camera Lidar auto calib paper]]|

# Week 2
## Feb 02
- Need to write a mini section on the four types for better clarity
- Identified Radar based papers for further investigation
- Finished reading [[liAutomaticTargetlessLiDAR2023]]
## Feb 03
- Found good number of papers to read
- Keeping on reading
## Feb 04
- Slowly read papers

## Feb 05
- Installed UV, Marimo (Jupyter notebook replacement), need to try out Polars (Pandas replacement)

## Feb 06
- Not much progress

# Week 3
## Feb 09
- Making notes of calibration based review papers
## Feb 10
- Nothing of note
## Feb 11
- Focusing on fusion based review papers
- [ ] [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#Hybrid and Self-Supervised Approaches]] looks interesting #interesting
## Feb 12
## Feb 13
- Submitted proposal plan for review

# Week 4
## Feb 16
- Huggingface allows streaming
- [Tutorial for Alvis](https://github.com/c3se/alvis-intro/tree/main)
- RLCNet looks good but no code - Fundamentally does what I wanna do
- UniLion has code
## Feb 19
- Alvis/Mimer has datasets but idk if they are outdated
- Doing a beginner's guide to HPC given by chalmers
## Feb 20
- What is LSS (Lift-Splat-Shoot)?
- [Futur3D](https://tsinghua-mars-lab.github.io/futr3d/) does multimodal 3D detection
	- No idea on calibration
	- Not tested for weather resistant
- [Need to read this](UniTR: A Unified and Efficient Multi-Modal Transformer for
Bird’s-Eye-View Representation)

# Week 5
## Feb 23 - 24
- Writing the planning report
![[IMG_20260220_163239570_AE.jpg]]

![[IMG_20260223_162122895_AE.jpg]]

## Feb 25
- Mailed REVERE
- Top two fusion models from nuscenes
	- [C-L based fusion](https://github.com/hht1996ok/EA-LSS)
	- [C-L-R based fusion](https://github.com/tianweiy/CenterPoint)
- [Streaming Datasets](https://docs.mosaicml.com/projects/streaming/en/stable/getting_started/main_concepts.html)

# Week 6
## March 02
- Skimmed Nuscenes and Waymo
- Started using Marimo to make a notebook for nuscenes / dataset
- Basic documentation
## March 03
- Marimo can suck my nuts
- Debugged Jupyter notebook and UV setup
- Reading papers to identify suitable metrics'

## March 04
- [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring]]
- [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving]] -  Dint finish reading
- Working on jupyter notebook - studying nuscens

## March 06
- NuScenes does not have the weather scenes categorized

# Week 7
## March 09
- Have fun exporting all the finnicky packages from /opt for centerpoint
- I hate debugging the installation segment of packages
- Do this
```bash
yay -S gcc7
```

## March 10
- Installed GCC-7
- Fought with Centerpoint and ES_LSS

## March 11
- Friendship with .venv is over, docker is my new best friend (for now)
	- CenterPoint is built (ig)
- In the process of executing code on Centerpoint
