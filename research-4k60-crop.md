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

The CP image contains diagnostics/control labels for:

```text
SetAPSCMode
CheckSetAPSCMode
SetImageSensorBarrier
ImageSensorReadoutMode
```

These CP strings show that crop mode and sensor readout are real camera-level
controls. They are not exported appFw symbols, and their presence alone does
not show which command is issued for A7C II 4K60 or whether full-width readout
at 60 fps is supported.

The application imports and calls the normal movie-parameter interface
`SetMovieRecParam`. No separate APSC-mode setter is exported by appFw. The
4K60 application path therefore reaches a compound movie-parameter operation;
the exact CP crop/readout command selected downstream has not yet been
reconstructed.

### Call-site findings from the 2026-11-13 capture

The retained read-only capture is `a7c2-service-readonly/20261113-075519`.
Its inventory identifies ILCE-7CM2 and firmware assumption 2.01; `appFw.so`
is AArch64 ELF64 ET_DYN. In this image the import is the mangled C++ symbol
`mpr::SetMovieRecParam(mpr::movieRecParam const&)`, resolved through the PLT
entry at `0x16604b0`. There is one direct appFw call site at `0x356afc8`.

At that site, the caller copies three 8-byte words from a candidate record
into a stack object at `x29 + 0x90`, passes its address in `x0`, then calls
`SetMovieRecParam`. The object is therefore 24 bytes at this call boundary,
but its fields have not been identified. The caller iterates candidate records
and invokes helper predicates before selecting the record. The helper call at
`0x356af98` is followed by the 24-byte copy and the `SetMovieRecParam` call;
the helper is reached through the imported PLT entry at `0x165d4d0`. This
establishes a conditional path to a movie-parameter submission, not that any
particular HAITA result changes the frame area. No frame-size, sensor-rate,
codec, or readout field offset has been proven.

The three HAITA names in scope are present in the string table. Relocation
records associate the FF and APS-C restriction names with the adjacent
relocation-backed name table at `0x57ed640` and `0x57ed648`, and the APS-C frame
size parameter name with the parallel table at `0x57ee820` (these are ELF
virtual addresses, not file offsets). This confirms
relocation-backed table entries, but the model-rule records, parameter IDs,
and their exact 50p/60p values have not yet been recovered. Do not interpret
the nearby relocation addends as those model-specific values without decoding
the table format.

Further inspection shows why static string matching cannot recover the values
by itself. The appFw data contains repeated registry records with the shape
`0x403`, a relocation-backed address in the BSS range, and a pointer to a
second table. The entries containing the HAITA names are associated with
relocation targets whose addends point into BSS, including addresses around
`0x883aa18` and `0x883ac54`, outside the file-backed image. This establishes
links to runtime storage, but does not identify the object layout or prove
that it contains computed HAITA results rather than parameter descriptors or
defaults. The current model-specific HAITA values remain unknown; the next
step is to identify the runtime getter and object layout, not to interpret
relocation addends as static 50p/60p settings.

In `cpapp-b.bin`, the CP text contains `FW: SetAPSCMode[%d]` at file offset
`0x250630`, `CheckSetAPSCMode` at `0x25a558`, and
`CheckSetImageSensorBarrier` at `0x25c2e0` (the prior substring search for
`SetImageSensorBarrier` began five bytes into that label). The string
`ImageSensorReadoutMode` occurs inside a firmware diagnostic format at
`0xec0c35`. These are part of CP firmware logging/parameter-check text. In
particular,
`CheckSetAPSCMode` appears next to the diagnostic format
`ParamCheckErr@[e_apsc_mode] cur:%d req:%d`, and
`CheckSetImageSensorBarrier` appears in the same family of `CheckSet...`
labels. `ImageSensorReadoutMode` appears in a firmware diagnostic format that
also prints a process-discrimination code and pixel dimensions. This makes the
CP path strong evidence for a parameter check named `e_apsc_mode` and for
readout diagnostics. The `SetAPSCMode` label appears in an FW command-style
message, but its dispatch/handler and whether it is sent by the 4K60 path have
not been traced. There is no established caller link from the appFw movie
parameter request to these CP operations.

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

The firmware contains separate full-frame and APS-C policy branches for 4K
recording. Their existence shows that the application models these cases, but
does not by itself establish that the crop is caused by a sensor limit rather
than a model-specific policy.

The physical sensor/readout capability for ILCE-7CM2 at 50p/60p remains unknown.
No sensor capability response, CP mode transition, or model-specific runtime
HAITA value has been captured in the evidence analyzed here.

The firmware contains a full-frame branch in its shared model, but that branch
may be intended for other Sony bodies. It should not be treated as evidence that
the A7C II can record full-frame 4K60 after a menu or parameter change.

The static evidence shows separate policy branches and a conditional compound
movie-parameter submission. It also shows that HAITA name-registry entries
link to runtime storage, but does not establish the contents of that storage.
It does not yet establish whether the HAITA evaluator only affects setting
validity, modifies the submitted `movieRecParam`, or triggers a downstream CP
readout change. Neither a product/readout limitation nor a software exception
has been demonstrated. The CP check and diagnostic labels are not by themselves
call-chain evidence.

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
A7C II's 4K60 crop. Whether the restriction is an application model rule, a
downstream CP/sensor constraint, or both remains unresolved.

## 8. What Would Change This Assessment

The next useful evidence is further offline analysis of the retained capture
`a7c2-service-readonly/20261113-075519`, followed by:

1. Decode the relocation-backed HAITA/model references and model tables to
   recover parameter IDs, record layout, and exact full-frame/APS-C values for
   50p/60p.
2. Trace the rule evaluator and all relevant consumers to determine whether a
   result affects only setting validity or the compound movie request.
3. Recover the `mpr::movieRecParam` field layout, including image frame size,
   sensor rate, codec, and any crop/readout selector.
4. Disassemble the CP string xrefs and command handlers, then test whether a
   path from this movie request reaches any APSC/readout operation.
5. Compare 30p and 50p/60p independently for XAVC HS, XAVC S, and XAVC S-I.
   Only consider a read-only runtime probe after its getter, ABI, storage, and
   lifetime are established.

## 9. Read-Only Probe Design

The next probe must observe the existing application state; it must not set a
movie parameter, change a sensor mode, call a CP setter, or write AP/CP data.
It is not yet safe to deploy a native probe because the HAITA objects and
getter ABI have not been identified. The following is the design to use after
those prerequisites are satisfied.

### Phase A: Static ABI qualification

1. Identify the HAITA getter or evaluator entry from appFw call sites, not from
   the parameter name alone. Record its exact AArch64 prototype: register
   arguments, return type, hidden object/context argument, and whether it
   returns a value or writes an output object.
2. Identify the owner object for the three HAITA entries and prove its
   lifetime. The BSS-related addresses seen in the file are relocation
   addends, not addresses that a probe may dereference directly.
3. Determine the value representation and validity state for each result:
   integer/enum, boolean, tri-state, error code, or a parameter wrapper. The
   probe must read the result through the same getter or accessor used by the
   application.
4. Identify the appFw module load base at runtime and translate all addresses
   through `module_base + ELF virtual address`. No hard-coded absolute camera
   address is permitted.
5. Prove the read range. The probe may read only the getter's returned scalar
   or a documented output object, plus immutable context needed to label the
   sample. It must not dump arbitrary BSS, heap, stack, CP shared memory, or
   sensor registers.

The qualification phase is complete only when an offline call graph shows:

```text
known appFw caller
  -> known HAITA getter/evaluator
  -> known object/output storage
  -> scalar or enum result
```

If any link is unresolved, stop and continue static analysis.

### Phase B: Observation-only sampling

The native part should be a temporary in-process routine executed in the same
application context as the verified getter, preferably from an already safe
service/debug callback. It should:

1. Resolve the appFw load base and verify the expected ELF build identity using
   the captured SHA-256
   `eaad807602ba2e9a97675b1d28624a7dd6096a231b900597b1670614c49a1091`
   before doing anything else.
2. Resolve the getter and owner object using verified relocations or symbols;
   do not use a guessed address.
3. Read, without writing, the following values in one sample:

   ```text
   imager_frame_size
   imager_frame_rate
   imager_frame_rate_in_file_format_4k
   model_diff_ff_restriction_imager_frame_rate_in_file_format_4k
   model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
   ```

4. Also read the current movie-setting selectors needed to label the sample:
   codec family, 4K record frame rate, exposure/recording mode, and the
   current image-frame-size setting. These must be obtained through verified
   read accessors, not by guessing offsets.
5. Copy the result into a fixed local record containing a magic value, build
   hash prefix, module base, getter address, value IDs, values, and status
   codes. Keep it in a preallocated probe buffer and return it only through a
   separately verified diagnostic read channel. Do not write a device file,
   allocate dynamically, persist settings, or send a camera command from the
   probe. The current Service USB inspector has no appFw process-memory or
   probe-result channel; adding or enabling one requires its own protocol and
   safety review before deployment.
6. Execute once per state, then return immediately. The first states should be
   idle/movie mode with the current 4K30 setting, followed by 4K50/60 states
   only if the camera has already selected them through normal user operation.
   The probe must not select those settings itself.

The sample matrix should be collected independently for XAVC HS, XAVC S, and
XAVC S-I, with 4K30 and 4K50/60 labeled separately. A single result from one
codec must not be generalized to the other two.

### Safety and recovery boundary

The probe must have no stores to AP, CP, settings, sensor-control, or movie
parameter addresses. Before invocation, it must verify that the current task
is the appFw process and that the getter is callable in the current context.
If the getter requires a lock, message loop, or recording-state context that
cannot be proven, the probe must report `unsupported_context` and return.

The native routine must use a bounded stack record, a fixed instruction/time
budget, and a return guard. It must not hook `SetMovieRecParam`, patch code,
change function pointers, disable checks, or continue after an exception. A
watchdog or process restart is the recovery boundary for a crash; there is no
claim that a temporary native probe is crash-free. The camera must be left to
restart normally, and the probe output must be treated as invalid if the
process exits or the build identity differs.

### Interpretation rules

The probe can distinguish the application gate only if the sampled values are
paired with the actual request passed to `SetMovieRecParam` or with an
equivalent verified accessor. The outcomes are:

| Observed state | Interpretation |
| --- | --- |
| HAITA rejects Full before the movie request | Application/model gate is sufficient to explain the crop path. |
| HAITA allows Full and request contains APS-C | The appFw candidate selection changes or substitutes the frame size. |
| Request contains Full, CP/readout result is APS-C or rejects | Crop is downstream of appFw. |
| Request and CP both contain Full, sensor reports no Full mode | Full-width 50p/60p is not available through this software path. |
| All layers report Full but output remains cropped | Inspect sensor/encoder output dimensions and hidden downstream state; do not call this a successful unlock. |

No write experiment should be proposed from a probe result alone. A valid
read-only result establishes the mechanism; it does not establish that a
modified request is safe or that the sensor can sustain full-width 50p/60p.

The runtime values of interest are:

```text
imager_frame_size
imager_frame_rate
imager_frame_rate_in_file_format_4k
model_diff_ff_restriction_imager_frame_rate_in_file_format_4k
model_diff_apsc_restriction_imager_frame_rate_in_file_format_4k
```

The current Service USB inspector does not expose these computed HAITA values.
The new program dump is retained locally and ignored by Git. Until the
evaluator, parameter layout, and CP command path are traced, no program or
setting change should be treated as a safe crop unlock.

## 10. Version Scope

```text
Model: Sony ILCE-7CM2
Firmware: 2.01
```

Do not apply offsets, enum values, or conclusions from this report to another
model or firmware version.
