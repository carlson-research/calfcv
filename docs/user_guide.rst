User Guide
==========

Overview
--------

``calfcv`` implements the Coarse Approximation Linear Function (CALF) algorithm integrated with Cross-Validation.

Mathematical Background
-----------------------

Instead of optimizing continuous weights via gradient descent or :math:`L_1 / L_2` shrinkage penalties, ``calfcv`` uses a greedy step-forward selection routine that assigns discrete weight values (:math:`\{-1, 0, 1\}`) to selected variables, optimizing target metrics such as the AUC-ROC or :math:`t`-statistic directly.