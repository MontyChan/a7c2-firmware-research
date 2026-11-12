# Sony A7C II 2.01 Firmware: HDMI RAW Output Research

## 1. Scope

This report examines the HDMI RAW-output path in Sony ILCE-7CM2 firmware 2.01.
The focus is whether the firmware contains a complete external RAW recording
path, what conditions gate it, and which parts belong to the application or CP
video pipeline.

The analyzed objects are:

```text
/usr/lib/appFw.so
/cp/cpapp-b.bin
```

This is static firmware research. The presence of a code path does not prove
that the A7C II hardware supports every mode represented by the shared Sony
framework.

## 2. Application-Level Evidence

The application contains an explicit external RAW output operation:

```text
PID_SET_RAW_EXTERNAL_OUTPUT
```

The RAW-output parameter model includes:

```text
PRM_setting_raw_output
PRM_setting_raw_output_frame_rate
PRM_setting_raw_output_connect_with_raw_compatible_device
PRM_hdmi_connect_state_connect_with_raw_compatible_device
PRM_raw_output_framerate_restriction
PRM_setting_color_gamut_for_raw_out_setting_raw_output_connect_with_raw_compatible_device
```

This is a complete state model rather than a single menu label. It explicitly
tracks the RAW-output switch, frame rate, compatible-device connection, HDMI
connection state, frame-rate restrictions, and color-gamut selection.

The application also models recording while HDMI output is active:

```text
PRM_setting_rec_media_during_hdmi_output_setting_raw_output_exposure_mode
PRM_setting_rec_media_during_hdmi_output_setting_raw_output_connect_with_raw_compatible_device_exposure_mode
PRM_setting_rec_media_during_hdmi_output
PRM_HAITA_setting_rec_media_during_hdmi_output_setting_raw_output_exposure_mode
```

These conditions determine whether the camera records to internal media while
an external RAW-compatible device is connected.

## 3. RAW Output Formats

The format model contains separate QFHD and DCI/UHD-size RAW paths:

```text
SETTING_RAW_OUTPUT_FORMAT_SETTING_SELECT_CODEC_RE_THROWING_RAW_OUTPUT_FORMAT_3840x2160
SETTING_RAW_OUTPUT_FORMAT_SETTING_SELECT_CODEC_RE_THROWING_RAW_OUTPUT_FORMAT_4096x2160
SETTING_RAW_OUTPUT_FORMAT_SETTING_SELECT_CODEC_RE_THROWING_RAW_OUTPUT_FORMAT_4096x2160_SELECT_CODEC_RAW
SETTING_RAW_OUTPUT_FORMAT_SETTING_SELECT_CODEC_RE_THROWING_RAW_OUTPUT_FORMAT_4096x2160_SELECT_CODEC_RAW_XAVC_I
```

The application also contains explicit video-format values:

```text
VIDEO_FORMAT_4096x2160P
VIDEO_FORMAT_3840x2160P
RAW_OUT
```

The presence of both 3840x2160 and 4096x2160 RAW formats is significant. It
indicates that external RAW output is integrated with the same resolution model
used by DCI 4K and UHD 4K, rather than being a generic unformatted sensor dump.

## 4. Frame-Rate Restrictions

RAW frame-rate restrictions have an explicit enum and function family:

```text
FUNC_raw_output_framerate_restriction_notset_for_haita
FUNC_raw_output_framerate_restriction_60p_for_haita
FUNC_raw_output_framerate_restriction_50p_for_haita
FUNC_raw_output_framerate_restriction_30p_for_haita
FUNC_raw_output_framerate_restriction_25p_for_haita
FUNC_raw_output_framerate_restriction_24p_for_haita
FUNC_raw_output_framerate_restriction_24_00p_for_haita
```

The matching values include RAW output, external RAW-device connection, and
movie exposure-mode conditions:

```text
RAW_FRAMERATE_60P_RAW_OUTPUT_RAW_DEVICE_CONNECTED
RAW_FRAMERATE_50P_RAW_OUTPUT_RAW_DEVICE_CONNECTED
RAW_FRAMERATE_30P_RAW_OUTPUT_RAW_DEVICE_CONNECTED
RAW_FRAMERATE_25P_RAW_OUTPUT_RAW_DEVICE_CONNECTED
RAW_FRAMERATE_24P_RAW_OUTPUT_RAW_DEVICE_CONNECTED
RAW_FRAMERATE_24_00P_RAW_OUTPUT_RAW_DEVICE_CONNECTED
```

This shows that RAW frame rate is evaluated together with connection state and
shooting mode. A frame-rate value alone is not sufficient to activate the path.

## 5. Model and Hardware Gates

The RAW path is tied to the same product-capability parameters used by other
restricted video functions:

```text
PRM_FEATURE_MANAGER_imager_model
PRM_FEATURE_MANAGER_product_concept
PRM_FEATURE_MANAGER_system_architecture
PRM_HAITA_setting_raw_output_4k_camera_control_imager_model
PRM_HAITA_setting_raw_output_connect_with_raw_compatible_device_exposure_mode_imager_model
PRM_HAITA_output_4k_compatible_device_setting_rec_media_during_hdmi_output_exposure_mode
```

The application also contains HDMI exclusion parameters:

```text
PRM_hdmi_output_format_frame_rate_for_exclusion
PRM_hdmi_output_format_raw_for_exclusion
PRM_hdmi_output_format_resolution_for_exclusion
PRM_hdmi_connect_state_connect_with_raw_compatible_device
```

This suggests that the firmware can reject RAW output based on the imager model,
external device state, output resolution, output frame rate, and whether an
internal recording mode is active.

The 4K RAW camera-control condition has a specific imager-model value:

```text
IMAGER_MODEL_IMX710
```

The related HAITA rules also require a RAW-compatible-device state and movie
exposure mode for the RAW-output menu path. The static application data does
not yet establish which imager-model enum ILCE-7CM2 reports.

The feature-manager enum table contains these imager-model values:

```text
IMAGER_MODEL_IMX710
IMAGER_MODEL_IMX451
IMAGER_MODEL_IMX223
IMAGER_MODEL_IMX510
IMAGER_MODEL_IMX684
IMAGER_MODEL_IMX810
IMAGER_MODEL_IMX610
IMAGER_MODEL_IMX910
```

The RAW 4K camera-control rule names only `IMX710` as its explicit supported
imager-model branch. The same feature-manager table defines product concepts
for `VLOGCAM`, `CINEMA_LINE`, and `OTHER`, as well as system architectures
`IPSX`, `ASTRA`, and `ARGO`.

No literal `ILCE-7CM2` to imager-model mapping was found in the application
string or relocation data. The current evidence indicates that the actual
imager-model value is initialized through a runtime model or hardware query,
rather than being stored as an ordinary user setting.

## 6. CP-Side Evidence

The CP image contains concrete RAW-output processing symbols and diagnostics:

```text
SendVDF_SetRawMode
SendVDF_SetRawOut
SetRawOutputFrameOffset
ConvertRawOutBit
SyncRawOut.cpp
RawPin
```

The CP image also reports RAW output errors and unsupported paths, including:

```text
CamCore: port(%d) typeof(rawOut) must be RdcImage.
FopdRcraw: FOPD_RATE_8PPC is not support
DualRec RawOut with L0 Memout is not implemented.
Error: ConvertRawOutbit!
```

This is stronger evidence than application-only strings. The CP side contains a
real RAW-output data path, frame-buffer handling, bit conversion, and explicit
unsupported-path checks.

## 7. What This Does Not Prove

The firmware is shared across several Sony product families. Therefore, the
following cannot be concluded from the shared code alone:

1. The A7C II exposes HDMI RAW output.
2. The A7C II sensor can provide every 3840x2160 or 4096x2160 RAW mode.
3. The HDMI hardware supports every listed output resolution or bit depth.
4. The external RAW-compatible-device handshake is enabled for this product.
5. A single application gate can activate the feature.

The CP RAW path may be present for higher-end bodies while the A7C II product
capability model returns an unsupported state.

## 8. Assessment

HDMI RAW output is a stronger research target than an ordinary hidden menu item.
The firmware contains all of the following layers:

```text
Application menu and parameter model
External RAW-device connection state
HDMI output exclusions
RAW frame-rate restriction logic
Imager/product/system capability gates
CP RAW mode and output commands
RAW buffer and bit-conversion code
```

The most useful next question is not whether a RAW menu string exists. It is
whether the ILCE-7CM2 capability branch returns an unavailable state or an
unsupported state, and which runtime model value produces that result. The
static evidence currently reaches the IMX710-only gate but cannot assign the
ILCE-7CM2 to one of the eight imager-model enums.

## 9. Next Static-Analysis Targets

```text
Initialization of PRM_setting_raw_output
Initialization of PRM_setting_raw_output_connect_with_raw_compatible_device
The imager-model branch for PRM_HAITA_setting_raw_output_4k_camera_control
The runtime model/hardware query that supplies PRM_FEATURE_MANAGER_imager_model
The consumers of PRM_raw_output_framerate_restriction
The CP call path from SetRawMode to SetRawOut
The output-format exclusion table for HDMI RAW
```

Only after those branches are understood would it be meaningful to classify HDMI
RAW output as a possible software restriction or a hardware/product limitation.

## 10. Version Scope

```text
Model: Sony ILCE-7CM2
Firmware: 2.01
```

Do not apply offsets, enum values, or conclusions from this report to another
model or firmware version.
