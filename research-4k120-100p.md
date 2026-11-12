# Sony A7C II 2.01 Firmware: 4K 120p / 100p Research

## 1. Scope

This report examines the 4K 120p and 100p recording paths in Sony ILCE-7CM2
firmware 2.01, focusing on codec profiles, license states, system architecture,
sensor readout, and crop restrictions.

The analysis covers the application and CP program models. Shared Sony firmware
paths are not assumed to be supported by every camera model that contains them.

## 2. Recording Profiles

The application defines 4K 120p/100p settings for both XAVC HS and XAVC S:

```text
setting_movie_rec_frame_rate_xavc_hs_4k_REC_FRAME_RATE_120P
setting_movie_rec_frame_rate_xavc_hs_4k_REC_FRAME_RATE_100P
setting_movie_rec_frame_rate_xavc_s_4k_REC_FRAME_RATE_120P
setting_movie_rec_frame_rate_xavc_s_4k_REC_FRAME_RATE_100P
```

The corresponding record-setting profiles are:

| Format | 120p / 100p profiles |
| --- | --- |
| XAVC HS 4K | 280 Mbps 4:2:2 10-bit; 200 Mbps 4:2:0 10-bit |
| XAVC S 4K | 280 Mbps 4:2:2 10-bit; 200 Mbps 4:2:0 8-bit |

The same frame rates are present in the S&Q model. Their presence proves that
the shared application framework describes these modes, not that ILCE-7CM2 can
execute them.

The CP image contains a separate output profile named:

```text
DCI4K 120hz YCC420 8Bit
```

This proves that the CP-side video framework knows about at least one 120 Hz
DCI 4K output profile. It does not prove that the A7C II sensor can generate
that profile for internal recording.

## 3. Availability and License Gates

The firmware defines two separate 4K120 capability parameters:

```text
PRM_frame_rate_4k_120fps_100fps_availability
PRM_license_type_4k120p_available
```

The frame-rate parameter has:

```text
FRAME_RATE_4K_120FPS_100FPS_AVAILABILITY_UNAVAILABLE
FRAME_RATE_4K_120FPS_100FPS_AVAILABILITY_AVAILABLE
```

The license parameter has three states:

```text
LICENSE_TYPE_4K120P_NOT_AVAILABLE
LICENSE_TYPE_4K120P_AVAILABLE
LICENSE_TYPE_4K120P_NOT_SUPPORT
```

The firmware also evaluates:

```text
PRM_license_state
PRM_HAITA_license_state_license_type_4k120p_available_setting_file_format
PRM_HAITA_license_state_license_type_4k120p_available_setting_file_format_pal
```

The license-state rules cover XAVC HS 4K, XAVC S 4K, XAVC S HD, XAVC S-I 4K,
XAVC S-I HD, and XAVC S-I DCI 4K. PAL-specific conditions are also present.

The application contains ten license slots and matching expired-license status
slots:

```text
BKID_APP_LICENSE_TYPE0 ... BKID_APP_LICENSE_TYPE9
BKID_APP_EXPIRED_LICENSE_STATUS0 ... BKID_APP_EXPIRED_LICENSE_STATUS9
```

The current static analysis does not identify which slot carries the 4K120p
entitlement or how Sony authenticates the slot contents.

## 4. System Architecture Gate

The Feature Manager defines these system architectures:

```text
SYSTEM_ARCHITECTURE_IPSX
SYSTEM_ARCHITECTURE_ASTRA
SYSTEM_ARCHITECTURE_ARGO
```

The 120p/100p HAITA rules explicitly combine the selected recording format and
frame rate with `FEATURE_MANAGER_system_architecture`. Among the registered
conditions are branches equivalent to:

```text
120P XAVC HS 4K ... TYPE_SYSTEM_ARCHITECTURE_ARGO
100P XAVC HS 4K ... TYPE_SYSTEM_ARCHITECTURE_ARGO
120P XAVC S 4K ... TYPE_SYSTEM_ARCHITECTURE_ARGO
100P XAVC S 4K ... TYPE_SYSTEM_ARCHITECTURE_ARGO
```

This is the strongest restriction found so far. It indicates that at least part
of the 4K 120/100p path is designed specifically for the ARGO architecture.
The A7C II application resources use the `IPSX` family (`image_*_IPSX.uxc`),
which is consistent with the ILCE-7CM2 application architecture being IPSX.
This is indirect evidence from the resource family, not a direct read of the
Feature Manager enum. It makes the ARGO-specific 4K120 branch unlikely to
apply to the A7C II.

The available Service USB snapshot returns persistent BK4 settings, not runtime
Feature Manager parameters. In the inspected ELF dynamic symbol table, the only
defined application entry is `Application_System_Init`; no exported getter for
`system_architecture` or `imager_model` is available through the current probe
interface. The firmware contains the source-name string
`feature_manager::update_product_model()`, but the binary does not retain a
normal symbol for that routine. Reading the exact enum would require
reconstructing its internal AArch64 data flow and ABI before a native probe
could be considered.

## 5. Sensor Readout and Crop Restrictions

The application has separate full-frame and APS-C restrictions:

```text
PRM_HAITA_model_diff_ff_restriction_imager_frame_rate_in_file_format_4k
PRM_HAITA_model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
PRM_HAITA_imager_frame_size_model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
```

The corresponding conditions include:

```text
IMAGER_FRAME_RATE_OVER_60_50
IMAGER_FRAME_RATE_OVER_120_100
IMAGER_FRAME_SIZE_FULL
IMAGER_FRAME_SIZE_APSC
```

These branches are used with XAVC HS 4K, XAVC S 4K, XAVC S-I 4K, S&Q, and
time-lapse settings. The firmware therefore checks sensor readout and image
frame size in addition to the nominal recording frame rate.

Other high-frame-rate restrictions reference:

```text
PRM_LensPowerExclusionFactor4K8K
```

This suggests that lens/power behavior may also participate in high-resolution
and high-frame-rate exclusions.

## 6. What the Evidence Means

The 4K 120/100p path is not one simple hidden switch. It is a conjunction of:

```text
frame-rate availability
license type
license state
system architecture
full-frame or APS-C image size
sensor readout rate
file format
NTSC/PAL conditions
lens/power exclusions
```

The most important distinction is:

```text
NOT_AVAILABLE
```

versus:

```text
NOT_SUPPORT
```

If ILCE-7CM2 returns `NOT_SUPPORT`, the limitation is a product or hardware
capability decision. If it returns `NOT_AVAILABLE`, a license or product gate
may be involved. Even in the latter case, the ARGO architecture and sensor
readout conditions could still block the recording path.

## 7. Current Conclusion

For firmware 2.01, the following are confirmed:

1. The application contains XAVC HS and XAVC S 4K 120p/100p recording models.
2. 4K 120p/100p has separate availability and license parameters.
3. The firmware contains ten application license slots and expired-license
   status slots.
4. 120p/100p restrictions explicitly use system architecture conditions.
5. APS-C/full-frame and sensor-readout restrictions are part of the path.
6. The CP model contains at least one DCI 4K 120 Hz output profile.

The static evidence does not show that A7C II 4K 120/100p is a simple hidden
software feature. The ARGO-specific branches, combined with the A7C II's IPSX
resource family, make a product/system-architecture restriction more likely
than a missing menu flag. The current evidence still does not directly read the
ILCE-7CM2 Feature Manager enum or its final license result.

## 8. Required Runtime Values

To classify the restriction, a read-only native probe must return:

```text
imager_model
product_concept
system_architecture
license_state
license_type_4k120p_available
frame_rate_4k_120fps_100fps_availability
```

The current read-only inspector does not return these runtime values. No native
probe was executed because the getter address and ABI are not established.
Without them, changing the menu or guessing a license slot would not establish
whether the feature is supported. The IPSX-to-ARGO mismatch is a strong
inference from the resource family and registered HAITA branches, not a
directly measured Feature Manager result.

## 9. Version Scope

```text
Model: Sony ILCE-7CM2
Firmware: 2.01
```

Do not apply offsets, enum values, or conclusions from this report to another
model or firmware version.
