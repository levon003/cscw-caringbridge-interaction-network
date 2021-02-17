Patterns of Patient and Caregiver Mutual Support Connections in an Online Health Community 
---

Repository for analysis code related to a Spring 2019 study investigating interactions between patient and caregiver authors on CaringBridge.org.

Originally submitted to CSCW in January 2020, revised June 2020, and conditionally accepted July 2020 for presentation at CSCW 2020 in October 2020.

As described in the paper, CaringBridge data used for analysis is not being released publicly for ethical reasons.

For any questions or additional information, contact the corresponding author: levon003@umn.edu

Paper: https://dl.acm.org/doi/abs/10.1145/3434184

Preprint: https://arxiv.org/abs/2007.16172

Author website: https://z.umn.edu/zlevonian

## Code Organization

Generally, each folder contains a mostly independent analysis.  Minimal effort has been made to tidy things up.

Some code makes use of functions or utilities in another repository: https://github.com/levon003/icwsm-cancer-journeys

Folders and a brief description:
 - `author_initiations` - All of the initiations code, including all (?) of the models for RQ1. Includes scripts for producing the features expected by the mlogit models.
 - `author_type` - All of the author role classification of CaringBridge users and sites. Notably, the `AuthorTypeClassification-New` notebook contains an implementation of [Black Box Shift Correction](https://arxiv.org/abs/1802.03916) (as `bbsc_clf` in the sklearn classification pipeline).
 - `build_network` - Exploratory work to build the interaction network.  Generally discarded in favor of other approaches.
 - `data_pulling` - Scripts for data processing and management, but also notebooks for survival analysis, as seen in Ruyuan Wan's CSCW'20 poster. For building the network data, `FilterAndMergeExtractedInteractions` does all the relevant merging, and includes some additional visualizations of users interaction tendencies. Subfolder `sa_poster_figures` has figures for the survival analysis poster (they probably should have been put in the top-level figures directory).
 - `data_selection` - Core notebooks for selecting valid authors, esp. `CandidateDataSelection-New`.
 - `dyad_growth` - A lot of the interaction network stuff here, as well as the most important notebook in the repo: `UserUserDyadDistributions-Demonstration`. This notebook should not be here, but it includes a lot of stuff, including some RQ2 models.
 - `figures` - generic output directory for many of the figures in the paper, in PDF format.
 - `geographic_analysis` - Code that generates US-state-assignments for valid authors, by using the recorded IP addresses on guestbooks and journal updates.
 - `visualization` - Author tenure analysis and figure in `AuthorTenure`. I think basically nothing else is relevant in this folder. (One interesting thing: our attempts to do "session"-centric analysis on CaringBridge basically failed; inter-activity times don't show clear evidence of sessions. Many (most?) authors come to CaringBridge on a fairly fixed schedule, which either suggests a lack of responsiveness to notifications or responding exclusively off-platform e.g. reading guestbooks via email.) Also a script to generate a pointless video breaking down users by their types of interactions on CaringBridge: https://youtu.be/tmRRubHZqDo

## Citing

The ACM reference is:

Zachary Levonian, Marco Dow, Drew Erikson, Sourojit Ghosh, Hannah Miller Hillberg, Saumik Narayanan, Loren Terveen, and Svetlana Yarosh. 2021. Patterns of Patient and Caregiver Mutual Support Connections in an Online Health Community. Proc. ACM Hum.-Comput. Interact. 4, CSCW3, Article 275 (December 2020), 46 pages. DOI:https://doi.org/10.1145/3434184

Bibtex:

```
@article{levonian_patterns_2020,
    author = {Levonian, Zachary and Dow, Marco and Erikson, Drew and Ghosh, Sourojit and Miller Hillberg, Hannah and Narayanan, Saumik and Terveen, Loren and Yarosh, Svetlana},
    title = {Patterns of Patient and Caregiver Mutual Support Connections in an Online Health Community},
    year = {2021},
    issue_date = {December 2020},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    volume = {4},
    number = {CSCW3},
    url = {https://doi.org/10.1145/3434184},
    doi = {10.1145/3434184},
    abstract = {Online health communities offer the promise of support benefits to users, in particular because these communities enable users to find peers with similar experiences. Building mutually supportive connections between peers is a key motivation for using online health communities. However, a user's role in a community may influence the formation of peer connections. In this work, we study patterns of peer connections between two structural health roles: patient and non-professional caregiver. We examine user behavior in an online health community---CaringBridge.org---where finding peers is not explicitly supported. This context lets us use social network analysis methods to explore the growth of such connections in the wild and identify users' peer communication preferences. We investigated how connections between peers were initiated, finding that initiations are more likely between two authors who have the same role and who are close within the broader communication network. Relationships---patterns of repeated interactions---are also more likely to form and be more interactive when authors have the same role. Our results have implications for the design of systems supporting peer communication, e.g. peer-to-peer recommendation systems.},
    journal = {Proc. ACM Hum.-Comput. Interact.},
    month = jan,
    articleno = {275},
    numpages = {46},
    keywords = {network analysis, online health communities, social support}
}
```

