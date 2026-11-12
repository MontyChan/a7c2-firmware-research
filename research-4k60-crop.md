# Sony A7C II 2.01 Firmware: 4K60 Crop Research

## 1. Scope

This report examines the 4K 50p/60p full-frame versus APS-C crop conditions in
Sony ILCE-7CM2 firmware 2.01. The goal is to distinguish a menu-level crop
restriction from a sensor readout or product-capability limit.

The analysis covers the application and CP program models. It does not assume
that a format path shared by Sony cameras is usable on every model.

## 2. 4K60 Recording Profiles

The application has separate 50p/60p recording profiles for three 4K codecs:

| Format | 4K 60p record-setting profiles |
| --- | --- |
| XAVC HS | 200 Mbps 4:2:2 10-bit; 150 Mbps 4:2:0 10-bit; 100 Mbps 4:2:2 10-bit; 75 Mbps 4:2:0 10-bit; 45 Mbps 4:2:0 10-bit |
| XAVC S | 200 Mbps 4:2:2 10-bit; 150 Mbps 4:2:0 8-bit |
| XAVC S-I | 600 Mbps 4:2:2 10-bit |

The shared application model contains all three codec families, so a codec's
presence alone does not establish the A7C II's crop behavior.

## 3. Separate Full-Frame and APS-C Rules

The 4K model contains distinct full-frame and APS-C restrictions:

```text
PRM_HAITA_model_diff_ff_restriction_imager_frame_rate_in_file_format_4k
PRM_HAITA_model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
PRM_HAITA_imager_frame_size_model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
```

The associated value model includes:

```text
IMAGER_FRAME_SIZE_FULL
IMAGER_FRAME_SIZE_APSC
IMAGER_FRAME_RATE_OVER_60_50
```

These conditions are used with XAVC HS 4K, XAVC S 4K, and XAVC S-I 4K movie
settings. Separate conditions also exist for S&Q, time-lapse, and fixed-camera
framing. This is evidence of a deliberate image-frame-size/readout capability
gate, not only a menu presentation rule.

The setting model contains 50p/60p cases under both full-frame and APS-C rule
families. Their presence does not mean both choices are allowed on the A7C II;
the HAITA rules combine frame size, file format, frame rate, and model-specific
restriction values.

The 4K60 rule set is not a single unconditional “force APS-C” branch. It has
parallel full-frame and APS-C condition families for XAVC HS, XAVC S, and
XAVC S-I. The values include both ordinary 50p/60p cases and explicit
`IMAGER_FRAME_RATE_OVER_60_50` cases. This structure describes a capability
decision table; it does not by itself show that the application writes APS-C
whenever 60p is selected.

## 4. Sensor-Rate Conditions

The restrictions reference the imager frame-rate state directly:

```text
IMAGER_FRAME_RATE_OVER_60_50
```

This state appears in 4K 50p/60p conditions across XAVC HS, XAVC S, and
XAVC S-I, and in corresponding APS-C/full-frame paths. It indicates that the
firmware evaluates the sensor/readout-rate condition separately from the
selected recording frame rate.

The application also has independent controls for:

```text
SetAPSCMode
SetImageSensorBarrier
ImageSensorReadoutMode
```

These symbols show that crop mode and sensor readout are real camera-level
controls. They are not evidence that the A7C II can run full-width sensor
readout at 60 fps.

The application exports only the normal movie-parameter interface
`SetMovieRecParam`; the APSC and sensor-barrier names appear in internal model
and firmware strings rather than as independent public dynamic symbols. The
4K60 parameter path therefore reaches a compound movie-parameter operation,
not a standalone crop toggle.

## 5. HDMI Output Is a Separate Constraint

The HDMI 4K output model contains its own APS-C and frame-rate restrictions:

```text
PRM_HAITA_hdmi_4k_outpute_apsc_restriction
PRM_setting_rec_media_during_hdmi_output
```

The registered conditions include 4K 50p/60p, movie exposure mode, internal
recording disabled, and imager frame rate over the 60/50 threshold. HDMI output
restrictions must be analyzed separately from internal 4K recording crop rules.

## 6. Assessment

The firmware contains real, separate full-frame and APS-C policy branches for
4K recording. The presence of these branches supports the conclusion that crop
selection is tied to sensor readout capability or model capability, rather than
being solely a UI toggle.

For ILCE-7CM2, the most plausible explanation for 4K60 crop is a product/readout
limit: the sensor cannot provide the full-width readout at the required rate
under the camera's thermal and processing budget, while APS-C readout reduces
the data path. Static firmware evidence alone cannot prove the physical limit
or identify a software-only exception.

The firmware contains a full-frame branch in its shared model, but that branch
may be intended for other Sony bodies. It should not be treated as evidence that
the A7C II can record full-frame 4K60 after a menu or parameter change.

The current static evidence is consistent with a readout-bandwidth limit: the
same 4K60 frame-rate condition is evaluated against both image-frame size and
sensor readout state, while the actual movie parameter is submitted through one
compound `SetMovieRecParam` path. A patch would need to alter the model decision,
the sensor-mode selection, and possibly the downstream sensor/encoder timing;
changing only an APS-C condition would not prove full-frame capture.

## 7. Current Conclusion

For firmware 2.01, the following are confirmed:

1. XAVC HS, XAVC S, and XAVC S-I have separate 4K 50p/60p recording profiles.
2. Full-frame and APS-C crop restrictions are modeled independently.
3. The rules reference sensor frame-rate state, file format, shooting mode, and
   crop size.
4. HDMI output has a separate set of 4K60 and crop restrictions.
5. The shared firmware contains full-frame branches, but they are not proven to
   apply to the ILCE-7CM2.

The current evidence does not establish a software-only method to remove the
A7C II's 4K60 crop. Given the explicit imager-rate and frame-size conditions,
the restriction is more likely a sensor/readout or product capability limit
than a hidden menu option.

## 8. What Would Change This Assessment

The next useful evidence would be a model-specific runtime result for:

```text
imager_frame_size
imager_frame_rate
imager_frame_rate_in_file_format_4k
model_diff_ff_restriction_imager_frame_rate_in_file_format_4k
model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
```

The current Service USB inspector does not expose these computed HAITA values.
They would require locating a verified read-only runtime getter or reconstructing
the relevant model-rule evaluation path. Until then, no program or setting
change should be treated as a safe crop unlock.

## 9. Version Scope

```text
Model: Sony ILCE-7CM2
Firmware: 2.01
```

Do not apply offsets, enum values, or conclusions from this report to another
model or firmware version.
