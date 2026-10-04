# Fix loop diagnosis
## Weakest gate
Opening accuracy cannot be evaluated because the source repository contains no measured opening ground truth.

## Root cause
The current MVP detects wall candidates but has no opening detector or physical labels.

## Predicted improvement
Adding wall-gap/opening candidate extraction and an evaluator should make the failure observable and reproducible; it cannot establish the 2 cm gate without measurements.
