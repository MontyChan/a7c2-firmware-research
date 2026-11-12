# Sony A7C II 2.01 Firmware: DCI 4K Research

## 1. Scope

This report examines the DCI 4K 24p path in Sony ILCE-7CM2 firmware 2.01. The
focus is the firmware's video model, capability checks, license states, and
recording transition logic.

The analyzed objects are:

```text
/usr/lib/appFw.so
/cp/cpapp-b.bin
```

`appFw.so` is an AArch64 ELF64 dynamic program. `cpapp-b.bin` is a raw CP-side
program image. The conclusions below concern firmware structure and program
logic only.

## 2. DCI 4K

DCI 4K is the digital-cinema format at 4096x2160, as opposed to UHD 4K at
3840x2160. Both formats use the same vertical resolution, but DCI 4K is wider
and is approximately 17:9.

24p means 24 progressive frames per second.

In this report, DCI 4K 24p means the firmware path for:

```text
4096x2160
XAVC S-I
24p / 24.00p
```

## 3. DCI 4K Program Structure

### 3.1 Separate resolution paths

The application contains independent 3840x2160 and 4096x2160 paths, including:

```text
VIDEO_FORMAT_3840x2160P
VIDEO_FORMAT_4096x2160P
AVC_3840_2160_*
AVC_4096_2160_*
```

4096x2160 also appears in HDMI, SDI, and RAW output tables:

```text
OUTPUT_FORMAT_SDI_4096x2160P_HDMI_4096x2160P
OUTPUT_FORMAT_SDI_4096x2160P_HDMI_1920x1080P
RAW_OUTPUT_FORMAT_4096x2160
```

DCI 4K is therefore represented as an independent format in Sony's shared
video framework. It is not just a renamed UHD format.

### 3.2 Dedicated recording parameters

The application contains a complete XAVC S-I DCI 4K parameter family:

```text
setting_movie_rec_frame_rate_xavc_s_i_dci_4k
setting_movie_record_setting_xavc_s_i_dci_4k_60p
setting_movie_record_setting_xavc_s_i_dci_4k_50p
setting_movie_record_setting_xavc_s_i_dci_4k_30p
setting_movie_record_setting_xavc_s_i_dci_4k_25p
setting_movie_record_setting_xavc_s_i_dci_4k_24p
setting_movie_record_setting_xavc_s_i_dci_4k_24_00p
```

The same family is represented in the movie, S&Q, and time-lapse models.

The DCI 4K 24p record-setting enum includes:

```text
240 Mbps, 4:2:2, 10-bit
```

The firmware defines separate record settings and invalid states for DCI 4K
60p, 50p, 30p, 25p, 24p, and 24.00p. These entries are referenced by the
parameter model and ELF relocation tables; they are not isolated display text.

### 3.3 Recording interfaces

The application imports and calls video interfaces including:

```text
SetMovieRecParam
GetMovieProperties
GetMovieRemain
PID_SET_MOVIE_FORMAT
PID_SET_MOVIE_COLOR_SPACE
```

The DCI parameters therefore reach the normal movie-recording parameter path.
Static analysis alone cannot establish that the ILCE-7CM2 hardware accepts an
actual 4096x2160 recording request.

## 4. Capability and License Gates

DCI 4K 24p has a dedicated capability parameter:

```text
PRM_license_type_dci4k24p_available
```

The parameter has three states:

```text
LICENSE_TYPE_DCI4K24P_AVAILABLE
LICENSE_TYPE_DCI4K24P_NOT_AVAILABLE
LICENSE_TYPE_DCI4K24P_NOT_SUPPORT
```

The states distinguish three cases:

| State | Meaning |
| --- | --- |
| `AVAILABLE` | The current product conditions allow the feature. |
| `NOT_AVAILABLE` | The feature exists, but a license or condition is missing. |
| `NOT_SUPPORT` | The current product or hardware does not support it. |

This is the most important finding. Sony separates a disabled capability from
a capability that the product does not support. They must not be treated as a
single software flag.

Related model parameters include:

```text
PRM_license_state
PRM_license_type_4k120p_available
PRM_FEATURE_MANAGER_product_concept
PRM_FEATURE_MANAGER_imager_model
PRM_FEATURE_MANAGER_camera_parameters
```

This suggests that availability is calculated from the Feature Manager, product
concept, imaging model, and license state rather than from an ordinary menu
setting.

The BKID model contains separate entries for the generic file format, DCI 4K
frame rate, and DCI 4K 24p record-setting families. The firmware also defines
ten application license slots (`BKID_APP_LICENSE_TYPE0` through
`BKID_APP_LICENSE_TYPE9`) and ten corresponding expired-license status slots.
This confirms that license data has a persistent representation in the
application model. It does not identify which slot, if any, carries the DCI 4K
24p entitlement, or prove that an entitlement can be changed without
Sony-signed license data.

## 5. 24p Transition and Reboot Logic

DCI 4K 24p has dedicated transition states:

```text
REC_FRAME_RATE_CROSS_24_00P
reboot_for_dci4k_cross_24_00p
is_prohibited_infra_api_by_cross_24_00p
execute_mode_change_for_dci4k_cross_24_00p
execute_mode_change_during_power_off_for_dci4k_cross_24_00p
```

Additional initialization and reboot factors include:

```text
init_dci4k_settings
init_dci4k_settings_mr
reboot_for_dci4k_activation_factor
movie_rec_frame_rate_for_dci4k_reboot
sq_rec_frame_rate_for_dci4k_reboot
tl_rec_frame_rate_for_dci4k_reboot
file_format_for_dci4k_reboot
```

The path can therefore involve:

- Recording-format reinitialization
- 24p and 24.00p transition handling
- Temporary blocking of lower-level APIs
- Video-path restart
- Synchronization across movie, S&Q, and time-lapse state

Removing only a menu gate would not be enough to establish a usable recording
mode.

## 6. CP-Side Evidence

`cpapp-b.bin` is a raw CP image without an ELF symbol table. It does not contain
the complete DCI parameter names as plain ASCII, but its status model contains:

```text
OFF_BY_DCI_4K24P
OFF_BY_LICENCE
```

This shows that the CP application recognizes DCI 4K 24p and license-related
disable states. The absence of complete names does not prove that CP is absent
from the DCI decision; CP logic may be represented by numeric states, tables,
or code constants.

## 7. Conclusion

For firmware 2.01, the following points are confirmed:

1. The shared video framework contains an independent 4096x2160 DCI 4K path.
2. XAVC S-I DCI 4K 24p has its own frame-rate, record-setting, and state model.
3. The 240 Mbps 4:2:2 10-bit DCI 4K 24p record setting is present in the model.
4. The application defines a three-state DCI capability/license check.
5. DCI 4K 24p has dedicated transition, 24.00p, and reboot handling.
6. The CP application model contains DCI 4K and license-related disable states.

The following points remain unconfirmed:

1. Whether the ILCE-7CM2 runtime result is `NOT_AVAILABLE` or `NOT_SUPPORT`.
2. Whether the A7C II sensor, encoder, and storage path can sustain 4096x2160.
3. Whether DCI 4K depends on signed license data or product capability data.
4. Whether one replaceable program gate is sufficient to expose the feature.

DCI 4K 24p is a real firmware feature candidate, but it cannot yet be called a
software-hidden A7C II capability.

## 8. Further Research

The next static-analysis targets are:

```text
Initialization of license_type_dci4k24p_available
The source of PRM_FEATURE_MANAGER_product_concept
The ILCE-7CM2 branch for PRM_FEATURE_MANAGER_imager_model
The AVAILABLE / NOT_AVAILABLE / NOT_SUPPORT decision branch
The CP call sites for OFF_BY_DCI_4K24P
```

If the A7C II path resolves to `NOT_AVAILABLE` and the controlling license or
product condition can be identified, DCI 4K 24p remains a viable research
target. If it resolves to `NOT_SUPPORT`, the investigation must move to sensor
and encoder capability; changing an application gate would not be meaningful.

## 9. Version Scope

```text
Model: Sony ILCE-7CM2
Firmware: 2.01
```

Do not apply offsets, enum values, or conclusions from this report to another
model or firmware version.
