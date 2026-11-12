# Sony A7C II 2.01 Firmware: 4K 120p / 100p Research

## 1. Scope

This report examines the 4K 120p and 100p recording paths in Sony ILCE-7CM2
firmware 2.01, with emphasis on codec profiles, license and capability gates,
sensor crop/readout conditions, and product-specific restrictions.

The analysis covers the application program and CP program. It does not assume
that a shared Sony firmware path is supported by every camera model that
contains it.

## 2. Recording Profiles in the Application Model

The application has 4K 120p/100p frame-rate settings for both XAVC HS and
XAVC S:

```text
setting_movie_rec_frame_rate_xavc_hs_4k_REC_FRAME_RATE_120P
setting_movie_rec_frame_rate_xavc_hs_4k_REC_FRAME_RATE_100P
setting_movie_rec_frame_rate_xavc_s_4k_REC_FRAME_RATE_120P
setting_movie_rec_frame_rate_xavc_s_4k_REC_FRAME_RATE_100P
```

The corresponding record-setting profiles include:

| Format | 120p / 100p profiles |
| --- | --- |
| XAVC HS 4K | 280 Mbps 4:2:2 10-bit; 200 Mbps 4:2:0 10-bit |
| XAVC S 4K | 280 Mbps 4:2:2 10-bit; 200 Mbps 4:2:0 8-bit |

The same 120/100 fps values occur in the S&Q model. Their presence in the
recording enums proves that the shared application framework describes these
modes; it does not prove that the ILCE-7CM2 accepts them.

## 3. Independent Availability and License Gates

4K 120p/100p uses two distinct capability parameters:

```text
PRM_frame_rate_4k_120fps_100fps_availability
PRM_license_type_4k120p_available
```

The frame-rate availability parameter has `AVAILABLE` and `UNAVAILABLE` values.
The license-type parameter has three states:

```text
LICENSE_TYPE_4K120P_AVAILABLE
LICENSE_TYPE_4K120P_NOT_AVAILABLE
LICENSE_TYPE_4K120P_NOT_SUPPORT
```

The application also tracks general license state and evaluates it together
with the selected file format:

```text
PRM_license_state
PRM_HAITA_license_state_license_type_4k120p_available_setting_file_format
PRM_HAITA_license_state_license_type_4k120p_available_setting_file_format_pal
```

The model contains license-state cases for XAVC HS 4K, XAVC S 4K, XAVC S HD,
XAVC S-I 4K, XAVC S-I HD, and XAVC S-I DCI 4K. PAL-specific handling is also
present. Thus a 4K 120p menu item depends on both rate availability and the
license/product state; these are not represented by one Boolean.

The firmware defines ten application license slots:

```text
BKID_APP_LICENSE_TYPE0 ... BKID_APP_LICENSE_TYPE9
BKID_APP_EXPIRED_LICENSE_STATUS0 ... BKID_APP_EXPIRED_LICENSE_STATUS9
```

This confirms that license information has a persistent representation in the
application model. The current static analysis has not mapped the 4K120p license
type to a particular slot or determined how those slots are authenticated.

## 4. Sensor Readout, Crop, and Lens Conditions

The 4K mode checks distinguish full-frame and APS-C sensor-frame cases:

```text
PRM_HAITA_model_diff_ff_restriction_imager_frame_rate_in_file_format_4k
PRM_HAITA_model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
PRM_HAITA_imager_frame_size_model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
```

The value model includes separate full-frame and APS-C conditions for 120p and
100p, as well as `IMAGER_FRAME_RATE_OVER_60_50` and
`IMAGER_FRAME_RATE_OVER_120_100` states. This indicates that the firmware
evaluates sensor readout rate and crop mode alongside the nominal output rate.

The application also defines:

```text
PRM_LensPowerExclusionFactor4K8K
PRM_HAITA_setting_file_format_LensPowerExclusionFactor4K8K_direct_rec
```

This is evidence of lens/power-related exclusions for high-resolution and
high-frame-rate recording. The 4K120 path may therefore depend on the selected
lens or a power/drive capability, not only the image-sensor mode.

## 5. Product-Specific Rules

The 4K120 checks are composed from multiple HAITA conditions involving:

```text
shooting mode
file format
frame rate
full-frame or APS-C image-frame size
sensor readout-rate state
Feature Manager system architecture
license state
NTSC/PAL selector
```

The function-name model contains separate APS-C and full-frame restrictions.
The available strings alone do not show which branch the ILCE-7CM2 selects.

The CP image does not expose a matching plain-text 4K120 setting table. This
does not rule out CP involvement; the CP-side mode and timing checks may use
numeric data or generated structures.

The CP image does contain a display/output capability entry for:

```text
DCI4K 120hz YCC420 8Bit
```

This confirms that the CP-side video framework knows about at least one 120 Hz
DCI 4K output profile. It is not proof that the A7C II sensor can generate that
profile for internal movie recording.

## 6. Interpretation

The firmware has a broad shared 4K120/100p model, including XAVC HS and XAVC S
recording profiles. It also has separate license, frame-rate availability,
sensor-readout, crop, and lens/power conditions.

This is a plausible software-gate research target, but the main unresolved
question is the ILCE-7CM2 result for the capability and license parameters:

```text
NOT_SUPPORT
```

would indicate a model or hardware exclusion, while:

```text
NOT_AVAILABLE
```

could indicate a license or product-condition gate. The strings and setting
enums cannot reveal the runtime result by themselves.

No conclusion is made that 4K 120p can be enabled on the A7C II. A firmware
patch that only exposes the menu could bypass the checks for sensor readout,
thermal behavior, lens/power limits, or recording stability.

## 7. Next Static-Analysis Targets

```text
Initialization of PRM_frame_rate_4k_120fps_100fps_availability
Initialization of PRM_license_type_4k120p_available
The ILCE-7CM2 product branch for full-frame and APS-C restrictions
The source of IMAGER_FRAME_RATE_OVER_120_100
The mapping from license slots to LICENSE_TYPE_4K120P
The consumer of LensPowerExclusionFactor4K8K
```

The first useful result would be the actual capability state for ILCE-7CM2,
followed by the code path that produces it. If it is `NOT_SUPPORT`, the
investigation should focus on sensor/encoder limits rather than removing a
menu condition.

## 8. Version Scope

```text
Model: Sony ILCE-7CM2
Firmware: 2.01
```

Do not apply offsets, enum values, or conclusions from this report to another
model or firmware version.
