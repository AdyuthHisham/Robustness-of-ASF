# Metamorphic Object Insertion for Testing Object Detection Systems (MetaOD)

#ReferPaper #corruption/camera/metamorphic

Wang, Su (HKUST / ETH Zurich). ASE '20.

## Contribution

MetaOD: black-box metamorphic testing for 2D object detectors via **compositional image mutation** — extracting real object instances (via YOLACT) and inserting them into background images at strategically chosen non-overlapping locations, then checking that predictions on *pre-existing* objects stay unchanged. Tested on 4 commercial APIs (Amazon Rekognition, Google AutoML, Microsoft Azure, IBM Vision) + 4 TensorFlow models (SSD Mobilenet/Inception, Faster-RCNN Resnet/Inception-Resnet).

## Method detail

Two insertion strategies compared: **random** (uniform non-overlapping placement) vs. **guided** (placed in a region symmetric about a randomly chosen existing object) — guided insertion found substantially more errors in a pilot study (2,529 vs. 1,454 errors across 8 detectors on the same 50-image, 14,850-synthetic-image set). A "relocation" step (delta-debugging-style, progressively moving a bug-triggering object toward the scene's object centroid) then generates additional diverse failure-preserving test images — 32.4% of all error-causing images came from this relocation step alone.

## Key findings

- **292,206 synthetic images generated, 38,345 triggered erroneous detections (13.1% overall trigger rate)**, ranging 10.5% (Faster-RCNN Resnet) to 15.6% (Amazon Rekognition) per detector.
- Naturalness (HOG-intersection similarity to real images): 98.0–98.9% across all detectors — synthetic images are visually indistinguishable from real composites by this metric, versus <50% for random unrelated image pairs.
- Only "recognition failures" (missed/false objects) were found on manual inspection of a ~800-image spot-check — no classification or localization failures observed, though the check wasn't exhaustive.
- Retraining case study (SSD MobileNet on Berkeley DeepDrive): retraining on *verified bug-triggering* synthetic images improved mAP 9.3→10.5 (+1.2), while retraining on *unverified/arbitrary* synthetic images actually **hurt** performance (→8.6) — a caution against naive synthetic-data augmentation without a failure-triggering filter.

## Relevance to AMSCUP

A camera-domain, semantic/compositional analog to this project's pixel-level corruption approach — MetaOD perturbs scene *content* (what objects are present and where), not sensor *signal* (noise, dropout, blur). Useful as a template if this project ever extends beyond physical-sensor-noise corruption into content-level test generation, and as evidence that verified-failure-only retraining outperforms blanket synthetic augmentation — relevant to how this project should approach any future retraining-on-corrupted-data experiment.

## Limitations acknowledged

Object-similarity selection is pixel-level (image hashing) only, not semantic — flagged by the authors as a known gap; inserted objects are only resized (not rotated/blurred/relit) to preserve realism, at the cost of transformation diversity; commercial detector internals are undisclosed, so failure causes can only be black-box-speculated.

## Source

- `docs/lit_survey/noise_addition/markdown/metamorphic_object_insertion.md` (477 L)
