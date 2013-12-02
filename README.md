question-analyzer
=================

Question Analyzer is the first module of our developing closed domain question answering system for Turkish. We try to apply the techniques employed in IBM Watson to Turkish.

It uses the dependency parser developed in Istanbul Technical University by Eryiğit et al. [http://acl.ldc.upenn.edu/E/E06/E06-1012.pdf].

After parsing the question, we apply the first line of detection, that is the baseline rules to extract the focus, LAT and QClass. Then the statistical part starts.

Both rules and statistical models create for each question a score for focus, LAT and QClass (for each word - class for QClass), then the highest scores for both three metadata win, and produced in a useful manner, such that the upcoming parts of the system (information retrieval, answer generation etc.) can benefit from it.

Will include:
- Focus detector
- LAT (Lexical Answer Type) detector
- Question Classifier
