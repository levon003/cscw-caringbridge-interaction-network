Patterns of Patient and Caregiver Mutual Support Connections in an Online Health Community 
---

Repository for analysis code related to a Spring 2019 study investigating interactions between patient and caregiver authors on CaringBridge.org.

Originally submitted to CSCW in January 2020, revised June 2020, and conditionally accepted July 2020 for presentation at CSCW 2020 in October 2020.

As described in the paper, CaringBridge data used for analysis is not being released publically for ethical reasons.

For any questions or additional information, contact the corresponding author: levon003@umn.edu

Preprint: https://arxiv.org/abs/2007.16172

Author website: https://z.umn.edu/zlevonian

## Code Organization

Generally, each folder contains a mostly independent analysis.  Minimal effort has been made to tidy things up.

Some code makes use of functions or utilities in another repository: https://github.com/levon003/icwsm-cancer-journeys

Folders and a brief description:
 - `author_initiations` - All of the initiations code, including all (?) of the models for RQ1. Includes scripts for producing the features expected by the mlogit models.
 - `author_type` - All of the author role classification of CaringBridge users and sites.
 - `build_network` - Exploratory work to build the interaction network.  Generally discarded in favor of other approaches.
 - `data_pulling` - Scripts for data processing and management, but also notebooks for survival analysis, as seen in Ruyuan Wan's CSCW'20 poster. For building the network data, `FilterAndMergeExtractedInteractions` does all the relevant merging, and includes some additional visualizations of users interaction tendencies. Subfolder `sa_poster_figures` has figures for the survival analysis poster (they probably should have been put in the top-level figures directory).
 - `data_selection` - TODO
 - `dyad_growth` - TODO
 - `figures` - generic output directory for many of the figures in the paper, in PDF format.
 - `geographic_analysis` - TODO
 - `visualization` - TODO

