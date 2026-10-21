# IrisFlow

An experiment in making an ordinary webcam useful as a desktop input device.

## The idea

Looking at something and acting on it are different steps. IrisFlow explores gaze-assisted reading and pointer movement, with deliberate gestures to trigger actions.

## What is built

- A reading line and optional focus masks that follow estimated gaze.
- Gaze-to-pointer jumps with blink or keyboard triggers, plus a second deliberate gesture to click.
- Per-user calibration, recentering and warnings when head position changes.
- Accuracy checks and guarded adaptation from ordinary mouse clicks.

The prototype uses Python and MediaPipe face/iris landmarks, a calibrated gaze model, smoothing and blink handling. Tracking runs locally; normal operation does not store camera images. Optional developer recording is a separate, explicit feature.

## Where it stands

IrisFlow is an experimental webcam-gaze prototype. Calibration, camera conditions, head movement and drift remain central reliability questions. It is not a validated replacement for a dedicated eye tracker or an established assistive technology.

The next focus is measuring when tracking is uncertain and making interaction behave safely around that uncertainty.
