Recommend metrics and graphs for answering the following questions

This is data I have with me
Each row in the visibility parquet is one object-in-one-frame observation, uniquely keyed by
  sequence_id + frame_idx + obj_tracking_id. It carries the object's raw geometry (class, position,
  orientation, dimensions, distance to ego) alongside per-sensor visibility results for all five
  sensors — radar (FOV/range gating plus a sparsity score), two LiDARs at 64- and 128-channel
  resolution (point count and sparsity), and four cameras front/left/right/rear (projected 2D centroid
  and a visibility score) — each contributing a *_visible boolean and sensor-specific quality metric.
  It closes with cross-sensor aggregates (num_sensors_visible, primary_sensor) and scene context
  (weather, environment, time_of_day, frame_object_count, ghost_flag, occluded), so the table lets you
  query how visible any given object was, sensor by sensor, under any environmental condition.

Questions:
1. When does corruptiion induced prediction increase compared to original data
2. How does the corruption affect the prediction when there are multipe objects in a frame
3. I want to do a comparitive study, when is prediction accuracy increasin and decreasing and when is there false detections etc
4. Does frame deletion impact the prediction? I need to check it out on a sequence of frames
5. Which frames and corruptions have max and minimum false predictions and missing predictions
6. In some corrupted inference 90% of the predictions would not have been predicted but one or two has been predicted. Any reason why certain labels or stuff gets identified even though everything else was left out.
7. Even if some sensors have complete loss the model still predicts. Need to check out the lavel of degredation and how it affects each label
8. Some predictions predict the GT which the original prediction did not. Need to identify these cases.
9. Which sensors affects the model the most when it is all zero
